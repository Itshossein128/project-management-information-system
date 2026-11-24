# Stage 1.2 QA Verification Report — Package B04: Filters, Complete Result Set, and Totals

- **Package ID:** B04
- **Requirement Title:** Filters, complete result set, and totals (فیلترها و جمع کل queryset)
- **Primary Acceptance Criteria:** API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics.
- **Delivery Phase:** A.1 (Daily Reports & Exports / گزارش روزانه و خروجی‌ها)
- **Verification Date:** 2026-11-21
- **Domain Scope:**
  - Direct ownership: E11 (Comprehensive Activity Log / FILE 1 with complete filtered result set), E12 (Daily Reports list filters and deep-linkable URLs), E13 (Multi-dimensional activity log filtering & URL preservation), E14 (Whole-queryset totals by measurement unit, independent of pagination)
  - Shared ownership: E15 (Version policy: current approved vs historical/cancelled), D07 (Headcount vs man-days labeling), D05 (Unset/not-measured vs zero semantics)
- **QA Verdict:** **qa_failed** (Defects and architectural gaps present)

---

## 1. End-User Persona Assessment

### 1.1. Project Manager / Supervisor Persona (مدیر پروژه / دستگاه نظارت)
- **Pagination Boundary Totals Distortion (Defect DEF-B04-01 / E14):**
  - When reviewing the Activity Log (`/projects/:projectId/activity-log`) with active filters matching >50 records (e.g., 51 records):
    - Page 1 renders a summary metric card showing 50 headcount.
    - Navigating to Page 2 causes the summary card to drop to 1 headcount.
    - End-user impact: The executive summary bar does not show the whole-queryset aggregate; it only aggregates the active 50-row page slice. This leads to severe reporting inaccuracies when assessing site resources.
- **Web UI Summary vs. FILE 1 Excel Discrepancy (Defect DEF-B04-02 / E11, E14):**
  - Clicking "خروجی اکسل دیتابیس جامع فعالیت‌ها (FILE 1)" triggers `ActivityLogExcelView`, which streams all 51 rows.
  - The Excel totals reflect the full 51 rows, whereas the UI summary cards show 50 rows (on page 1) or 1 row (on page 2). Stakeholders comparing screen metrics with exported reports observe mismatched figures.

### 1.2. Technical Office / Planning Engineer Persona (سرپرست دفتر فنی و برنامه‌ریزی)
- **Missing Standard Dimensional Filters on Daily Reports List (Defect DEF-B04-03 / E12, FR016):**
  - On `/projects/:projectId/daily-reports`, the user requires filtering reports by discipline, contractor, or block.
  - Currently, both UI (`daily-reports-list.tsx`) and backend API (`DailyReportViewSet.get_queryset`) only handle `date_from`, `date_to`, and `status`. Discipline, contractor, and block filters are completely absent from the daily reports listing.
- **URL Parameter Restoration & Unset Semantics (Defect DEF-B04-04 / E13, D05):**
  - Filter state serialization in `project-activity-log.tsx` sends parameters, but when fields are unset/not measured, client-side zero substitution (`Number(r.quantity) || 0`) collapses unmeasured entries into zero quantities rather than distinguishing `null`/unset from valid 0.0 values.

### 1.3. QA & Data Auditor Persona (ممیز کنترل کیفیت و داده)
- **Misleading "Man-Days" Label for Raw Headcount Sum (Defect DEF-B04-05 / D07):**
  - The UI summary card displays `مجموع نفرات (نفر-روز):`.
  - In reality, this is a plain algebraic sum of the `headcount` column from activity rows, not true verified man-days (which require working hours, shifts, and distinct worker identity reconciliation). Decision D07 forbids labeling raw headcount row sums as man-days without qualification.

---

## 2. Technical Inspection & Evidence

### 2.1. Frontend Code Inspection (`apps/web`)
1. **`apps/web/src/app/routes/project-activity-log.tsx` (Lines 126-141):**
   ```typescript
   const rows = data?.results ?? [];
   const totalPages = data ? Math.ceil(data.count / 50) : 1;

   const totalHeadcount = useMemo(() => {
     return rows.reduce((acc, r) => acc + (Number(r.headcount) || 0), 0);
   }, [rows]);

   const quantitiesByUnit = useMemo(() => {
     const map: Record<string, number> = {};
     for (const r of rows) {
       if (r.unit && r.quantity != null && !isNaN(Number(r.quantity))) {
         map[r.unit] = (map[r.unit] || 0) + Number(r.quantity);
       }
     }
     return map;
   }, [rows]);
   ```
   - **Root Cause:** Aggregations are calculated entirely client-side using `data.results` (the single page of 50 items).

2. **`apps/web/src/app/routes/daily-reports-list.tsx`:**
   - Lacks UI controls or query parameter synchronization for `discipline`, `block`, or `subcontractor`.

### 2.2. Backend API Code Inspection (`apps/api`)
1. **`apps/api/core/field_reports/report_views.py` (`ActivityLogView`):**
   - Implements standard `ReportPagination` returning `{ count, next, previous, results }`.
   - Does not compute or return whole-queryset totals (`totals`, `quantities_by_unit`, or `total_headcount`) across `qs`.

2. **Empirical Audit Evidence (`output/a1-requirements-2026-11-18/evidence/pagination-probe.json`):**
   - Verified probe demonstrates:
     - `count`: 51
     - `page_rows`: 50
     - `page_headcount_sum`: 50
     - `whole_filter_expected_sum`: 51
     - Client and server responses lack independent whole-queryset totals.

---

## 3. Defects Register

| Defect ID | Title | Component | Severity | Description | Status |
|:---|:---|:---|:---|:---|:---|
| **DEF-B04-01** | Client-side aggregation on page slice instead of whole queryset | `project-activity-log.tsx` | High | Totals shift on pagination navigation; Page 2 shows only its subset. | Open |
| **DEF-B04-02** | Missing `aggregates`/`totals` payload in `ActivityLogView` API | `report_views.py` | High | DRF response lacks whole-queryset totals metadata across filtered queryset. | Open |
| **DEF-B04-03** | Missing discipline, block, and contractor filters on Daily Reports list | `daily-reports-list.tsx` / `daily_report_views.py` | Medium | Missing FR016 multidimensional filtering for daily reports listing. | Open |
| **DEF-B04-04** | Collapsing unset quantities into zero | `project-activity-log.tsx` | Medium | Unset/unmeasured quantities treated as numeric zero. | Open |
| **DEF-B04-05** | Erroneous "man-days" label for raw headcount sum | `project-activity-log.tsx` | Low | Violates Decision D07 naming requirement. | Open |

---

## 4. Remediation Requirements for Stage 5

To achieve `qa_passed` for B04:
1. Update `ActivityLogView` in `apps/api/core/field_reports/report_views.py` to annotate/aggregate the filtered queryset (`qs.aggregate(...)`) and inject whole-queryset totals (headcount and volume by unit) into the paginated response.
2. Update `project-activity-log.tsx` to read whole-queryset summary metrics directly from the API response rather than calculating them over `data.results`.
3. Add discipline, contractor, and block filters to `DailyReportViewSet.get_queryset` and expose corresponding filter controls in `daily-reports-list.tsx`.
4. Correct summary card labeling to distinguish headcount row summation from certified man-days.

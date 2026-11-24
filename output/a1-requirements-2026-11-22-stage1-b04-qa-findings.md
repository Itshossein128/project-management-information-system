# Stage 1.2 QA Verification Report — Package B04: Filters, Complete Result Set, and Totals

- **Package ID:** B04
- **Requirement Title:** Filters, complete result set, and totals (فیلترها و جمع کل queryset)
- **Primary Acceptance Criteria:** API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics.
- **Delivery Phase:** A.1 (Daily Reports & Exports / گزارش روزانه و خروجی‌ها)
- **Verification Date:** 2026-11-22
- **Domain Scope:**
  - Direct ownership: E11 (Comprehensive Activity Log / FILE 1 with complete filtered result set), E12 (Daily Reports list filters and deep-linkable URLs), E13 (Multi-dimensional activity log filtering & URL preservation), E14 (Whole-queryset totals by measurement unit, independent of pagination)
  - Shared ownership: E15 (Version policy: current approved vs historical/cancelled), D07 (Headcount vs man-days labeling), D05 (Unset/not-measured vs zero semantics)
- **QA Verdict:** **qa_passed** (All historical defects resolved, acceptance criteria met)

---

## 1. Executive Summary & Status

Requirement **B04** establishes comprehensive filtering, unified full-result aggregation, and reference-grade Excel/UI reconciliation across the Daily Reports list (`/daily-reports`) and Project Activity Master Log (`/projects/:id/activity-log`).

Following the complete implementation and end-to-end verification documented in `specs/060-a1-b04-filters-totals/` and `output/a1-b04-stage5-qa-verification-2026-11-22.md`, all 5 historical defects (`DEF-B04-01` through `DEF-B04-05`) have been verified as **RESOLVED**. Both frontend (`apps/web`) and backend (`apps/api`) maintain rigorous synchronization between UI filters, deep-linkable URL search params, whole-queryset server-side aggregates, and FILE 1 Excel export workbooks.

---

## 2. End-User Persona Verification

### 2.1. Project Manager / Supervisor Persona (مدیر پروژه / دستگاه نظارت)
- **Whole-Queryset Aggregation (Resolves DEF-B04-01 & DEF-B04-02):**
  - **Behavior:** On `/projects/:projectId/activity-log`, when an active filter matches 51 records with pagination set to 50 per page:
    - **Page 1 (rows 1–50):** The top summary card displays total headcount sum = 51, and per-unit measured totals (e.g., 45 m², 25 m³).
    - **Page 2 (row 51):** The summary card preserves total headcount sum = 51 and identical per-unit measured totals.
    - **Result:** Aggregates do not fluctuate across pagination boundaries. Server-side computation in `activity_log_aggregates` ensures the entire filtered queryset is summarized before pagination slicing.
- **FILE 1 Excel Export Parity (Resolves DEF-B04-02 & SC-002):**
  - Triggering the FILE 1 download from either Page 1 or Page 2 yields an identical 51-row workbook matching the server aggregates and including Excel formula `SUM(F2:F52)`.

### 2.2. Technical Office / Planning Engineer Persona (سرپرست دفتر فنی و برنامه‌ریزی)
- **Dimensional Filtering on Daily Reports List (Resolves DEF-B04-03 / E12):**
  - On `/projects/:projectId/daily-reports`, the filter bar exposes `discipline`, `contractor`, and `block` selectors alongside date range and status.
  - **Single-Row Matching & Split-Row Exclusion:** In accordance with ratified B01/B04 rules, a daily summary is included if and only if at least one eligible activity row satisfies *all* selected dimensional filters simultaneously. Split-row matches across disparate activity rows are strictly excluded.
- **Deep-Link State Restoration (SC-001):**
  - Query parameters (`discipline`, `contractor`, `block`, `date_from`, `date_to`, `page`) are bidirectional. Hard browser reloads, shared links, and Back/Forward navigation restore identical UI control states and result sets in both Persian (RTL) and English (LTR).

### 2.3. QA & Data Auditor Persona (ممیز کنترل کیفیت و داده)
- **Unset vs. Measured Zero Semantics (Resolves DEF-B04-04 / D05):**
  - Explicit measured zeros (`0.0`) are rendered as valid numeric quantities and contribute to measured counts.
  - Unset or not-measured values are rendered as null/dash markers and tracked under `unknown_count`, never collapsing into numeric zero or corrupting quantity sums.
- **Compliant Headcount Labeling (Resolves DEF-B04-05 / D07):**
  - Labeling strictly reflects "Sum of activity-row headcounts" / "مجموع نفرات ثبت‌شده در ردیف‌ها", avoiding misleading "man-days" or "unique worker" implications without shift and attendance reconciliation.
- **RBAC & Project Isolation:**
  - Cross-project and unauthorized accounts attempting to access filtered activity logs, option aliases, or FILE 1 exports receive HTTP 403 Forbidden with zero data leakage or cache-warming side channels.

---

## 3. Historical Defect Resolution Matrix

| Defect ID | Severity | Description | Resolution Status | Technical Implementation Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-B04-01** | High | Client-side aggregation on page slice instead of whole queryset | **Resolved** | UI binds directly to `listQuery.data.aggregates` in `apps/web/src/app/routes/project-activity-log.tsx`. |
| **DEF-B04-02** | High | Missing whole-queryset totals/aggregates payload in ActivityLogView API | **Resolved** | `activity_log_aggregates(qs)` in `apps/api/core/field_reports/services/activity_log.py` computes totals across full `qs`. |
| **DEF-B04-03** | Medium | Missing discipline, block, contractor filters on Daily Reports list | **Resolved** | Filters integrated in `daily-reports-list.tsx` and `DailyReportViewSet.get_queryset` with single-row match semantics. |
| **DEF-B04-04** | Medium | Collapsing unset/unmeasured quantities into numeric zero | **Resolved** | `MEASURED_QUANTITY` Q-filter separates measured amounts from unmeasured/unset records in DB queries. |
| **DEF-B04-05** | Low | Misleading man-days labeling for raw headcount row sum | **Resolved** | Localized strings updated in `apps/web/src/app/locales/{fa,en}/common.json` under `reportFilters.headcountSum`. |

---

## 4. Verification Evidence & Quality Gates

1. **Frontend Typecheck:**
   - Command: `pnpm --filter web typecheck`
   - Result: `react-router typegen && tsc` passed with **0 errors**.
2. **Backend Regression Test Suite:**
   - Test File: `apps/api/core/field_reports/tests/test_a1_b04_filters_totals.py`
   - Covers: Single-row match rule, split-row exclusion, foreign identity isolation, version policy (B02 current-approved), whole-selection totals reconciliation with FILE 1, and cache invalidation upon report correction/cancellation.
3. **Delivery Plan Registration:**
   - Status: Registered as `implemented` in `apps/web/src/app/data/delivery-plan.ts` under `A.1-B04`.

---

## 5. QA Verdict

- **Requirement Status:** `qa_passed`
- **Total Defects:** 0 open defects (5 resolved)
- **Summary:** Package B04 meets all functional, non-functional, bilingual, and security acceptance criteria for Phase A.1.

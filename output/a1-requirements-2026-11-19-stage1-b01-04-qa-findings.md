# Stage 1.2 QA Verification: Requirement B01-04 (Shifts, Durations, and Labor Metrics)

- **Requirement ID**: `B01-04`
- **Title**: Shifts, durations, and labor metrics
- **Phase**: Phase A.1 (`specs/057-a1-b01-data-contract`)
- **Evaluation Date**: 2026-11-19
- **Assigned Acceptance Criteria**:
  > Use worked shifts only with canonical IDs 1-3, actual durations, unknown missing durations, and distinct bilingual labor metrics.
- **Audited Specifications & Standards**:
  - `specs/057-a1-b01-data-contract/spec.md` (User Story 4, FR-011, FR-012, FR-013, SC-004, SC-005, C03, H04, D07, DEF-B01-02, DEF-B01-03)
  - `specs/057-a1-b01-data-contract/checklists/requirements.md`
- **Audited Codebase & Endpoints**:
  - Backend models: `apps/api/core/field_reports/models.py` (`DailyReport`, `ReportShift`, `ActivityRowShift`, `DailyReportLabor`, `BaseEquipmentEntry`)
  - Backend services & calculation rules: `apps/api/core/field_reports/services/man_hours.py`, `apps/api/core/field_reports/serializers.py`
  - Excel export templates: `apps/api/core/field_reports/shiraz_file4_excel.py`, `apps/api/core/field_reports/shiraz_file1_excel.py`
  - Frontend views & types: `apps/web/src/app/lib/api/daily-reports.ts`, `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx`, `apps/web/src/components/daily_reports/LaborTab.tsx`, `apps/web/src/app/routes/project-activity-log.tsx`, `apps/web/src/app/routes/project-labor-productivity.tsx`
  - Runtime services: `http://localhost:5173` and `http://localhost:8000` (connection refused; dev processes stopped)

---

## 1. End-User Persona & Workflow Evaluation

### 1.1 Resident Supervisor / Site Engineer Persona
- **Shift Structure & Canonical Identifiers (C03, FR-011)**:
  - *Expectation*: The daily report header lists ONLY shifts that actually worked on that calendar date (e.g. shifts 1 and 3 if shift 2 did not work), using identical canonical shift identifiers (`1`, `2`, `3`) across header, activity records, and date lookups. Invalid shift codes must be rejected.
  - *Observed Runtime Reality*:
    - Backend `DailyReport.shift` is defined as `day`, `night`, `full` (`ReportShift` enum) with a database unique constraint `['project', 'report_date', 'shift']`, permitting multiple reports per date if shifts differ.
    - Child activity rows use `shift_1`, `shift_2`, `shift_3` (`ActivityRowShift` enum).
    - Header and row models use conflicting enum schemas (`day/night/full` vs `shift_1/shift_2/shift_3`) rather than the canonical shift IDs `1`, `2`, and `3`.
    - No mechanism exists in `DailyReport` header to represent "only worked shifts 1 and 3".

### 1.2 Technical Office / Planning Engineer Persona
- **Actual Working Durations vs Default/Planned Hours (FR-012, DEF-B01-02)**:
  - *Expectation*: Person-hours must be calculated exclusively from the actual working duration recorded for each worked shift. If actual duration is missing, it must remain unknown/unrecorded without assuming planned or default hours, and static placeholder text ("ساعات کاری شیفت: ثبت نشده") must be eliminated.
  - *Observed Runtime Reality*:
    - In `apps/api/core/field_reports/shiraz_file4_excel.py` line 205, cell `G4` hardcodes static placeholder text: `ws['G4'] = 'ساعات کاری شیفت: ثبت نشده'`.
    - In `apps/api/core/field_reports/services/man_hours.py` and `serializers.py` lines 453-455 and 509-511, `compute_man_hours` falls back to `config.standard_shift_hours or Decimal('8')`. When actual duration is missing, it silently substitutes a default 8-hour planned duration rather than marking person-hours as unknown/unrecorded.
    - `DailyReport` does not have an actual shift duration field on the header or shift records.

### 1.3 QA Auditor & Cost Controller Persona
- **Bilingual Labor Metrics & Anti-Mislabeled Person-Days (FR-013, DEF-B01-03)**:
  - *Expectation*: The system must clearly distinguish headcount (persons), person-shifts, person-days, and person-hours in Persian and English. Simple row sums across activities or shifts without deduplicated worker attendance tracking MUST NEVER be labeled as unique persons or "person-days" (`نفرروز`).
  - *Observed Runtime Reality*:
    - In `apps/web/src/app/routes/project-activity-log.tsx` line 295, the summary bar displays:
      `<span className='text-muted-foreground'>مجموع نفرات (نفر-روز):</span> <span className='font-bold text-foreground'>{totalHeadcount}</span>`
      where `totalHeadcount` is a simple row sum (`rows.reduce((acc, r) => acc + (Number(r.headcount) || 0), 0)`). This directly violates FR-013 and Decision D07 by mislabeling an un-deduplicated activity row headcount sum as "نفر-روز".
    - In `apps/web/src/app/routes/project-labor-productivity.tsx` lines 128 and 133, table headers display `["عنوان", "ساعات", "نفر-روز"]` without attendance deduplication.
    - Neither the backend serializers nor frontend interfaces provide distinct bilingual definitions/labels differentiating `headcount`, `person-shifts` (`نفر-شیفت`), `person-days` (`نفر-روز`), and `person-hours` (`نفر-ساعت`).

---

## 2. Acceptance Criteria Verification Matrix

| Acceptance Item | Specification Rule | Code / Runtime Status | Verdict |
|:---|:---|:---|:---|
| **One logical daily report per project-date** | C03, FR-011: Exactly one logical daily report per project per calendar date. | `DailyReport` allows separate reports for `day` and `night` via `unique_current_daily_report_per_date_shift`. | **Failed** |
| **Header worked shifts only** | C03, FR-011: Report header lists ONLY shifts that actually worked. | Header has single scalar `shift` field (`ReportShift`), incapable of listing worked shift combinations (e.g. 1 & 3). | **Failed** |
| **Canonical shift IDs 1-3 everywhere** | C03, FR-011: Use exact canonical IDs `1`, `2`, `3` across header, activities, labor, and lookups. Reject invalid IDs. | Header uses `day/night/full`; activities use `shift_1/shift_2/shift_3`; labor rows use `shift_1_count/shift_2_count/shift_3_count`. Divergent enums without canonical 1-3 unification. | **Failed** |
| **Person-hours from actual duration only** | C03, FR-012: Person-hours derived exclusively from recorded actual shift duration; eliminate static placeholder text. | Excel exporter hardcodes `'ساعات کاری شیفت: ثبت نشده'`; `man_hours.py` defaults to 8-hour standard shift when duration is missing. | **Failed** |
| **Unknown missing duration semantics** | C03, FR-012: When shift duration is missing, treat duration and person-hours as unknown/unrecorded; do not assume default/planned hours. | System silently substitutes `standard_shift_hours` (default 8) instead of returning null/unknown. | **Failed** |
| **Distinct bilingual labor metrics** | FR-013, D07: Disallow labeling row sums as "نفرروز" without unique attendance proof; define distinct Persian/English labels. | Activity log UI explicitly labels simple headcount sum as `مجموع نفرات (نفر-روز)`; missing bilingual metric schema. | **Failed** |

---

## 3. Discovered Defects Register

1. **DEF-B01-04-GAP-01 (Backend Data Model / Schema Inconsistency)**:
   - *Description*: `DailyReport` uses `ReportShift` (`day`, `night`, `full`) while `DailyReportActivity` uses `ActivityRowShift` (`shift_1`, `shift_2`, `shift_3`), violating FR-011 canonical shift identifier rules (`1`, `2`, `3`). Furthermore, the database constraint allows separate reports for day and night on the same date rather than enforcing one logical daily report per project-date with a list of worked shifts.
   - *Component*: `apps/api/core/field_reports/models.py`
   - *Severity*: High

2. **DEF-B01-04-GAP-02 (Excel Export Static Placeholder & Hardcoded Hours)**:
   - *Description*: Official Excel exporter hardcodes `ws['G4'] = 'ساعات کاری شیفت: ثبت نشده'` instead of rendering recorded actual shift durations or proper unknown indicators, violating FR-012 (`DEF-B01-02`).
   - *Component*: `apps/api/core/field_reports/shiraz_file4_excel.py` (L205)
   - *Severity*: Medium

3. **DEF-B01-04-GAP-03 (Silent Coercion to 8-Hour Planned Shift)**:
   - *Description*: `compute_man_hours` and serializer logic silently fall back to `standard_shift_hours` or `Decimal('8')` when actual shift duration is absent, fabricating person-hours rather than preserving missing duration as unknown/unrecorded, violating FR-008 and FR-012.
   - *Component*: `apps/api/core/field_reports/services/man_hours.py` & `apps/api/core/field_reports/serializers.py`
   - *Severity*: High

4. **DEF-B01-04-GAP-04 (Semantic Mislabeling of Headcount Sum as Person-Days)**:
   - *Description*: `project-activity-log.tsx` labels raw summed activity headcount as `مجموع نفرات (نفر-روز)`, and `project-labor-productivity.tsx` uses `نفر-روز` headers, in direct violation of Decision D07 and FR-013 (`DEF-B01-03`).
   - *Component*: `apps/web/src/app/routes/project-activity-log.tsx` (L295), `apps/web/src/app/routes/project-labor-productivity.tsx` (L128, L133)
   - *Severity*: Medium

5. **DEF-B01-04-GAP-05 (Missing Bilingual Metric Taxonomy & Definitions)**:
   - *Description*: The software lacks an explicit bilingual taxonomy and API contracts distinguishing headcount (تعداد نفرات), person-shifts (نفر-شیفت), person-days (نفر-روز), and person-hours (نفر-ساعت).
   - *Component*: `apps/web/src/app/lib/api/daily-reports.ts`, `apps/api/core/field_reports/serializers.py`
   - *Severity*: Medium

---

## 4. Final QA Verdict & Status

Requirement `B01-04` is clearly ratified and specified in `specs/057-a1-b01-data-contract/spec.md` (User Story 4, FR-011–FR-013, C03), but the application implementation in `apps/api/core/` and `apps/web/src/` contains multiple open architectural, semantic, and calculation defects.

```json
{
  "requirementId": "B01-04",
  "title": "Shifts, durations, and labor metrics",
  "acceptanceCriteria": "Use worked shifts only with canonical IDs 1-3, actual durations, unknown missing durations, and distinct bilingual labor metrics.",
  "qaStatus": "qa_failed",
  "defects": [
    "DEF-B01-04-GAP-01: Backend DailyReport schema uses mismatched shift enums (day/night/full vs shift_1/2/3) and lacks one-report-per-date worked shift list with canonical IDs 1-3 (FR-011, C03)",
    "DEF-B01-04-GAP-02: Shiraz File 4 Excel export hardcodes static placeholder text 'ساعات کاری شیفت: ثبت نشده' in cell G4 (FR-012, DEF-B01-02)",
    "DEF-B01-04-GAP-03: Man-hours calculation silently defaults missing durations to 8 planned hours rather than treating missing durations as unknown (FR-008, FR-012)",
    "DEF-B01-04-GAP-04: Frontend activity log sums row headcounts and mislabels them as 'مجموع نفرات (نفر-روز)' without unique worker attendance deduplication (FR-013, D07, DEF-B01-03)",
    "DEF-B01-04-GAP-05: Missing explicit bilingual data contract definitions distinguishing headcount, person-shifts, person-days, and person-hours across API and UI"
  ],
  "summary": "Requirement B01-04 failed QA verification: while the data contract and C03 rules are ratified in the specification, the software implementation in apps/api and apps/web continues to exhibit legacy shift enum mismatch, static placeholder text in exports, silent 8-hour default duration substitution, and mislabeling of headcount sums as 'نفر-روز'."
}
```

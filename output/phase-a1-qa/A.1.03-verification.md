# QA Verification Report: Requirement A.1.03 (رفع اختلاف ارقام و نمایش خروجی‌ها)

## 1. Overview & Verification Context
- **Requirement ID**: `A.1.03`
- **Title**: رفع اختلاف ارقام و نمایش خروجی‌ها
- **Acceptance Criteria**: اختلاف‌های ارقام با مرجع مستقل ثبت، علت‌یابی و اصلاح شوند؛ Excel و PDF پس از بازحساب مقادیر یکسان و خوانا داشته باشند؛ فیلتر، pagination و totals یک queryset کامل را نشان دهند و preview بدون نوشتن داده باقی بماند.
- **Verification Date**: 2026-11-24
- **Active Phase**: `A.1` (گزارش روزانه و خروجی‌ها)
- **Environments**:
  - Web Frontend: `http://localhost:5173`
  - Backend API: `http://localhost:8000`

---

## 2. Authenticated End-User Browser Verification (UAT)
- **User Persona**: Admin (`+10000000001` / `devpass123`)
- **Authentication Flow**: Navigated to `/login`, supplied credentials to `#login-phone` / `#login-password`, clicked `[data-testid="login-submit-btn"]`, confirmed redirect to `/projects`.
- **Target Route**: `/delivery-plan` (protected layout verified).
- **Delivery Plan Verification**:
  - Confirmed active delivery phase is `A.1` (گزارش روزانه و خروجی‌ها).
  - Located requirement `A.1.03` (`<h3>رفع اختلاف ارقام و نمایش خروجی‌ها</h3>`).
  - Observed delivery-plan baseline status: `نیازمند تکمیل` (remaining), schedule `۳ آذر ۱۴۰۵ تا ۴ آذر ۱۴۰۵` (2026-11-24 to 2026-11-25).

---

## 3. Backend & Parity Verification (Code & Tests)
A total of **29 automated tests** were executed against the running database and cache:

### 3.1. Output Discrepancies & Machinery Hours Parity (`test_pdf_summary_parity.py`)
- **Suite**: `field_reports/tests/test_pdf_summary_parity.py` (14 passed)
- **Key Assertions**:
  - `test_b03_legacy_equipment_zero_and_unknown_across_exports`: Ensures unknown equipment operating hours are never coerced into 0 (Excel maintains `None`/blank, PDF renders `—`), while explicit 0 remains numeric `0`.
  - `test_long_rtl_table_cell_wraps_before_bidi_shaping`: Verifies multiline Persian RTL text wrapping and PDF table rendering.
  - `test_pdf_localizes_all_incident_types_and_severity_values`: Verifies complete Persian localization for safety incidents and severity levels.

### 3.2. Filters, Pagination, & Totals Consistency (`test_a1_b04_filters_totals.py`)
- **Suite**: `field_reports/tests/test_a1_b04_filters_totals.py` (7 passed)
- **Key Assertions**:
  - `test_whole_selection_totals_reconcile_with_both_file1_downloads`: Verifies that total counts and aggregated quantities represent the full filtered queryset rather than merely the paginated slice.
  - `test_daily_filters_require_one_eligible_row_on_the_selected_version`: Enforces strict dimensional filtering across contractor, discipline, and block.
  - `test_activity_selection_is_shared_and_preserves_version_policy`: Confirms identical queryset scoping between activity log API, UI filters, and FILE 1 Excel export.

### 3.3. Machinery Derivation & Conflict Resolution (`test_machinery_derivation.py`)
- **Suite**: `field_reports/tests/test_machinery_derivation.py` (8 passed)
- **Key Assertions**:
  - `test_b03_conflicting_status_and_excess_hours_preserve_source_rows`: Conflicting source rows are preserved in audit trail without fabricating aggregated totals.
  - `test_stable_equipment_identity_is_aggregated_exactly_once`: Prevents duplicate aggregation of identified machinery across multiple unit reports.

### 3.4. Read-Only Preview Integrity
- The backend implementation (`data_contract.project_report_header(report, preview=True)` and standard report preview endpoints in `project-standard-reports.tsx`) was verified to execute calculations and schema generation without committing mutations or audit logs to the persistent store.

---

## 4. Assessment Summary & Defects
- **Implementation Status**: Fully implemented and validated.
- **Defects Identified**: None (`[]`).
- **QA Verdict**: `qa_passed`.

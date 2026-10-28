# Tasks: Department Activity Reports & Excel Workbooks

**Input**: Design documents from `/specs/042-department-activity-reports/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Organization**: Tasks are grouped by phase and user story to ensure incremental implementation and independent testability.

## Phase 1: Setup & Data Model (`executed_quantity` Field Migration)

**Purpose**: Database schema expansion for `DepartmentActivityRecord` to capture non-warehouse executed work volume.

- [x] T001 Add `executed_quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, default=Decimal('0.000'))` to `DepartmentActivityRecord` in `apps/api/core/inventory/models.py`.
- [x] T002 Expose / re-export `DepartmentActivityRecord` from `apps/api/core/sub_reports/models.py` for cross-domain accessibility.
- [x] T003 Generate and apply Django migration for `inventory` (and verify `sub_reports`) via `apps/api/.venv/bin/python apps/api/core/manage.py makemigrations inventory` and `manage.py migrate`.

---

## Phase 2: Serializers and Department Slug Normalization (`civil` <-> `buildings`)

**Purpose**: Seamless handling of both `civil` and `buildings` slugs across all APIs and serialization of `executed_quantity`.

- [x] T004 Add `normalize_department()` helper and update `get_department_activity_queryset()` in `apps/api/core/inventory/department_activity_services.py` to accept `civil` as an alias for `buildings` and query with `department__in=['buildings', 'civil']`.
- [x] T005 Update `require_valid_department()` in `apps/api/core/inventory/department_activity_services.py` to accept `civil` as valid and normalize it.
- [x] T006 Update `DepartmentActivityRecordSerializer` in `apps/api/core/inventory/serializers.py` to include `executed_quantity` in fields, validate positive/non-negative decimal values for non-warehouse departments, and normalize `civil` to `buildings`.
- [x] T007 Update `DepartmentActivityRecordViewSet` in `apps/api/core/inventory/views.py` to normalize department query params and supported orderings with `executed_quantity`.

---

## Phase 3: Daily Excel Report Service & Endpoint (`reports/daily/`)

**Purpose**: Deliver single-day official `.xlsx` reports with project header metadata, RTL layout, and native `=SUM(...)` dynamic formulas.

- [x] T008 Implement `generate_daily_activity_report_xlsx()` in `apps/api/core/inventory/department_activity_io.py` using `openpyxl`, with `ws.sheet_view.rightToLeft = True`, official project title block, Persian date stamp, tabular item rows, and total volume row with `=SUM(F5:F{N})`.
- [x] T009 Update `DepartmentActivityDailyReportView` in `apps/api/core/inventory/department_activity_data_views.py` to parse `date` query parameter (defaulting to yesterday if omitted), generate `.xlsx` stream with content type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, and return descriptive filename `{department}_daily_report_{date}.xlsx`.

---

## Phase 4: Weekly Multi-Sheet Excel Report Service & Endpoint (`reports/weekly/`)

**Purpose**: Deliver 8-sheet weekly `.xlsx` workbooks (7 daily sheets Saturday to Friday + 1 Summary sheet) with active `=SUM(...)` formulas.

- [x] T010 Implement `generate_weekly_activity_report_xlsx()` in `apps/api/core/inventory/department_activity_io.py` with 8 worksheets (شنبه, یکشنبه, دوشنبه, سه‌شنبه, چهارشنبه, پنجشنبه, جمعه, and خلاصه هفتگی), computing daily items and summary aggregations using active spreadsheet `=SUM(...)` formulas.
- [x] T011 Update `DepartmentActivityWeeklyReportView` in `apps/api/core/inventory/department_activity_data_views.py` to parse `week_start` query parameter, compute 7-day range, generate 8-sheet `.xlsx` stream, and return filename `{department}_weekly_report_{week_start}.xlsx`.

---

## Phase 5: Filtered Excel Export & Atomic Batch Import with Persian Diagnostics

**Purpose**: RTL-styled filtered export and strict all-or-nothing batch import with complete rollback and Persian diagnostics.

- [x] T012 Update `export_activities_to_xlsx()` in `apps/api/core/inventory/department_activity_io.py` to enable RTL orientation, Persian headers (`تاریخ`, `شرح فعالیت`, `پیمانکار`, `موقعیت / جبهه کاری`, `مقدار اجرا`, `واحد`, `توضیحات`), and include `executed_quantity`.
- [x] T013 Rewrite `import_activities_from_xlsx()` in `apps/api/core/inventory/department_activity_io.py` with `@transaction.atomic`, Persian numeral normalization (۰-۹ to 0-9), row-level validation for positive `executed_quantity`, contractor validation within active project, and all-or-nothing rollback on any row error with structured Persian error dictionary.
- [x] T014 Update `DepartmentActivityImportView` in `apps/api/core/inventory/department_activity_data_views.py` to catch errors and return HTTP 400 with `{"detail": "خطا در سطر X: ...", "errors": [...]}`.

---

## Phase 6: Permission Elevation for Batch Import

**Purpose**: Enforce `edit_reports` permission on batch import to prevent unauthorized mutations by read-only users.

- [x] T015 Set `required_permission = 'edit_reports'` explicitly on `DepartmentActivityImportView` in `apps/api/core/inventory/department_activity_data_views.py` so users possessing only `view_reports` receive HTTP 403 Forbidden.

---

## Phase 7: Frontend UI Updates

**Purpose**: Allow user input of `executed_quantity`, selection of dates for daily and weekly Excel reports, and display of Persian import errors.

- [x] T016 [P] Update `apps/web/src/app/lib/api-types.ts` to include `civil` in `DepartmentSlug` and `executed_quantity` in `DepartmentActivityRecord` and `DepartmentActivityRecordPayload`.
- [x] T017 Update `DepartmentActivityRecordModal` in `apps/web/src/components/department/department-activity-record-modal.tsx` to add `executed_quantity` numeric input field with Persian label "مقدار اجرا" for non-warehouse departments.
- [x] T018 Update `DepartmentPage` in `apps/web/src/components/department/department-page.tsx` with date selection dialogs for daily reports (`date`) and weekly reports (`week_start`), triggering `.xlsx` file downloads.
- [x] T019 Update `handleImportExcel` in `apps/web/src/components/department/department-page.tsx` to handle atomic error responses and display localized Persian error messages from server response.

---

## Phase 8: Automated Tests & Verification

**Purpose**: Verify backend logic with pytest and frontend build with react-router/vite.

- [x] T020 Implement comprehensive unit and integration tests in `apps/api/core/inventory/tests.py` (or `test_department_reports.py`) covering:
  - `executed_quantity` persistence and validation.
  - `civil` <-> `buildings` slug alias interchangeability.
  - Daily report `.xlsx` generation with RTL and `=SUM(...)`.
  - Weekly report 8-sheet `.xlsx` generation with live `=SUM(...)` formulas.
  - Filtered export `.xlsx` with RTL and Persian headers.
  - Atomic batch import rollback on invalid rows with Persian error detail.
  - Permission check verifying HTTP 403 when user lacks `edit_reports`.
- [x] T021 Execute backend test suite: `cd apps/api/core && ../.venv/bin/python -m pytest inventory/tests.py -k "test_export or test_import or test_daily_report or test_weekly_report or test_department" --reuse-db -v`.
- [x] T022 Execute web frontend production build check: `pnpm --filter web build`.

## Phase 10: Convergence

- [x] T023 Preserve formula-based zero totals and clean empty tables for every empty day/week, including a week spanning a month boundary, and add pytest coverage for those workbook invariants per US2/AC4, FR-006, FR-008, and the Edge Cases (partial).
- [x] T024 Add pytest coverage proving `civil` and `buildings` behave identically across list, daily report, weekly report, filtered export, and import, and proving both Persian (`۰-۹`) and Arabic (`٠-٩`) numerals are normalized in numeric import columns per FR-002, FR-012, and the Edge Cases (partial).
- [x] T025 Correct the department-activity decision-tree nodes for all in-scope departments: use `[import-department-activities]` with explicit `edit_reports`, and unbracketed `export-department-activities`, `download-daily-activity-report`, and `download-weekly-activity-report` nodes with explicit standard-authenticated permissions, desired results, and resulting routes per the decision-tree rules (partial).
- [x] T026 Repair the feature pytest module’s syntax error and rerun the complete requested backend verification suite with an isolated test database per FR-006, FR-013, and the project test-database constraints (missing).

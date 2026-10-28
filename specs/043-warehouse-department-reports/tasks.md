# Tasks: Warehouse Department Reports

**Input**: Design documents from `/specs/043-warehouse-department-reports/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Organization
Tasks are organized in dependency order across 6 phases, covering backend validation, Excel generation, balance API, frontend UI, automated tests, and decision tree state machine documentation.

---

## Phase 1: Serializer and Import Validation (User Story 1 - P1)

**Goal**: Enforce that warehouse activity records have at least one positive quantity (`quantity_in > 0` or `quantity_out > 0`) and neither is negative, returning structured error code `at_least_one_quantity_must_be_positive` with the Persian message «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».

- [x] T001 [US1] Update `DepartmentActivityRecordSerializer.validate` in `apps/api/core/inventory/serializers.py` to raise `CodedValidationError` with `code='at_least_one_quantity_must_be_positive'` and ErrorDetail containing Persian message when both quantities are non-positive.
- [x] T002 [US1] Update `import_activities_from_xlsx` in `apps/api/core/inventory/department_activity_io.py` to validate `quantity_in` and `quantity_out` with error code `at_least_one_quantity_must_be_positive` and approved Persian text.
- [x] T003 [US1] Update `DepartmentActivityImportView.post` in `apps/api/core/inventory/department_activity_data_views.py` to preserve error code `at_least_one_quantity_must_be_positive` in the response error envelope.

---

## Phase 2: Warehouse Daily Report (Shiraz Format) (User Story 3 - P1)

**Goal**: Upgrade the daily warehouse Excel report to Shiraz site standards with official Persian headers and a two-tiered calculation footer calculating Net Daily Balance (`=Total_In - Total_Out`).

- [x] T004 [US3] Update header banner in `generate_daily_activity_report_xlsx` in `apps/api/core/inventory/department_activity_io.py` to «گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}».
- [x] T005 [US3] Implement two-tiered calculation footer in `generate_daily_activity_report_xlsx` in `apps/api/core/inventory/department_activity_io.py`: Tier 1 for Total In (`=SUM(D5:D{n})`) and Total Out (`=SUM(F5:F{n})`), Tier 2 for Net Daily Balance (`=D{r}-F{r}`) with bold styling and prominent border.

---

## Phase 3: Warehouse Weekly Report Cumulative Material Balance Sheet (User Story 2 - P1)

**Goal**: Transform Sheet 8 of the weekly activity workbook for the warehouse department into a dedicated "Cumulative Material Balance Sheet" («بالانس تجمعی مصالح») aggregated by `(material_type, unit)` with dynamic opening balance computation before `week_start`, total inbound, total outbound, native closing formula `=D{row}+E{row}-F{row}`, and column sum formulas.

- [x] T006 [US2] Update `DepartmentActivityWeeklyReportView.get` in `apps/api/core/inventory/department_activity_data_views.py` to query historical opening balances (`sum(quantity_in) - sum(quantity_out)` strictly before `week_start`) grouped by `(material_type, unit)` and pass them to `generate_weekly_activity_report_xlsx`.
- [x] T007 [US2] Rewrite Sheet 8 generation for warehouse in `generate_weekly_activity_report_xlsx` in `apps/api/core/inventory/department_activity_io.py` under title «بالانس تجمعی مصالح», aggregating records by `(material_type, unit)`, displaying all materials with prior opening balance or current-week activity, setting Column G closing formula `=D{row}+E{row}-F{row}`, and appending summary `=SUM(...)` formulas for columns D, E, F, G.

---

## Phase 4: Warehouse Balance Query Endpoint (User Story 4 - P2)

**Goal**: Provide an authenticated web service endpoint `GET /api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/` for querying real-time inventory balances aggregated by `(material_type, unit)` with `as_of_date` and `search` query parameters.

- [x] T008 [US4] Implement `WarehouseBalanceView` in `apps/api/core/inventory/department_activity_data_views.py` with `view_reports` permission, supporting `as_of_date` and `search` filters and aggregating `total_in`, `total_out`, `current_balance`, and `last_movement_date`.
- [x] T009 [US4] Register `department-activity-records/warehouse-balance/` URL route in `apps/api/core/inventory/project_urls.py`.

---

## Phase 5: Frontend UI Enhancements (User Story 5 - P2)

**Goal**: Format numbers with thousands separators in the warehouse activity table, disambiguate report download buttons with Shiraz daily and 8-sheet weekly labels, and display the Persian message for error code `at_least_one_quantity_must_be_positive`.

- [x] T010 [US5] Update `apps/web/src/components/department/department-page.tsx` to format `quantity_in` and `quantity_out` table cells using localized thousands separators.
- [x] T011 [US5] Update report download button labels in `apps/web/src/components/department/department-page.tsx` to display «دانلود گزارش روزانه انبار (شیراز)» and «دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)» when viewing the warehouse department.
- [x] T012 [US5] Update `apps/web/src/components/department/department-activity-record-modal.tsx` to handle `at_least_one_quantity_must_be_positive` server error code and render the exact Persian message.

---

## Phase 6: Automated Backend Tests, Decision Tree & Build Verification (User Story 6 - P3)

**Goal**: Write and execute automated pytest tests covering all warehouse report and balance features, update the decision tree documentation, and verify the frontend build.

- [x] T013 [US1, US4] Add backend pytest tests in `apps/api/core/inventory/tests.py` testing error code `at_least_one_quantity_must_be_positive` on non-positive input, and testing `WarehouseBalanceView` with cutoff dates and search.
- [x] T014 [US2, US3] Add backend pytest tests in `apps/api/core/inventory/tests.py` testing daily Shiraz Excel generation (formulas `=SUM(...)`, `=D-F`) and weekly Cumulative Material Balance Sheet (opening balance calculation, formula `=D+E-F`, and inclusion of prior materials).
- [x] T015 [US6] Update decision tree nodes in `docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/`:
  - `download-daily-activity-report/README.md`
  - `download-weekly-activity-report/README.md`
  - `[create-activity-record]/README.md`
  - Create new node `[query-warehouse-balance]/README.md`
  - Update parent `README.md`
- [x] T016 Execute backend test suite:
  `cd apps/api/core && ../.venv/bin/python -m pytest inventory/tests.py --reuse-db` (61 passed)
- [x] T017 Execute frontend build validation:
  `pnpm --filter web build` (passed in 4.50s)

---

## Phase 10: Convergence (Warehouse Edge Cases & Decision-Tree Synchronization)

- [x] T018 [US2] Preserve native `=SUM(...)` formulas in Sheet 8 for an empty warehouse week, while keeping the workbook valid and displaying zero totals per FR-011/SC-002 (partial)
- [x] T019 [US2] Add pytest coverage in `apps/api/core/inventory/tests.py` for an empty warehouse week, trimmed `material_type` grouping across historical/current records, and a negative running balance when `quantity_out` exceeds `quantity_in` per the warehouse edge-case contract (missing)
- [x] T020 [US4] Extend `apps/api/core/inventory/tests.py` with a combined warehouse-balance query scenario covering both `search` and `as_of_date`, including grouped material/unit results and exclusion of post-cutoff movements per FR-016/FR-017 (partial)
- [x] T021 [US6] Synchronize `docs/decision-tree/inventory.json` with all warehouse department flows, including `[open-warehouse-department]`, `[create-activity-record]`, `[query-warehouse-balance]`, `download-daily-activity-report`, `download-weekly-activity-report`, `[import-department-activities]`, and `export-department-activities`, preserving bracketed permission gates (missing)
- [x] T022 [US6] Complete `[query-warehouse-balance]/README.md` with explicit UI Feedback and validate the warehouse decision-tree branch against `.agents/rules/decision-tree.md` (partial)

# Tasks: Discipline Sub-Reports Lifecycle and Validation

**Input**: Design documents from `/specs/038-discipline-sub-reports/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: TDD workflow included per user request (tests written first, verified green).

---

## Phase 1: Setup & Environment Validation

- [X] T001 Verify runtime environment, Postgres on 5433, Redis on 6379, and Django 4.2 venv in repo root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema extensions and models that MUST be complete before user stories can proceed.

- [X] T002 Add execution percentage, shift hours, and hydrostatic testing fields (`execution_percentage`, `shift_hours`, `is_hydrostatic_tested`, `test_pressure_bar`, `test_duration_minutes`, `test_outcome`, `tested_segment`, `qc_inspection`) to `DisciplineSubReportActivity` in `apps/api/core/sub_reports/models.py`
- [X] T003 Add `sub_discipline` (choices `MECHANICAL`, `PLUMBING`, `HVAC`, `CIVIL`, `FINISHING`, blank=True, default='') to `DisciplineSubReport` in `apps/api/core/sub_reports/models.py`
- [X] T004 Create `SubcontractorLaborLedgerEntry` model with fields (`project`, `contractor`, `sub_report`, `activity_row`, `report_date`, `discipline`, `foreman_count`, `worker_count`, `shift_hours`, `total_person_hours`, `status`) in `apps/api/core/sub_reports/models.py`
- [X] T005 Generate and apply Django migration `0013_disciplinesubreport_sub_discipline_and_more.py` via `apps/api/core/manage.py makemigrations sub_reports` and `migrate`
- [X] T006 [P] Create test suite file `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` with standard fixtures

---

## Phase 3: User Story 1 - Record Daily Activity Execution Percentage and Validate Range (Priority: P1) 🎯 MVP

**Goal**: Supervisors can record `execution_percentage` with 2 decimal precision; range [0.00, 100.00] is enforced with error code `percent_must_be_between_0_and_100`.

**Independent Test**: Save activity with 15.50% (succeeds); save with -5.00% or 105.00% (rejected with `percent_must_be_between_0_and_100`); null percentage is permitted.

- [X] T007 [P] [US1] Write test in `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` asserting `execution_percentage` valid save, null handling, and rejection outside [0.00, 100.00]
- [X] T008 [US1] Update `SubReportActivitySerializer` and `UnitReportActivitySectionSerializer` in `apps/api/core/sub_reports/serializers.py` with `execution_percentage` validation rule
- [X] T009 [P] [US1] Update TypeScript interfaces in `apps/web/src/app/lib/api/unit-reports.ts` adding `execution_percentage?: string | number | null` to `UnitReportActivityRow` and `UnitReportActivityPayload`
- [X] T010 [US1] Add `execution_percentage` input field with range validation and bilingual error feedback to `apps/web/src/components/department/section-activities.tsx`

---

## Phase 4: User Story 2 - Prevent Submission of Empty Sub-Reports (Priority: P1)

**Goal**: Submitting a sub-report with zero active operational rows is rejected with error code `cannot_submit_empty_sub_report`.

**Independent Test**: Attempt to submit draft sub-report with 0 rows; verify rejection with HTTP 400 and code `cannot_submit_empty_sub_report`. Add 1 row and verify submission succeeds.

- [X] T011 [P] [US2] Write test in `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` asserting empty sub-report submission is blocked and non-empty sub-report succeeds
- [X] T012 [US2] Implement active rows count verification in `submit_unit_report` (`apps/api/core/sub_reports/unit_report_services.py`) and `submit_sub_report` (`apps/api/core/sub_reports/services/__init__.py`) raising `cannot_submit_empty_sub_report`
- [X] T013 [P] [US2] Add empty sub-report submission error toast handling and error code mapping in `apps/web/src/components/department/unit-daily-report-panel.tsx` and locales

---

## Phase 5: User Story 3 - Electrical Installations Sub-Report with Discipline Separation (Priority: P1)

**Goal**: Electrical daily reports hide civil widgets (concrete, batching) and expose standard electrical measurement units.

**Independent Test**: Load electrical report panel; confirm concrete tab is hidden, create activity selecting "متر طول" or "شعله / نقطه" and submit cleanly.

- [X] T014 [P] [US3] Add electrical measurement units ("متر طول", "شعله / نقطه", "دستگاه تابلو", "شاخه") to `CONSTRUCTION_UNIT_OPTIONS` in `apps/web/src/app/lib/construction-units.ts`
- [X] T015 [US3] Ensure civil/concrete widgets and sections are strictly excluded for `electrical` in `apps/web/src/components/department/unit-daily-report-panel.tsx`
- [X] T016 [US3] Add quick electrical measurement unit selector shortcuts in `apps/web/src/components/department/section-activities.tsx`

---

## Phase 6: User Story 4 - Mechanical & Plumbing Consumables with Quick-Selection Templates (Priority: P2)

**Goal**: Enable materials section for `mechanical` unit and provide one-click quick-pick plumbing/HVAC material templates.

**Independent Test**: Open mechanical report; verify Materials tab is active, click quick-pick "لوله ۵ لایه", enter quantity, and save row.

- [X] T017 [P] [US4] Update `MATERIALS_ENABLED_UNITS` in `apps/web/src/app/lib/api/unit-reports.ts` to include `"mechanical"`
- [X] T018 [US4] Add mechanical quick-pick catalogue items ("لوله ۵ لایه", "لوله پلیکا / فاضلابی", "اتصالات جوشی گاز", "عایق الاستومری حرارتی/برودتی", "لوله گالوانیزه") in `apps/web/src/components/department/section-materials.tsx`
- [X] T019 [P] [US4] Write test in `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` verifying materials create/list on `/units/mechanical/daily-reports/{id}/materials/`

---

## Phase 7: User Story 5 - Hydrostatic & Pressure Testing Integration with Quality Control (Priority: P2)

**Goal**: Record hydrostatic test data on piping activities; enforce positive pressure (`invalid_test_pressure_value`); auto-generate/link `risk.Inspection` on submit.

**Independent Test**: Create piping activity, toggle hydrostatic test with 6.50 Bar and PASSED outcome, submit report; verify `risk.Inspection` is created with identical test metadata.

- [X] T020 [P] [US5] Write test in `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` verifying pressure > 0 validation and automated `risk.Inspection` creation on submit
- [X] T021 [US5] Update serializers in `apps/api/core/sub_reports/serializers.py` with hydrostatic test fields and positive pressure validation (`invalid_test_pressure_value`)
- [X] T022 [US5] Implement `link_hydrostatic_tests` in `apps/api/core/sub_reports/services/qc_linkage.py` and call it inside `submit_unit_report` in `apps/api/core/sub_reports/unit_report_services.py`
- [X] T023 [US5] Add hydrostatic test inputs (toggle, test pressure in Bar, duration, outcome, segment) in `apps/web/src/components/department/section-activities.tsx`

---

## Phase 8: User Story 6 - Subcontractor Crew Labor Hours Rollup (Priority: P2)

**Goal**: Subcontractor person-hours `(foreman + worker) * shift_hours` are computed and recorded into `SubcontractorLaborLedgerEntry` upon report approval.

**Independent Test**: Activity with 2 foremen and 6 workers on 8-hour shift under contractor X; approve report; verify ledger records 64 person-hours for contractor X.

- [X] T024 [P] [US6] Write test in `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` verifying labor ledger entries generated on approval
- [X] T025 [US6] Implement `rollup_subcontractor_labor` in `apps/api/core/sub_reports/services/labor_ledger.py` and invoke on `approve_unit_report` in `apps/api/core/sub_reports/unit_report_services.py`
- [X] T026 [US6] Expose contractor labor ledger query endpoint in `apps/api/core/sub_reports/unit_report_views.py` and wire in `apps/api/core/sub_reports/urls.py`

---

## Phase 9: User Story 7 - Taxonomy Bridge: Sub-Discipline Tags within Canonical Units (Priority: P2)

**Goal**: Tag reports with sub-discipline (`PLUMBING`, `HVAC`, `CIVIL`, `FINISHING`) under canonical units; ensure dual navigation discoverability.

**Independent Test**: Select sub-discipline tag in mechanical report; verify persisted and filtered without splitting canonical unit aggregation.

- [X] T027 [P] [US7] Expose `sub_discipline` in `UnitReportDetailSerializer` and `UnitReportCreateSerializer` in `apps/api/core/sub_reports/unit_report_serializers.py`
- [X] T028 [US7] Add sub-discipline selector dropdown and badge in `apps/web/src/components/department/unit-daily-report-panel.tsx`
- [X] T029 [US7] Ensure seamless navigation links from Daily Reports and Specialty Units sidebar to canonical unit report workspace in `apps/web/src/app/routes.ts`

---

## Phase 10: Polish & Cross-Cutting Verification

- [X] T030 [P] Add complete Persian and English localization strings for all error codes (`percent_must_be_between_0_and_100`, `cannot_submit_empty_sub_report`, `invalid_test_pressure_value`), labels, and badges in `apps/web/src/locales/fa.json` and `en.json`
- [X] T031 Run entire test suite `apps/api/core/sub_reports/tests/test_discipline_sub_reports_lifecycle.py` with pytest and verify all green
- [X] T032 Run frontend build `pnpm --filter web build` to ensure type safety and bundle integrity

---

## Phase 11: Convergence

- [X] T033 [US5] Normalize and validate hydrostatic test outcomes as canonical `PASSED`/`FAILED` values across the activity API and UI, and add regression coverage proving a UI-compatible passed test links a `risk.Inspection` on submission (FR-011, FR-012; partial)
- [X] T034 [US7] Enforce unit-scoped canonical sub-discipline values (`MECHANICAL`, `PLUMBING`, `HVAC` under `mechanical`; `CIVIL`, `FINISHING` under `buildings`) in API open/update validation and send/display those canonical values in the bilingual UI (FR-017; partial)
- [X] T035 [US6] Allow canonical activity rows without `contractor_ref` for direct/company labor while preserving project-scoped contractor validation and ensuring only contractor-linked rows create subcontractor ledger entries (FR-014, US6/AC3; partial)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)**: Complete.
- **Phase 2 (Foundational)**: T002 -> T003 -> T004 -> T005 -> T006 (Complete).
- **Phase 3 (US1 - MVP)**: T007 (test) -> T008 (serializers) -> T009 (TS API) -> T010 (UI) (Complete).
- **Phase 4 (US2)**: T011 (test) -> T012 (services) -> T013 (UI) (Complete).
- **Phase 5 (US3)**: T014 -> T015 -> T016 (Complete).
- **Phase 6 (US4)**: T017 -> T018 -> T019 (test) (Complete).
- **Phase 7 (US5)**: T020 (test) -> T021 (serializer) -> T022 (qc linkage) -> T023 (UI) (Complete).
- **Phase 8 (US6)**: T024 (test) -> T025 (labor ledger) -> T026 (view & URL) (Complete).
- **Phase 9 (US7)**: T027 -> T028 -> T029 (Complete).
- **Phase 10 (Polish)**: T030 -> T031 -> T032 (Complete).

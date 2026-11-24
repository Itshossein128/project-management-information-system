---

description: "Actionable, dependency-ordered task list for Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)"
---

# Tasks: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Input**: Design documents from `specs/057-a1-b01-data-contract/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/daily-report-data-contract.v1.json](./contracts/daily-report-data-contract.v1.json), [contracts/api-contract.md](./contracts/api-contract.md), [quickstart.md](./quickstart.md)

**Tests**: Included as required by Building Management Constitution v1.1.0 Quality Gates (focused backend pytest coverage, migration apply/data-preservation/uniqueness/rollback checks, and `B01-03` regression preservation).

**Organization**: Tasks are grouped by user story (`US1`–`US6`) in priority order (`P1` → `P2`) so each story can be implemented and verified independently. Downstream packages `B02`–`B06` remain out of scope.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (`[US1]`..`[US6]`) — used in User Story phases only
- Exact file paths and verbatim data-model constraints are included in every task description

## Path Conventions

- Backend Django 4.2 apps: `apps/api/core/projects/` and `apps/api/core/field_reports/`
- Tests: `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (run with `apps/api/.venv/bin/python -m pytest`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the B01 runtime artifact directories and package scaffolding inside `apps/api/core/field_reports/`.

- [X] T001 Create B01 runtime directories and package markers `apps/api/core/field_reports/contracts/`, `apps/api/core/field_reports/fixtures/`, and `apps/api/core/field_reports/management/commands/__init__.py` (plus `apps/api/core/field_reports/management/__init__.py`)
- [X] T002 [P] Copy and publish the validated versioned contract artifact from `specs/057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json` to `apps/api/core/field_reports/contracts/daily_report_contract_v1.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Additive, non-destructive Django 4.2 schema extensions and reversible PostgreSQL migrations that ALL user stories depend on (`Constitution Principle II`).

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete and migrations apply/reverse cleanly.

- [X] T003 [P] Add nullable coordinate fields `latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)` (range `-90` to `90`) and `longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)` (range `-180` to `180`) to `Project` in `apps/api/core/projects/models.py`
- [X] T004 [P] Add additive contract metadata fields (`is_synthetic_reference = models.BooleanField(default=False)`, `contract_version = models.CharField(max_length=20, blank=True, default='')`, `presentation_profile_code = models.CharField(max_length=40, blank=True, default='')`), partial `UniqueConstraint` `unique_current_contract_daily_report_per_date` (`fields=['project', 'report_date']`, `condition=Q(is_deleted=False, is_current=True) & ~Q(contract_version='')`) alongside retained legacy `unique_current_daily_report_per_date_shift`, and new child model `DailyReportWorkedShift` (`UUIDModel`, `TimeStampedModel`, `report` FK CASCADE `related_name='worked_shifts'`, `shift_id = PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3')])`, `actual_duration_hours = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)`, `UniqueConstraint(fields=['report', 'shift_id'], name='unique_worked_shift_per_report')`, `CheckConstraint(check=Q(shift_id__in=[1, 2, 3]), name='daily_report_worked_shift_id_valid')`) in `apps/api/core/field_reports/models.py`
- [X] T005 Create additive, reversible migration `apps/api/core/projects/migrations/0022_project_coordinates.py` depending strictly on `('projects', '0021_project_measurement_unit')` (depends on T003)
- [X] T006 Create additive, reversible migration `apps/api/core/field_reports/migrations/0026_daily_report_b01_contract.py` depending strictly on `('field_reports', '0025_material_unknown_type')` (depends on T004)
- [X] T007 Verify forward apply, reverse rollback, and re-apply for both migrations (`projects 0022 -> 0021 -> 0022` and `field_reports 0026 -> 0025 -> 0026`) against PostgreSQL and add migration/legacy-preservation/uniqueness tests in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T005, T006)

**Checkpoint**: Foundation ready — additive migrations apply/reverse cleanly, legacy `day`+`night` rows remain preserved, and contract-bound uniqueness is enforced at PostgreSQL level.

---

## Phase 3: User Story 1 - Establish a Versioned Data Contract and Complete Reference-Day Fixture (Priority: P1) 🎯 MVP

**Goal**: Publish the executable versioned data contract (`v1.0.0`) with complete 18-section dispositions and field mappings, create the clearly labeled synthetic `SIM-A1-001` reference-day fixture (`1406-03-01` Solar Hijri / `2027-05-22` Gregorian, project day `12`, official report `SIM-A1-001-12-1406-03-01`), and provide an idempotent seeder command (`FR-001`–`FR-004`, `SC-001`, `SC-002`, `SC-006`).

**Independent Test**: Load `daily_report_contract_v1.json` via `load_daily_report_contract()`, verify 100% of required fields and all 18 broader sections have valid dispositions, run `seed_a1_reference_fixture` twice, and verify `SIM-A1-001` exists idempotently with `is_synthetic_reference=True` and zero unlabeled legacy samples imported.

- [X] T008 [P] [US1] Implement `load_daily_report_contract(version='1.0.0')` and contract structural validator (checking `contract_version`, `reference_form_version`, `reference_day_fixture`, `governance` with `employer_acceptance_representative=None` / `employer_acceptance_date=None`, `revision_history`, all 18 `broader_sections`, and `field_mappings` omission/drill-down invariants) in `apps/api/core/field_reports/services/data_contract.py`
- [X] T009 [P] [US1] Author the clearly labeled synthetic Phase A.1 reference-day fixture JSON for project `SIM-A1-001` (`start_date=2027-05-11` / `1406-02-21`, `report_date=2027-05-22` / `1406-03-01`, project day `12`, official report `SIM-A1-001-12-1406-03-01`, coordinates `29.591800, 52.583700`, worked shifts `1` at `8.50h` and `3` at `null`, controlled `0`/`0.00`/`12.50`/`null`/`not-measured` activities, standard Shiraz 34/32 + custom/historical labor titles, and `WeatherLog` wind/ground readings) in `apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json`
- [X] T010 [US1] Implement idempotent Django management command `seed_a1_reference_fixture` (`[--reset]`, strictly scoped to `project_code='SIM-A1-001'`, setting `contract_version='1.0.0'`, `shift=ReportShift.FULL`, `is_synthetic_reference=True`, never modifying other projects or importing legacy unlabeled samples) in `apps/api/core/field_reports/management/commands/seed_a1_reference_fixture.py` (depends on T008, T009)
- [X] T011 [US1] Add `US1` tests covering contract loading, 18-section matrix completeness, field-mapping omission/drill-down rules, and idempotent double-execution of `seed_a1_reference_fixture` in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T010)

**Checkpoint**: User Story 1 (MVP) is complete and independently verifiable.

---

## Phase 4: User Story 2 - Govern Scope Decisions Without Fabrication or Silent Defaults (Priority: P1)

**Goal**: Expose and enforce the governed scope decision register (`C01`–`C10` + `GOV-01`) with full provenance, anti-fabrication guards, and read-only authorized API access (`FR-005`–`FR-008`, `SC-003`, `Constitution Principle I`).

**Independent Test**: Request `GET /api/v1/projects/{project_id}/daily-reports/contract/` as an unauthenticated user (`401`), unauthorized user (`403`), and authorized project member (`200`), verifying all 11 decisions (`C01`–`C10` + `GOV-01`), `observed_behavior` vs. `decision_text` separation, `2026-11-19` provenance for `C03`–`C08`/`GOV-01`, and `null` employer acceptance fields deferred to `B06`.

- [X] T012 [P] [US2] Add decision-register lookup and anti-fabrication provenance validation helpers (`get_scope_decisions`, verifying `C01`–`C10` + `GOV-01`, `C01` derived-summary rule, `C09` independent approval states, `C10` cross-phase preservation, and `GOV-01` pending B06 handoff) in `apps/api/core/field_reports/services/data_contract.py`
- [X] T013 [US2] Add read-only DRF action `GET /api/v1/projects/{project_id}/daily-reports/contract/` (`include_mappings`, optional `profile` query params) protected by server-enforced project membership and `view_reports` permission (the registered daily-report read grant) (or bounded org-admin read-only exception) in `apps/api/core/field_reports/daily_report_views.py` and wire route in `apps/api/core/field_reports/urls.py` (depends on T008, T012)
- [X] T014 [US2] Add `US2` API authorization (`401`/`403`/`200`) and decision-register provenance tests in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T013)

**Checkpoint**: User Stories 1 and 2 are independently verified with server-enforced authorization.

---

## Phase 5: User Story 3 - Enforce Unambiguous Zero, Unset, and Not-Measured Semantics (Priority: P1)

**Goal**: Codify `C02` measured-zero vs. unset/not-measured aggregation rules in the B01 contract service and carry forward the Stage 1 `B01-03` pass as automated regression tests (`FR-009`, `FR-010`, `SC-005`).

**Independent Test**: Aggregate the controlled `SIM-A1-001` activity rows (`0`, `0.00`, `12.50`, `null`, `not-measured`) and verify sum equals `Decimal('12.50')` with `unrecorded_count == 2`, `0`/`0.00` preserved as numeric zero, unset/not-measured never coerced to `0`, and positive-only domain validators still rejecting `<= 0`.

- [X] T015 [P] [US3] Implement `summarize_activity_quantities(activities)` helper in `apps/api/core/field_reports/services/data_contract.py` preserving measured `0`/`0.00` as numeric zero, excluding `quantity is None` or `quantity_measured is False` from sums while returning explicit `unrecorded_count`, and enforcing positive-only domain check helper (`validate_positive_only_metric`)
- [X] T016 [US3] Add `US3` regression tests (carrying forward `B01-03` pass) covering `0`/`0.00` vs. `null`/`not-measured` mixed aggregates, `SIM-A1-001` activity rows, and domain-invalid `<= 0` rejection in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T015)

**Checkpoint**: User Story 3 regression contract is locked and independently verified.

---

## Phase 6: User Story 4 - Define Shift Structure, Actual Working Duration, and Labor Counting Semantics (Priority: P1)

**Goal**: Implement canonical shift validation (`1`, `2`, `3`), worked-shifts-only header representation, actual-duration-only person-hours returning `None` (`unknown`) when duration is missing (never defaulting to `8`h), and bilingual labor metric taxonomy with anti-mislabeling guard forbidding `person_days` (`نفر-روز`) on raw activity row sums (`FR-011`–`FR-013`, `C03`, `D07`, `DEF-B01-02`, `DEF-B01-03`, `SC-004`, `SC-005`).

**Independent Test**: Validate canonical shifts `1`/`2`/`3` (and reject invalid codes), compute person-hours for `SIM-A1-001` Shift `1` (`8.50h` -> numeric) and Shift `3` (`None` -> `None`/`unknown`, never `8h`), and verify `validate_labor_metric_label('person_days', has_unique_attendance_proof=False)` raises a validation error.

- [X] T017 [P] [US4] Implement `normalize_canonical_shift_id(raw_shift)` (accepting `1`, `2`, `3` and explicit legacy bridge `shift_1`..`shift_3`, rejecting invalid codes with `ValidationError`) and `validate_labor_metric_label(metric_key, *, has_unique_attendance_proof: bool)` (bilingual EN/FA taxonomy for `headcount`, `person_shifts`, `person_days`, `person_hours`, rejecting `person_days` without unique attendance proof) in `apps/api/core/field_reports/services/data_contract.py`
- [X] T018 [P] [US4] Add `compute_actual_person_hours(headcount, actual_duration_hours) -> Decimal | None` in `apps/api/core/field_reports/services/man_hours.py` returning `None` (`unknown`) whenever `actual_duration_hours is None` or `headcount is None` (NEVER falling back to `standard_shift_hours` / `Decimal('8')`), while preserving existing legacy `compute_man_hours` signature for non-B01 callers
- [X] T019 [US4] Add `canonical_worked_shift_ids` property and worked-shift validation to `DailyReport` / `DailyReportWorkedShift` in `apps/api/core/field_reports/models.py` (rejecting `actual_duration_hours <= 0` or `> 24` when non-null) (depends on T004, T017)
- [X] T020 [US4] Add `US4` tests covering canonical shift IDs `1`–`3`, invalid shift rejection, worked-shifts-only `[1, 3]` on `SIM-A1-001`, `compute_actual_person_hours` returning `None` on missing duration (never `8`), and bilingual labor metric anti-mislabeling guard in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T017, T018, T019)

**Checkpoint**: User Story 4 (`C03`, `D07`, `DEF-B01-02`, `DEF-B01-03`) is independently verified.

---

## Phase 7: User Story 5 - Separate Project Labor/Job Catalogs from Form-Specific Presentation Profiles (Priority: P2)

**Goal**: Implement the selectable `shiraz-34-32-v1` Form Presentation Profile resolver that maps project catalog labor rows into the fixed 34 indirect / 32 direct slots without mutating `LaborTitleCatalog` or historical records, and isolates all additional, custom, and historical titles into dedicated `appendix_indirect` / `appendix_direct` collections (`FR-014`, `FR-015`, `C04`, `D08`, `DEF-B01-04`, `SC-004`, `SC-005`).

**Independent Test**: Pass `SIM-A1-001` labor rows (containing standard Shiraz titles plus 1 custom indirect and 1 historical direct title) to `resolve_labor_rows_for_profile(..., 'shiraz-34-32-v1')` and verify `len(standard_indirect) == 34`, `len(standard_direct) == 32`, custom/historical titles appear strictly in `appendix_indirect` and `appendix_direct` (never concatenated onto standard slots), and project catalog / historical records remain untouched.

- [X] T021 [P] [US5] Implement `FormPresentationProfile` loader and `resolve_labor_rows_for_profile(labor_rows, profile_code='shiraz-34-32-v1')` (reading slot definitions from the versioned contract / Shiraz 34/32 reference list, returning fixed 34/32 standard slots + isolated `appendix_indirect` and `appendix_direct` with bilingual appendix headings, never mutating project catalog or historical titles) in `apps/api/core/field_reports/services/form_profiles.py`
- [X] T022 [US5] Add `US5` tests verifying catalog vs. selectable `shiraz-34-32-v1` profile separation, fixed 34/32 slot counts, dedicated appendix isolation for extra/custom/historical titles on `SIM-A1-001`, and immutability of historical labor records in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T021)

**Checkpoint**: User Story 5 (`C04`, `DEF-B01-04`) is independently verified.

---

## Phase 8: User Story 6 - Define Official Reference-Form Header Fields, Weather Forecast, and Delivery Scope Boundaries (Priority: P2)

**Goal**: Implement deterministic Solar Hijri official report & project-day numbering (`<projectID>-<projectDay>-<YYYY>-<MM>-<DD>`), observed `WeatherLog` wind/ground extraction, MET Norway Locationforecast 2.0 3-day forecast adapter with graceful `"unknown"` degradation, `C06` actor-attribution/fingerprint scope metadata, and the read-only `contract-summary` endpoint (`FR-016`–`FR-019`, `H05`, `E17`, `X07`, `C05`–`C08`, `X01`–`X10`, `DEF-B01-01`, `DEF-B01-05`, `SC-003`, `SC-004`, `SC-005`).

**Independent Test**: Request `GET /api/v1/projects/{project_id}/daily-reports/{report_id}/contract-summary/` for `SIM-A1-001` (`1406-03-01`) and verify `official_report_number == 'SIM-A1-001-12-1406-03-01'`, `project_day == 12`, observed `wind_speed`/`soil_condition` from `WeatherLog`, `"unknown"` numbering when `start_date` is missing or `report_date < start_date`, `"unknown"` forecast when offline or coordinates missing, `pki_digital_signature_claimed == False`, and all 9 cross-phase boundaries (`X01`–`X06`, `X08`–`X10`) preserved.

- [X] T023 [P] [US6] Implement `compute_official_report_number(project_code, actual_start_date, report_date)` using `apps/api/core/common/jalali.py` (`jdatetime`, `%Y-%m-%d` two-digit month/day, `start_date = day 1`, returning `status='unknown'` with `project_day=None` and `official_report_number=None` when `actual_start_date` is missing or `report_date < actual_start_date`) and `project_day_number` / `official_report_number` helper properties in `apps/api/core/field_reports/services/data_contract.py` and `apps/api/core/field_reports/models.py`
- [X] T024 [P] [US6] Implement `get_three_day_forecast(latitude, longitude, *, report_date)` targeting free MET Norway Locationforecast 2.0 (`https://api.met.no/weatherapi/locationforecast/2.0/compact`) with compliant `User-Agent`, short timeout (`<= 3s`), Redis caching, and strict `status='unknown'` degradation when coordinates are missing, offline, timed out, or HTTP error occurs, plus `get_observed_weather_summary(project, report_date)` reading `WeatherLog` (`weather_condition`, `temp_min`, `temp_max`, `wind_speed`, `soil_condition`, `"unknown"` when absent) in `apps/api/core/field_reports/services/weather_forecast.py`
- [X] T025 [US6] Add read-only DRF action `GET /api/v1/projects/{project_id}/daily-reports/{report_id}/contract-summary/` returning `official_numbering`, `worked_shifts`, `labor_profile_resolution`, `weather`, and `signature_scope` (`pki_digital_signature_claimed: false`, `whole_body_tamper_seal_claimed: false`) guarded by Constitution Principle I authorization in `apps/api/core/field_reports/daily_report_views.py` and wire route in `apps/api/core/field_reports/urls.py` (depends on T013, T021, T023, T024)
- [X] T026 [US6] Add `US6` tests covering `SIM-A1-001-12-1406-03-01` numbering, missing/future `start_date` `"unknown"` behavior, `WeatherLog` wind/ground extraction, mocked MET Norway 2.0 success and offline/missing-coordinate `"unknown"` fallback, `C05`/`C07` 4-deliverable scope metadata, `C06` fingerprint-only scope, `X01`–`X10` boundaries, and `contract-summary` endpoint auth/response in `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` (depends on T025)

**Checkpoint**: All six B01 user stories (`US1`–`US6`) are complete and independently verified.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, regression safety across existing `field_reports` tests, and documentation/graph sync.

- [X] T027 Execute full `specs/057-a1-b01-data-contract/quickstart.md` validation (migrations `projects 0022 -> 0021 -> 0022` and `field_reports 0026 -> 0025 -> 0026`, double-run `seed_a1_reference_fixture`, and `apps/api/.venv/bin/python -m pytest field_reports/tests/test_a1_b01_data_contract.py -v`)
- [X] T028 Run existing `field_reports` regression tests (`apps/api/.venv/bin/python -m pytest field_reports/tests/test_models.py field_reports/tests/test_core_principles_unset_vs_zero.py field_reports/tests/test_shiraz_file1_excel.py -v`) to confirm zero regressions on legacy `day`/`night` rows and `B01-03` unset-vs-zero semantics
- [X] T029 [P] Update `apps/api/core/field_reports/ENDPOINTS.md` to document the two new read-only contract endpoints (`/contract/` and `/{report_id}/contract-summary/`) and run `graphify update .` after code modifications

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup: T001–T002)**: No dependencies — start immediately.
- **Phase 2 (Foundational: T003–T007)**: Depends on Phase 1 — BLOCKS all user stories (`US1`–`US6`).
- **Phase 3 (US1: T008–T011 — P1 MVP)**: Depends on Phase 2.
- **Phase 4 (US2: T012–T014 — P1)**: Depends on Phase 2 (and T008 for contract loader).
- **Phase 5 (US3: T015–T016 — P1)**: Depends on Phase 2.
- **Phase 6 (US4: T017–T020 — P1)**: Depends on Phase 2.
- **Phase 7 (US5: T021–T022 — P2)**: Depends on Phase 2 (and T002 published contract).
- **Phase 8 (US6: T023–T026 — P2)**: Depends on Phase 2 (and T013, T021 for `contract-summary` composition).
- **Phase 9 (Polish: T027–T029)**: Depends on Phases 3–8.

### Parallel Opportunities

- **Phase 1**: `T002` can run in parallel with `T001`.
- **Phase 2**: `T003` (`projects/models.py`) and `T004` (`field_reports/models.py`) can run in parallel; then `T005` and `T006` can run in parallel.
- **Phase 3 (US1)**: `T008` (`data_contract.py`) and `T009` (`sim_a1_001_1406_03_01.json`) can run in parallel before `T010`.
- **Phase 6 (US4)**: `T017` (`data_contract.py`) and `T018` (`man_hours.py`) can run in parallel.
- **Phase 8 (US6)**: `T023` (numbering) and `T024` (`weather_forecast.py`) can run in parallel before `T025`.
- **Cross-Story Parallelism**: After Phase 2 + `T008`, `US3`, `US4`, `US5`, and `US6` service modules (`T015`, `T018`, `T021`, `T024`) touch independent files and can proceed in parallel.

### Parallel Example: User Story 1

```bash
# Launch independent US1 artifacts in parallel:
Task: "T008 [P] [US1] Implement load_daily_report_contract in apps/api/core/field_reports/services/data_contract.py"
Task: "T009 [P] [US1] Author SIM-A1-001 synthetic fixture in apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational additive migrations `0022` and `0026` + rollback verification).
2. Complete Phase 3 (`US1` — versioned contract loader + `SIM-A1-001` synthetic fixture + idempotent `seed_a1_reference_fixture`).
3. **STOP and VALIDATE**: Verify `US1` independently via pytest and double-run seeder.

### Incremental B01 Delivery

1. Deliver `US1` (MVP: versioned contract + `SIM-A1-001` fixture).
2. Add `US2` (decision register + authorized `/contract/` endpoint) and `US3` (`C02` zero/unset/not-measured regression).
3. Add `US4` (`C03` canonical shifts, actual durations, bilingual labor metric guard).
4. Add `US5` (`C04` Shiraz 34/32 profile + dedicated Appendix) and `US6` (`C08` official numbering, `WeatherLog` + MET Norway 2.0 adapter, `/contract-summary/` endpoint).
5. Run Phase 9 full `quickstart.md` validation + legacy regression checks.
6. Hand off verified B01 baseline to downstream packages `B02`–`B06` (employer representative & acceptance date remain pending `B06` handoff under `GOV-01`).

## B03 handoff from convergence

Convergence item `T030` remains open under B03. The [B01 contract](./contracts/daily-report-data-contract.v1.json) records both deliverables under `FR-016`, and the [B01 plan](./plan.md) assigns their implementation and output verification to the downstream package.

- `DEL-03` (`C05`) — Implement and verify the multi-sheet date-range Excel workbook.
- `DEL-04` (`C07`) — Implement and verify standalone PDFs for each discipline.

Carry both items into the [B03 workflow](../../output/a1-requirements-2026-11-18/speckit-prompts/03-b03-reference-parity.md) after its B02 prerequisite is satisfied.

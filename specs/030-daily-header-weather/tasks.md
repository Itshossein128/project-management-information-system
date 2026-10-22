---
description: "Task list for Standardized Daily Weather and Temperature implementation"
---

# Tasks: Standardized Daily Weather and Temperature

**Input**: Design documents from `/specs/030-daily-header-weather/`
- Spec: [spec.md](./spec.md)
- Plan: [plan.md](./plan.md)
- Data Model: [data-model.md](./data-model.md)
- API Contract: [contracts/daily-report-header-weather-api.md](./contracts/daily-report-header-weather-api.md)
- UI Contract: [contracts/daily-report-header-weather-ui.md](./contracts/daily-report-header-weather-ui.md)
- Research: [research.md](./research.md)
- Quickstart & Verification: [quickstart.md](./quickstart.md)

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test-Driven Development (TDD) approach requested. All test tasks must be written first and observed to FAIL before implementing the corresponding features.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- All descriptions include exact file paths and quoted verbatim constraints from data-model.md where applicable

## Path Conventions

- Backend (Django 4.2 + DRF): `apps/api/core/`
- Frontend (React Router 7 + Vite): `apps/web/src/`
- End-to-End Tests (Playwright): `e2e/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test infrastructure initialization, baseline verification, and test environment readiness

- [x] T001 Verify backend test database connectivity and pytest configuration in `apps/api/core/pytest.ini` against PostgreSQL port 5433 and Redis port 6379
- [x] T002 [P] Verify frontend typecheck and node test harness environment in `apps/web/src/app/lib/__tests__/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure, shared vocabulary standardization, data migration verification, and base localization that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete. Legacy weather values must be normalized before new choice restrictions take effect.

- [x] T003 [P] Verify committed migration state and schema consistency in `apps/api/core/field_reports/migrations/0018_daily_header_weather.py` and `apps/api/core/sub_reports/migrations/0004_standardize_weather.py`
- [x] T004 [P] Create migration executor test suite in `apps/api/core/field_reports/tests/test_daily_report_weather_migration.py` verifying legacy normalization (`sunny -> clear`, `partly_cloudy -> cloudy`, `foggy -> cloudy`) across daily reports, weather logs, and specialty reports
- [x] T005 [P] Update dev fixtures in `apps/api/core/projects/seeds/full_project.py` ensuring all sample daily reports and weather logs use only approved weather conditions (`clear`, `cloudy`, `rainy`, `snowy`, `stormy`)
- [x] T006 [P] Update Persian and English base localization catalogs in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json` for the five weather choices, temperature validation error code `temp_max_must_be_gte_temp_min`, and `weather_impact_notes` labels
- [x] T007 [P] Standardize shared weather types and metadata in `apps/web/src/app/lib/api/weather.ts` and `apps/web/src/app/lib/api/daily-reports.ts` with approved vocabulary: `clear`, `cloudy`, `rainy`, `snowy`, `stormy`
- [x] T008 [P] Verify and update offline IndexedDB data upgrade normalization in `apps/web/src/app/lib/offlineDB.ts` and test in `apps/web/src/app/lib/__tests__/offlineDB.test.ts` for `sunny -> clear`, `partly_cloudy -> cloudy`, and `foggy -> cloudy`

**Checkpoint**: Shared vocabulary standardized, legacy data normalized, and schema foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Record one of five standard weather conditions (Priority: P1) 🎯 MVP

**Goal**: An authorized report editor records daily weather using the five official Shiraz-form categories (`clear`, `cloudy`, `rainy`, `snowy`, `stormy`). Reviewers see the standardized value everywhere. Retired values are rejected on new saves. Historical reports are normalized. Derived summary weather selects the highest severity (`stormy > snowy > rainy > cloudy > clear`), ignores blanks/unknowns, resets to `null` if no valid contributors remain, and preserves approved project-level overrides.

**Independent Test**: Save and reopen one report for each approved weather value, try every retired/unknown value, inspect available choices, and reconcile reports with different weather severities.

### Tests for User Story 1 (TDD - Write FIRST, ensure they FAIL before implementation) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Write failing backend contract and model tests in `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` verifying `DailyReport` and `WeatherLog` accept exactly five approved weather values (`clear`, `cloudy`, `rainy`, `snowy`, `stormy`) and reject retired (`sunny`, `partly_cloudy`, `foggy`) or unknown strings with HTTP 400
- [x] T010 [P] [US1] Write failing sub-report compatibility tests in `apps/api/core/sub_reports/tests/test_sub_reports.py` verifying `DisciplineSubReport` accepts the five approved weather choices and rejects retired values
- [x] T011 [P] [US1] Write failing aggregation tests in `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` verifying weather severity hierarchy (`stormy > snowy > rainy > cloudy > clear`), ignoring blanks/unknowns, setting derived weather to `null` when no valid contributors remain, and preserving `weather_override=True`
- [x] T012 [P] [US1] Write failing E2E tests in `e2e/tests/daily-report-header-weather.spec.ts` for US1 verifying the five approved weather choices in exact order, absence of retired choices, radio semantics, and bilingual display in Persian and English

### Implementation for User Story 1

- [x] T013 [P] [US1] Standardize `WeatherCondition` enum choices and labels in `apps/api/core/field_reports/models.py` to `clear` ("آفتابی / صاف"), `cloudy` ("ابری"), `rainy` ("بارانی"), `snowy` ("برفی"), `stormy` ("طوفانی / گرد و غبار") ("nullable shared weather choice", "Non-empty value is one of five")
- [x] T014 [P] [US1] Standardize `DisciplineSubReport.weather_condition` in `apps/api/core/sub_reports/models.py` to use the shared `WeatherCondition` enum
- [x] T015 [US1] Implement deterministic weather aggregation logic in `apps/api/core/field_reports/services/daily_report_aggregation.py` using severity ranking `stormy (50) > snowy (40) > rainy (30) > cloudy (20) > clear (10)`, setting derived weather to `None` when no valid contributors exist and `weather_override=False`, and preserving override when `weather_override=True`
- [x] T016 [US1] Ensure `DailyReportSerializer` in `apps/api/core/field_reports/serializers.py` validates `weather_condition` against approved choices and returns localized `weather_condition_label`
- [x] T017 [P] [US1] Update weather icons and helper mappings in `apps/web/src/components/weather/weather-icons.tsx`, `apps/web/src/components/weather/weather-log-drawer.tsx`, and `apps/web/src/components/weather/weather-log-grid.tsx` for the five approved conditions
- [x] T018 [US1] Implement accessible `WeatherSelector` component in `apps/web/src/components/daily_reports/WeatherSelector.tsx` exposing radio semantics, ordered choices, localized text, and keyboard navigation
- [x] T019 [US1] Integrate `WeatherSelector` into `ReportHeader` in `apps/web/src/components/daily_reports/ReportHeader.tsx`
- [x] T020 [US1] Integrate `WeatherSelector` into the summary metadata editor in `apps/web/src/app/routes/daily-report-view.tsx` replacing hard-coded select options
- [x] T021 [US1] Update daily reports API client in `apps/web/src/app/lib/api/daily-reports.ts` to handle the standardized five weather values and labels

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. The five standard weather choices are enforced across backend, frontend, aggregation, and offline layers.

---

## Phase 4: User Story 2 - Enter valid minimum and maximum temperatures (Priority: P1)

**Goal**: An authorized report editor enters optional minimum and maximum temperatures in Celsius (inclusive `[-40, 60]`). Out-of-range values and reversed pairs (`temp_max < temp_min`) are blocked with field-specific guidance and stable error code `temp_max_must_be_gte_temp_min`. Equal values are accepted. In partial updates, candidate state merges supplied and stored temperatures. The interactive header provides immediate feedback and blocks manual save, autosave, and offline queueing.

**Independent Test**: Enter each boundary (-40, 60), values immediately outside boundaries, maximum below minimum, equal values, and partial updates that change only one temperature.

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL before implementation) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US2] Write failing model validation tests in `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` verifying `DailyReport.full_clean()` enforces inclusive `[-40.0, 60.0]` on `temp_min` and `temp_max`
- [x] T023 [P] [US2] Write failing API serializer tests in `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` verifying candidate-state merge on PATCH, returning HTTP 400 with stable error code `temp_max_must_be_gte_temp_min` attached to `temp_max` when `temp_max < temp_min`, and accepting equal values or nulls
- [x] T024 [P] [US2] Write failing standalone `WeatherLog` temperature validation tests in `apps/api/core/field_reports/tests/test_weather.py` verifying bounds `[-40, 60]` and `temp_max_must_be_gte_temp_min`
- [x] T025 [P] [US2] Write failing client temperature validation unit tests in `apps/web/src/app/lib/__tests__/temperatureValidation.test.ts` verifying numeric parsing, `[-40, 60]` bounds, incomplete tokens, equal values, and `temp_max_must_be_gte_temp_min`
- [x] T026 [P] [US2] Write failing E2E tests in `e2e/tests/daily-report-header-weather.spec.ts` for US2 verifying boundary saves, out-of-bounds rejection, reversed range error display attached to `temp_max`, and save/autosave blocking

### Implementation for User Story 2

- [x] T027 [US2] Enforce decimal range validators `MinValueValidator(Decimal('-40.0'))` and `MaxValueValidator(Decimal('60.0'))` on `temp_min` and `temp_max` ("decimal with one fractional digit", "Inclusive -40..60 Celsius") in `apps/api/core/field_reports/models.py`
- [x] T028 [US2] Implement effective-state candidate validation in `DailyReportSerializer.validate()` in `apps/api/core/field_reports/serializers.py` merging incoming PATCH data with instance values and raising `ValidationError` with code `temp_max_must_be_gte_temp_min` attached to `temp_max` ("when both are known, temp_max >= temp_min")
- [x] T029 [US2] Create shared pure temperature validation helper in `apps/web/src/app/lib/temperatureValidation.ts` distinguishing blank optional values, incomplete in-focus tokens, out-of-range bounds, and reversed pairs
- [x] T030 [US2] Implement inline temperature validation and field error display with `aria-describedby` and `aria-invalid` in `apps/web/src/components/daily_reports/ReportHeader.tsx`
- [x] T031 [US2] Implement inline temperature validation and structured error mapping consuming `ApiRequestError.code` and details in `apps/web/src/app/routes/daily-report-view.tsx`
- [x] T032 [US2] Gate manual form submission, debounced autosave, and offline queueing on temperature validation in `apps/web/src/components/daily_reports/DailyReportForm.tsx` and `apps/web/src/app/lib/offlineWrite.ts`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Temperature bounds and ordering are strictly guarded on both server and client without premature autosave fires.

---

## Phase 5: User Story 3 - Preserve weather impacts in the official record (Priority: P2)

**Goal**: An authorized report editor enters optional multi-line `weather_impact_notes` describing weather effects on work fronts, delays, or productivity. The notes are preserved across detail readback, summary rebuilds, correction copies, and sync batches. In the official daily-report PDF, an unconditional table row labeled «توضیحات و اثرات شرایط جوی» reproduces the exact notes, or renders an empty cell when empty without fabricated placeholders.

**Independent Test**: Save multi-line Persian and English notes, reopen the report, inspect header/detail views, rebuild summary, copy correction, and verify the generated PDF contains the exact text and unconditional label. Repeat with an empty note.

### Tests for User Story 3 (TDD - Write FIRST, ensure they FAIL before implementation) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T033 [P] [US3] Write failing backend persistence and rebuild tests in `apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py` verifying `weather_impact_notes` preserves Persian, English, and multi-line strings on GET and PATCH, defaults to empty string `""`, and is never overwritten during daily report summary rebuilds
- [x] T034 [P] [US3] Write failing correction copy and sync comparison tests in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` and `apps/api/core/field_reports/tests/test_sync_batch.py` verifying `weather_impact_notes` is copied across report versions and included in sync batch payloads
- [x] T035 [P] [US3] Write failing PDF export tests in `apps/api/core/field_reports/tests/test_daily_report_pdf.py` verifying unconditional header row labeled «توضیحات و اثرات شرایط جوی», rendering plain text with line breaks preserved (including escaping `&` and `<`), and rendering empty cell when note is blank
- [x] T036 [P] [US3] Write failing E2E tests in `e2e/tests/daily-report-header-weather.spec.ts` for US3 verifying note entry, hydration on reload, read-only display, and PDF download verification

### Implementation for User Story 3

- [x] T037 [US3] Ensure `weather_impact_notes` field on `DailyReport` in `apps/api/core/field_reports/models.py` is configured as `models.TextField(blank=True, default='')` ("plain multi-line text", "blank, default ''")
- [x] T038 [US3] Ensure `DailyReportSerializer` in `apps/api/core/field_reports/serializers.py` exposes `weather_impact_notes` in read and write fields with empty representation as `""`
- [x] T039 [US3] Update correction service in `apps/api/core/field_reports/services/correction_service.py` to copy `weather_impact_notes` when creating report corrections/versions
- [x] T040 [US3] Update daily report summary aggregation in `apps/api/core/field_reports/services/daily_report_aggregation.py` to preserve existing `weather_impact_notes` untouched during summary rebuilds
- [x] T041 [US3] Update PDF generator in `apps/api/core/field_reports/pdf.py` to unconditionally render header-table row labeled «توضیحات و اثرات شرایط جوی», escaping plain text, preserving line breaks, and rendering an empty cell when note is blank
- [x] T042 [US3] Add multi-line `weather_impact_notes` textarea with `dir="auto"`, localization, and accessible label in `apps/web/src/components/daily_reports/ReportHeader.tsx`
- [x] T043 [US3] Add multi-line `weather_impact_notes` control with `dir="auto"` and bilingual label in the summary metadata editor in `apps/web/src/app/routes/daily-report-view.tsx`
- [x] T044 [US3] Fix `headerFromDetail` in `apps/web/src/components/daily_reports/DailyReportForm.tsx` to initialize `weather_impact_notes` from `report.weather_impact_notes ?? ""` before autosave runs to prevent accidental note erasure
- [x] T045 [US3] Update offline sync in `apps/web/src/app/lib/syncService.ts` and `apps/web/src/app/lib/offlineWrite.ts` to include `weather_impact_notes` in cached reports, mutation payloads, and conflict resolution

**Checkpoint**: All three user stories are now independently functional and verified end-to-end. Weather impacts are reliably captured and printed in the official Shiraz PDF layout.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: System documentation, dead code audit, regression verification, and final compliance check

- [x] T046 [P] Update API documentation in `apps/api/core/field_reports/ENDPOINTS.md` and `apps/api/core/sub_reports/ENDPOINTS.md` documenting the five approved weather values, temperature validation rules, error code `temp_max_must_be_gte_temp_min`, and `weather_impact_notes`
- [x] T047 [P] Audit codebase for retired weather strings (`sunny`, `partly_cloudy`, `foggy`) with grep across `apps/web/src/` and `apps/api/core/` to ensure no retired value is used as an active option or default
- [x] T048 Run full backend test suite in `apps/api/core` via `pytest field_reports/tests sub_reports/tests -q` and `python manage.py verify_blueprint_schema`
- [x] T049 Run frontend typecheck via `pnpm typecheck` and offline unit tests via `node --test --experimental-strip-types apps/web/src/app/lib/__tests__/offlineDB.test.ts` and `apps/web/src/app/lib/__tests__/temperatureValidation.test.ts`
- [x] T050 Run full E2E test suite in `e2e/tests/daily-report-header-weather.spec.ts` with Playwright across `chromium-desktop` and `mobile-chrome` projects
- [x] T051 Execute quickstart verification workflow per `specs/030-daily-header-weather/quickstart.md` and compile final verification evidence report

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Depends on Phase 2
  - User Story 2 (P1): Depends on Phase 2; can proceed in parallel with US1 or sequentially
  - User Story 3 (P2): Depends on Phase 2; integrates with US1/US2 header state
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent increment delivering the five-value weather standard
- **User Story 2 (P1)**: Independent increment delivering temperature range & cross-field bounds
- **User Story 3 (P2)**: Independent increment delivering weather impact notes and PDF parity

### Within Each User Story

1. Tests MUST be written FIRST and observed to FAIL before implementation begins
2. Model changes / validators before service changes
3. Service logic (aggregation, correction) before serializers / views
4. Shared UI components before page-level integration
5. Form hydration and autosave protection before end-to-end verification

### Parallel Opportunities

- In **Phase 1**: T001 and T002 can run in parallel
- In **Phase 2**: T003, T004, T005, T006, T007, T008 can all run in parallel
- In **Phase 3 (US1)**: Test tasks T009, T010, T011, T012 can run in parallel; implementation tasks T013, T014, T017 can run in parallel
- In **Phase 4 (US2)**: Test tasks T022, T023, T024, T025, T026 can run in parallel
- In **Phase 5 (US3)**: Test tasks T033, T034, T035, T036 can run in parallel
- In **Phase 6**: T046 and T047 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch test tasks for User Story 1 in parallel:
Task T009: "Write failing backend contract and model tests in apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py"
Task T010: "Write failing sub-report compatibility tests in apps/api/core/sub_reports/tests/test_sub_reports.py"
Task T011: "Write failing aggregation tests in apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py"
Task T012: "Write failing E2E tests in e2e/tests/daily-report-header-weather.spec.ts"

# Launch model & icon tasks for User Story 1 in parallel:
Task T013: "Standardize WeatherCondition enum choices and labels in apps/api/core/field_reports/models.py"
Task T014: "Standardize DisciplineSubReport.weather_condition in apps/api/core/sub_reports/models.py"
Task T017: "Update weather icons and helper mappings in apps/web/src/components/weather/weather-icons.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch test tasks for User Story 2 in parallel:
Task T022: "Write failing model validation tests in apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py"
Task T023: "Write failing API serializer tests in apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py"
Task T024: "Write failing standalone WeatherLog temperature validation tests in apps/api/core/field_reports/tests/test_weather.py"
Task T025: "Write failing client temperature validation unit tests in apps/web/src/app/lib/__tests__/temperatureValidation.test.ts"
Task T026: "Write failing E2E tests in e2e/tests/daily-report-header-weather.spec.ts"
```

---

## Parallel Example: User Story 3

```bash
# Launch test tasks for User Story 3 in parallel:
Task T033: "Write failing backend persistence and rebuild tests in apps/api/core/field_reports/tests/test_spec_01_daily_header_weather.py"
Task T034: "Write failing correction copy and sync comparison tests in apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py"
Task T035: "Write failing PDF export tests in apps/api/core/field_reports/tests/test_daily_report_pdf.py"
Task T036: "Write failing E2E tests in e2e/tests/daily-report-header-weather.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently (weather choices, rejection, severity ranking)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently (temperatures bounded, ordered, client gated) → Deploy/Demo
4. Add User Story 3 → Test independently (notes preserved, unconditional PDF row rendered) → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Weather vocabulary & aggregation)
   - Developer B: User Story 2 (Temperature validation & immediate feedback)
   - Developer C: User Story 3 (Weather impact notes & PDF row)
3. Stories complete and integrate independently

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Phase 7: Convergence

- [x] T052 Add the same `testInfo.project.name === "pwa-offline"` skip guard (documented reason: "Requires the dev server", matching `navigation.spec.ts` and `role-localization.spec.ts`) or an offline-capable variant to `e2e/tests/daily-report-header-weather.spec.ts` so the default full-suite Playwright run exits 0 across all three projects, then rerun `pnpm exec playwright test e2e/tests/daily-report-header-weather.spec.ts` and confirm the 5 `pwa-offline` executions no longer fail at `page.goto` per T050 (partial)

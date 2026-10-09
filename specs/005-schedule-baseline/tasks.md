---
description: "Task list for Schedule & Baseline Gap Closure (FR-SCH)"
---

# Tasks: Schedule & Baseline Gap Closure

**Input**: Design documents from `/specs/005-schedule-baseline/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: existing `schedule` + `projects.Activity` / `ActivityRelation`; soft-delete/audit (002); WBS packages (004)

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002–004). Implemented via `/speckit-implement` (TDD).

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 maps to spec user stories
- Exact file paths required

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm baseline schedule APIs and scaffold test/i18n stubs

- [X] T001 Verify existing activity CRUD, relation cycle reject, Gantt baseline compare, and `BaselineSchedule`/`BaselineActivity` in `apps/api/core/schedule/` and `apps/api/core/projects/models.py` (smoke read of ENDPOINTS.md + services)
- [X] T002 [P] Create placeholder test modules `apps/api/core/schedule/tests/test_working_calendars.py`, `test_activity_forecast_and_validation.py`, `test_baseline_lock.py`, `test_schedule_change_request.py`, `test_schedule_status_and_critical_validity.py`
- [X] T003 [P] Add i18n stub keys for forecast dates, milestone, calendar, baseline lock, change request statuses, critical-path-not-valid, and schedule status labels under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema and routing hooks all stories need

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing model/serializer expectations for `WorkingCalendar` (name, is_default, work_monday…work_sunday), `CalendarException` (exception_date, is_working, unique calendar+date), and Activity fields `duration_days` (Integer null), `is_milestone` (Bool default False), `forecast_start`/`forecast_finish` (Date null), `working_calendar` FK null in `apps/api/core/schedule/tests/test_working_calendars.py` and `test_activity_forecast_and_validation.py`
- [X] T005 [P] Write failing expectations for `BaselineSchedule.is_locked` (Bool default False), `locked_at`, `locked_by` FK User null, `source_change_request` FK null in `apps/api/core/schedule/tests/test_baseline_lock.py`

### Implementation

- [X] T006 Add `WorkingCalendar` and `CalendarException` models per `data-model.md` (CalendarException unique `(calendar, exception_date)` among non-deleted; soft-delete/audit) in `apps/api/core/schedule/models.py` + migration
- [X] T007 Add Activity fields on `projects.Activity` in `apps/api/core/projects/models.py`: `duration_days` Integer null, `is_milestone` Bool default False, `forecast_start`/`forecast_finish` Date null, `working_calendar` FK to WorkingCalendar null + migration
- [X] T008 Extend `BaselineSchedule` in `apps/api/core/schedule/models.py` with `is_locked` Bool default False, `locked_at` DateTime null, `locked_by` FK User null, `source_change_request` FK null (defer FK to ScheduleChangeRequest if circular — use SET_NULL nullable and wire after US3 model, or string reference) + migration
- [X] T009 Register URL stubs under `apps/api/core/schedule/urls.py` for `working-calendars/`, `baselines/`, `schedule-change-requests/`, `schedule-status/` (can 501 until story wires views)
- [X] T010 Re-run T004–T005 until PASS for schema/serializer smoke (views may still be incomplete)

**Checkpoint**: Shared schema + route mounts ready

---

## Phase 3: User Story 1 - Activity calendar, duration, forecast (Priority: P1) 🎯 MVP

**Goal**: Working calendars; duration/milestone; distinct forecast dates; impossible-date and non-working-day rejection

**Independent Test**: Create default calendar; two FS-linked activities with forecast; zero-duration milestone; reject finish&lt;start and non-working planned start

### Tests for User Story 1

- [X] T011 [P] [US1] Failing API tests for calendar CRUD + exceptions per `contracts/working-calendars.md` in `apps/api/core/schedule/tests/test_working_calendars.py`
- [X] T012 [P] [US1] Failing tests: activity create/PATCH persists `forecast_*` without clearing planned/actual; milestone `is_milestone=true` + `duration_days=0` allowed; `impossible_planned_dates` / `impossible_forecast_dates` / `non_working_day` / `invalid_milestone` in `apps/api/core/schedule/tests/test_activity_forecast_and_validation.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement calendar service (default uniqueness: at most one `is_default` per project; soft-delete `calendar_in_use` if activities reference) in `apps/api/core/schedule/services/calendar_service.py`
- [X] T014 [US1] Implement working-day resolver (weekday flags + exceptions) in `apps/api/core/schedule/services/calendar_service.py`
- [X] T015 [US1] Implement activity date validation (finish≥start; milestone rules; calendar working days; resolve null calendar → project default) in `apps/api/core/schedule/services/activity_validation.py` (or extend `activity_service.py`)
- [X] T016 [US1] Serializers + views for working calendars/exceptions per contract in `apps/api/core/schedule/serializers.py` and new/extended views; wire URLs; permissions `view_activities`/`edit_activities`
- [X] T017 [US1] Extend activity serializers/views in `apps/api/core/schedule/serializers.py` / `activity_views.py` to expose and validate new fields per `contracts/activities-extended.md`
- [X] T018 [P] [US1] UI: calendar management + activity form fields (duration, milestone, forecast, calendar) on `apps/web/src/app/routes/project-activities.tsx` and API client `apps/web/src/app/lib/api/activities.ts` (or new `schedule-calendars.ts`)
- [X] T019 [US1] Re-run T011–T012 until PASS

**Checkpoint**: US1 independently verifiable

---

## Phase 4: User Story 2 - Lock approved baseline (Priority: P1)

**Goal**: Approve-lock baseline; live edits never rewrite locked snapshots; prior versions retained

**Independent Test**: Approve-lock → PATCH live planned dates → `BaselineActivity` unchanged; PATCH locked snapshot → `baseline_locked`

### Tests for User Story 2

- [X] T020 [P] [US2] Failing tests: `POST .../baselines/{id}/approve-lock/` sets `is_locked`, `is_current`, approved/locked audit fields; demotes prior current but keeps row in `apps/api/core/schedule/tests/test_baseline_lock.py`
- [X] T021 [P] [US2] Failing tests: after lock, live activity PATCH leaves snapshot dates unchanged; mutating locked `BaselineActivity` returns `baseline_locked` in same module

### Implementation for User Story 2

- [X] T022 [US2] Implement baseline list/create-snapshot and `approve_lock_baseline` in `apps/api/core/schedule/services/baseline_service.py` per `contracts/baselines-and-change-requests.md`
- [X] T023 [US2] Guard all BaselineActivity create/update/delete when parent `is_locked` (except system snapshot create) in baseline service + any existing write paths
- [X] T024 [US2] Wire baseline views/serializers/URLs in `apps/api/core/schedule/` with `view_activities`/`edit_activities`; include `is_locked` on Gantt baselines list in `apps/api/core/schedule/gantt_views.py`
- [X] T025 [P] [US2] UI: baseline list + approve-lock action on schedule/Gantt UI (`apps/web/src/app/routes/project-schedule-gantt.tsx` or activities route) + API client
- [X] T026 [US2] Re-run T020–T021 until PASS

**Checkpoint**: US2 independently verifiable

---

## Phase 5: User Story 3 - Schedule change request (Priority: P1)

**Goal**: Draft→submit→approve/reject; approve applies items, creates new locked baseline, retains prior

**Independent Test**: Locked baseline → change request with impacts → approve → new current locked version; prior locked retained; second submit while in-flight → `schedule_change_in_flight`

### Tests for User Story 3

- [X] T027 [P] [US3] Failing tests: submit requires non-empty `reason`, `milestone_impact`, `cost_impact`, `contract_impact`; only one `submitted` per project in `apps/api/core/schedule/tests/test_schedule_change_request.py`
- [X] T028 [P] [US3] Failing tests: approve applies `ScheduleChangeItem` proposed dates to live activities (with US1 validation), creates new locked current baseline with `source_change_request`, prior remains `is_locked=true` `is_current=false`; reject creates no baseline in same module

### Implementation for User Story 3

- [X] T029 [US3] Add `ScheduleChangeRequest` (status enum `draft`/`submitted`/`approved`/`rejected`; impact text fields; base/resulting baseline FKs; decided_* audit) and `ScheduleChangeItem` (proposed planned/forecast/duration fields nullable) in `apps/api/core/schedule/models.py` + migration; finalize `BaselineSchedule.source_change_request` FK if deferred
- [X] T030 [US3] Implement change-request lifecycle service (create/update draft, submit, approve transactional, reject) in `apps/api/core/schedule/services/change_request_service.py`
- [X] T031 [US3] Wire serializers/views/URLs per `contracts/baselines-and-change-requests.md` under `apps/api/core/schedule/`
- [X] T032 [P] [US3] UI: change-request list/drawer (impacts + line items + submit/approve/reject) in `apps/web/src/components/schedule/` + route hook from project schedule nav
- [X] T033 [US3] Re-run T027–T028 until PASS

**Checkpoint**: US3 independently verifiable

---

## Phase 6: User Story 4 - Milestone/delay report & critical-path validity (Priority: P2)

**Goal**: Schedule status report with four-way dates; critical path empty + not valid when durations incomplete

**Independent Test**: Complete durations → milestones/delays/forecast finish; strip duration → `critical_path.valid=false` and empty critical ID arrays

### Tests for User Story 4

- [X] T034 [P] [US4] Failing tests for `GET .../schedule-status/` shape per `contracts/schedule-status-report.md` in `apps/api/core/schedule/tests/test_schedule_status_and_critical_validity.py`
- [X] T035 [P] [US4] Failing tests: incomplete `duration_days` (and no planned span) → `valid=false`, empty critical/near-critical IDs; complete data may expose flags/float≤5 near-critical in same module
- [X] T036 [P] [US4] Failing/regression: Gantt payload includes critical_path validity object so invalid path is not authoritative in `apps/api/core/schedule/tests/test_gantt.py` (or new assertion file)

### Implementation for User Story 4

- [X] T037 [US4] Implement `evaluate_critical_path_validity` per research D6 in `apps/api/core/schedule/services/critical_path_validity.py`
- [X] T038 [US4] Implement schedule status aggregator (milestones, delays, forecast_project_finish, date_sets) in `apps/api/core/schedule/services/status_report_service.py`
- [X] T039 [US4] Wire `GET .../schedule-status/` view + OpenAPI; embed validity on `GET .../gantt/` in `apps/api/core/schedule/gantt_views.py` / `gantt_service.py`
- [X] T040 [P] [US4] UI: new route `apps/web/src/app/routes/project-schedule-status.tsx` with four distinct date columns + not-valid critical banner; add nav entry
- [X] T041 [US4] Re-run T034–T036 until PASS

**Checkpoint**: All stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T042 [P] Update `apps/api/core/schedule/ENDPOINTS.md` with calendars, baselines, change requests, schedule-status
- [X] T043 [P] drf-spectacular summaries/tags on new endpoints
- [X] T044 [P] Verification checklist `specs/005-schedule-baseline/checklists/verification.md` mapping SC-001–SC-005 to tests
- [X] T045 Run quickstart smoke commands from `specs/005-schedule-baseline/quickstart.md` and record evidence categories (pytest vs typecheck vs UI)
- [X] T046 [P] Confirm MSP/P6 import still creates baselines; document unlock-then-approve-lock expectation in ENDPOINTS.md (no silent locked overwrite)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** → no deps
- **Phase 2 Foundational** → after Setup; **blocks** all stories
- **US1 (Phase 3)** → after Foundational (MVP)
- **US2 (Phase 4)** → after Foundational; uses lock fields; independently testable without change requests
- **US3 (Phase 5)** → after Foundational; **practically after US2** (approve path needs lock + snapshot create); may reuse US1 validation on apply
- **US4 (Phase 6)** → after Foundational; **practically after US1** (forecast/duration fields); benefits from US2 baseline for approved dates
- **Polish** → after desired stories

### User Story Dependencies

```text
Foundational
 ├── US1 (calendar / forecast / validation)  ← MVP
 ├── US2 (baseline lock)
│     └── US3 (change request → new locked baseline)
└── US4 (status report / validity) ← needs US1 fields; optional US2 for baseline_finish
```

### Parallel Opportunities

- T002/T003; T004/T005; T011/T012; T020/T021; T027/T028; T034/T035/T036
- After Foundational: US1 and US2 can proceed in parallel if staffed
- US3 waits on US2 lock/approve-lock service
- US4 can start once US1 fields land (mock baseline_finish if US2 incomplete)

### Parallel Example: User Story 1

```bash
# Tests in parallel:
Task: T011 calendar API tests
Task: T012 activity forecast/validation tests

# After services:
Task: T016 calendar views
Task: T018 UI activity/calendar forms  # [P] different files from serializers if careful
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + 2  
2. Phase 3 US1  
3. **STOP** — validate SC-001 date separation + calendar validation  
4. Demo activities with forecast/milestone/calendar

### Incremental Delivery

1. US1 → calendars + forecast  
2. US2 → baseline lock (SC-002)  
3. US3 → change requests (SC-003)  
4. US4 → status report + validity (SC-004/SC-005)  
5. Polish + quickstart evidence

### Suggested MVP scope

**US1 only** (T001–T019): delivers FR-SCH-001/003/004 gap closure without waiting on change-request workflow.

---

## Notes

- Do **not** implement until `/speckit-implement` (or explicit user request)
- Reuse `view_activities` / `edit_activities` — no new permission codes in v1
- Near-critical default: total float ≤ 5 days when float available and path valid
- Live activity PATCH must never mutate locked `BaselineActivity` rows
- All tasks use checklist format with IDs and file paths

---

## Phase 8: Convergence

Remaining gaps found by `/speckit-converge` against spec/plan/tasks/constitution after implement. Do not renumber prior tasks.

- [X] T047 CRITICAL: Migrate `BaselineSchedule` (and decide snapshot `BaselineActivity`) to soft-delete + audit fields and block hard-delete of locked/approved baseline history in `apps/api/core/schedule/models.py` per FR-009 / Constitution II–IV (contradicts)
- [X] T048 Add WorkingCalendar management UI (list/create/update/soft-delete + exceptions) wired to `apps/web/src/app/lib/api/schedule.ts` and calendar API; keep activity drawer select as assignment only (`apps/web/src/components/schedule/` or activities route) per T018 / plan Structure / SC-001 (partial)
- [X] T049 Gate `get_activity_network` critical flags via `evaluate_critical_path_validity` (empty IDs + not-valid when incomplete) in `apps/api/core/schedule/services/activity_service.py` and ensure network UI respects validity per FR-008 / US4 (partial)
- [X] T050 Require `duration_days=0` whenever `is_milestone=true` (reject null) in `apps/api/core/schedule/services/activity_validation.py` and cover in `test_activity_forecast_and_validation.py` per FR-001 / US1 (partial)
- [X] T051 [P] Replace hardcoded Persian labels on `apps/web/src/app/routes/project-schedule-status.tsx` and `project-schedule-gantt.tsx` with fa/en i18n keys per Constitution III (partial)

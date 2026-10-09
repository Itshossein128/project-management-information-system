---
description: "Task list for Physical Progress & Periodic Reports Gap Closure (FR-PRG)"
---

# Tasks: Physical Progress & Periodic Reports Gap Closure

**Input**: Design documents from `/specs/009-progress-periodic-reports/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: existing Sprint 6 progress (`schedule.ActivityProgress`, progress dashboard/S-curve); daily-report approve→recalc (`field_reports`); WBS/activities (004/005); soft-delete/audit (002)

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002–007). Implemented via `/speckit-implement` (TDD). **Do not implement** until `/speckit-implement` is requested.

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 maps to spec user stories
- Exact file paths required

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm progress baseline and scaffold test/i18n stubs

- [X] T001 Verify existing progress ViewSets, `ActivityProgress` model, manual entry clamp behavior, daily-report recalc path, and ENDPOINTS in `apps/api/core/schedule/` (`models.py`, `progress_views.py`, `services/progress_service.py`, `ENDPOINTS.md`) and `apps/api/core/field_reports/tasks.py`
- [X] T002 [P] Create placeholder test modules `apps/api/core/schedule/tests/test_measurement_methods.py`, `test_progress_four_way.py`, `test_progress_validation.py`, `test_period_reports.py`
- [X] T003 [P] Add i18n stub keys for measurement methods, four-way progress labels (period/cumulative/planned/approved), incomplete basis, progress_exceeds_100, photo≠approval, weekly/monthly report sections, not_recorded, figure override under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema for measurement + progress extensions + period-report mounts all stories need

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing expectations for `ActivityMeasurementDefinition` fields per `data-model.md` (`method` in `quantity|weighted_milestones|evidence_percent`, `status` in `draft|approved`, total_quantity/unit nullable, milestones JSON/children, evidence_rules, current_version FK null, approved_at/by) in `apps/api/core/schedule/tests/test_measurement_methods.py`
- [X] T005 [P] Write failing expectations for `ActivityMeasurementVersion` (version_number monotonic, method copy, basis_snapshot JSON, change_reason required when not first) and `ActivityQuantityChange` (`status` draft|approved|rejected, previous_total/new_total, reason) in same module
- [X] T006 [P] Write failing expectations for additive `ActivityProgress` fields: `period_progress` Decimal null, `approved_progress` Decimal null, `measurement_version` FK null, `technical_approved_at`/`technical_approved_by` null, `evidence_refs` JSON blank in `apps/api/core/schedule/tests/test_progress_four_way.py`
- [X] T007 [P] Write failing expectations for `ProjectPeriodReport` (`kind` weekly|monthly, period_start/end, `status` generated|superseded, generated_at/by, superseded_by) and `PeriodReportFigure` (`value_status` recorded|not_recorded, source_type/id/path, source_approved, last_updated_at) + `PeriodReportFigureOverride` (reason required) in `apps/api/core/schedule/tests/test_period_reports.py`

### Implementation

- [X] T008 Add `ActivityMeasurementDefinition`, `ActivityMeasurementVersion`, `ActivityQuantityChange` models per `data-model.md` in `apps/api/core/schedule/models.py` + migration
- [X] T009 Extend `ActivityProgress` with period/approved/measurement_version/technical_approved/evidence_refs fields in `apps/api/core/schedule/models.py` + migration; keep existing unique `(activity, report_date)`
- [X] T010 Add `ProjectPeriodReport`, `PeriodReportFigure`, `PeriodReportFigureOverride` models per `data-model.md` in `apps/api/core/schedule/models.py` + migration; unique one non-superseded report per `(project, kind, period_start, period_end)`
- [X] T011 [P] Register URL stubs under `apps/api/core/schedule/urls.py` for measurement, quantity-changes, technical-approve, progress-reports per `contracts/`; outline in `apps/api/core/schedule/ENDPOINTS.md` (views may 501 until stories wire)
- [X] T012 Re-run T004–T007 until PASS for schema smoke in `apps/api/core/schedule/tests/test_measurement_methods.py`, `test_progress_four_way.py`, `test_period_reports.py` (views may still be incomplete)

**Checkpoint**: Shared schema + route mounts ready

---

## Phase 3: User Story 1 - Record progress with approved measurement method (Priority: P1) 🎯 MVP

**Goal**: Select/approve measurement method; record period progress linked to WBS+method; reject >100% without quantity change; photo alone ≠ technical approval; block incomplete milestone basis

**Independent Test**: Approve quantity method + total/unit; record period progress; see cumulative + version link; >100% → 400; photo-only approve denied; incomplete milestones blocked

### Tests for User Story 1

- [X] T013 [P] [US1] Failing API tests for GET/PATCH measurement draft, POST approve, incomplete_measurement_basis on bad milestones/missing total per `contracts/measurement-methods.md` in `apps/api/core/schedule/tests/test_measurement_methods.py`
- [X] T014 [P] [US1] Failing tests: progress write without approved measurement → `measurement_not_approved`; manual/recalc >100% without approved quantity change → `progress_exceeds_100` (no 200 clamp); quantity-change approve allows exceed old 100% up to new total per `contracts/progress-validation.md` in `apps/api/core/schedule/tests/test_progress_validation.py`
- [X] T015 [P] [US1] Failing tests: technical-approve without auth path / photo-only → `photo_not_technical_approval` or equivalent; approved daily recalc advances approved_progress only when rules met in `apps/api/core/schedule/tests/test_progress_validation.py` (and/or field_reports recalc test)

### Implementation for User Story 1

- [X] T016 [US1] Implement `measurement_service.py` (draft, approve→Version, change start, quantity-change approve) in `apps/api/core/schedule/services/measurement_service.py`
- [X] T017 [US1] Wire measurement + quantity-change serializers/views/URLs per `contracts/measurement-methods.md` in `apps/api/core/schedule/`
- [X] T018 [US1] Update `progress_service.py` + manual progress view: require approved measurement; store `measurement_version_id`; compute period/cumulative; **reject** >100% (`progress_exceeds_100`) instead of clamp in `apps/api/core/schedule/services/progress_service.py` and `progress_views.py`
- [X] T019 [US1] Update daily-report recalc in `apps/api/core/field_reports/tasks.py` to honor measurement gate + reject>100 semantics; add technical-approve endpoint per `contracts/progress-four-way.md`
- [X] T020 [P] [US1] UI: measurement method picker/approve status on activity or progress page; manual drawer shows validation errors; photo not treated as approve in `apps/web/src/components/progress/` + `apps/web/src/app/lib/api/progress.ts` (+ activity API if needed)
- [X] T021 [US1] Re-run T013–T015 until PASS in `apps/api/core/schedule/tests/test_measurement_methods.py` and `test_progress_validation.py`

**Checkpoint**: US1 independently verifiable (SC-001 / SC-003)

---

## Phase 4: User Story 2 - Four-way progress display (Priority: P1)

**Goal**: Progress API/UI show period, cumulative, planned, approved as four distinct labeled values; unapproved recorded ≠ approved

**Independent Test**: GET activities progress with period window; assert four fields present and unequal when states differ; UI labels visible

### Tests for User Story 2

- [X] T022 [P] [US2] Failing contract tests for progress list/snapshot additive fields `period_progress_pct`, `cumulative_progress_pct`, `planned_progress_pct`, `approved_progress_pct`, measurement_* per `contracts/progress-four-way.md` in `apps/api/core/schedule/tests/test_progress_four_way.py`
- [X] T023 [P] [US2] Failing test: recorded-but-unapproved progress leaves `approved_progress_pct` unchanged / not equal to period or cumulative recorded in same module

### Implementation for User Story 2

- [X] T024 [US2] Extend progress serializers/views/`progress_service.py` to compute and return four-way fields for interval query params `period_start`/`period_end`
- [X] T025 [P] [US2] UI: four labeled columns/cards on `apps/web/src/app/routes/project-progress.tsx` and `apps/web/src/components/progress/ActivityProgressTable.tsx` (or equivalent); wire API client in `apps/web/src/app/lib/api/progress.ts`
- [X] T026 [US2] Re-run T022–T023 until PASS in `apps/api/core/schedule/tests/test_progress_four_way.py`

**Checkpoint**: US2 independently verifiable (SC-005)

---

## Phase 5: User Story 3 - Weekly & monthly project reports (Priority: P2)

**Goal**: Generate weekly/monthly snapshots with required sections, provenance, not_recorded placeholders, audited overrides (no silent figure edit)

**Independent Test**: Generate weekly with approved dailies; open figure source; figure PATCH without override fails; monthly missing cost → not_recorded

### Tests for User Story 3

- [X] T027 [P] [US3] Failing tests: POST generate weekly/monthly, supersede prior same period, minimum sections present per `contracts/weekly-monthly-reports.md` in `apps/api/core/schedule/tests/test_period_reports.py`
- [X] T028 [P] [US3] Failing tests: each figure has source_type/path + last_updated_at or value_status=not_recorded; POST override requires reason; direct figure mutate → `figure_immutable` in same module

### Implementation for User Story 3

- [X] T029 [US3] Implement `period_report_service.py` compose weekly (critical, next-week plan, barriers, decisions) and monthly (progress, baseline variance, cost, commitments, IPC, risks, forecast) with not_recorded fallbacks in `apps/api/core/schedule/services/period_report_service.py`
- [X] T030 [US3] Serializers + views + URLs for list/detail/generate/overrides per contract; update `ENDPOINTS.md`
- [X] T031 [P] [US3] UI: generate weekly/monthly actions + report viewer with source links and override dialog on progress route or dedicated panel in `apps/web/src/components/progress/` + `apps/web/src/app/lib/api/progress.ts` (or `progress-reports.ts`)
- [X] T032 [US3] Re-run T027–T028 until PASS in `apps/api/core/schedule/tests/test_period_reports.py`

**Checkpoint**: US3 independently verifiable (SC-002 / SC-004)

---

## Phase 6: User Story 4 - Measurement method versioning (Priority: P2)

**Goal**: Method change creates version pending approval; history keeps prior method on old progress; draft/rejected does not govern new writes

**Independent Test**: Change method with reason → approve → old progress retains prior version_id; new progress uses new version; rejected change ignored

### Tests for User Story 4

- [X] T033 [P] [US4] Failing tests: POST measurement/change requires reason; approve creates Version N+1; historical ActivityProgress.measurement_version unchanged; draft/rejected change does not apply to new writes per `contracts/measurement-methods.md` in `apps/api/core/schedule/tests/test_measurement_methods.py`

### Implementation for User Story 4

- [X] T034 [US4] Complete change lifecycle in `measurement_service.py` (pending draft while prior approved version remains current for writes until approve)
- [X] T035 [US4] Wire change/approve endpoints + permission checks in `apps/api/core/schedule/` views/urls; ensure progress writes in `progress_service.py` always stamp current approved version only
- [X] T036 [P] [US4] UI: method change request + reason + pending badge in `apps/web/src/components/progress/` (and/or activity drawer); locales already stubbed in `apps/web/src/app/locales/`
- [X] T037 [US4] Re-run T033 until PASS in `apps/api/core/schedule/tests/test_measurement_methods.py`

**Checkpoint**: US4 independently verifiable (FR-011)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, regressions, quickstart validation

- [X] T038 [P] Finalize `apps/api/core/schedule/ENDPOINTS.md` for measurement, four-way progress, validation codes, progress-reports (distinct from inventory weekly PDF)
- [X] T039 [P] Confirm fa/en strings for all new errors/labels; no English-only user messages on touched paths in `apps/web/src/app/locales/`
- [X] T040 Regression: existing S-curve/KPI/history tests still pass under `apps/api/core/schedule/tests/test_progress.py` (adjust only if clamp removal requires assertion updates)
- [X] T041 Run quickstart scenarios from `specs/009-progress-periodic-reports/quickstart.md` (pytest modules listed there); note evidence categories per Constitution VI
- [X] T042 Mark completed tasks `[X]` in this file as work finishes during `/speckit-implement`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: start immediately
- **Phase 2 Foundational**: after Setup — **blocks all stories**
- **US1 (Phase 3)**: after Foundational — MVP
- **US2 (Phase 4)**: after Foundational; benefits from US1 measurement/approve but display can use fixture-seeded approved fields
- **US3 (Phase 5)**: after Foundational; stronger with US1/US2 data but composable from approved dailies + schedule-status stubs
- **US4 (Phase 6)**: after US1 measurement approve path exists
- **Polish**: after desired stories

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|------------|-------------------------|
| US1 | Foundational | Yes — method + progress write + validation |
| US2 | Foundational (+ US1 preferred) | Yes — four-way read with fixtures |
| US3 | Foundational | Yes — generate with seeded sources |
| US4 | US1 measurement | Yes — version history after US1 |

### Parallel Opportunities

- T002–T003; T004–T007; T013–T015; T022–T023; T027–T028 after prior phase done
- UI tasks marked [P] alongside backend within a story when contracts stable
- US2 UI can proceed in parallel with US1 backend finish if four-way API stubbed

---

## Parallel Example: User Story 1

```bash
# Failing tests in parallel:
Task: "T013 measurement API tests in test_measurement_methods.py"
Task: "T014 progress_exceeds_100 / measurement_not_approved in test_progress_validation.py"
Task: "T015 technical-approve / photo rules in test_progress_validation.py"

# Then sequential service → views → field_reports recalc → UI → re-run until PASS
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1–2  
2. Phase 3 US1 (method + reject >100% + WBS/method link)  
3. **STOP and VALIDATE** via quickstart US1  
4. Then US2 (four-way) for manager UX; US3/US4 next

### Incremental Delivery

1. Setup + Foundational → schema ready  
2. US1 → demo measurable progress integrity  
3. US2 → four-way clarity  
4. US3 → weekly/monthly with provenance  
5. US4 → method change governance  
6. Polish + quickstart evidence

### Suggested MVP scope

**US1 only** (measurement approval gate + period progress + reject >100% + photo≠approval). US2 is the smallest add-on for SC-005.

---

## Notes

- Do **not** implement until `/speckit-implement`
- Do **not** reuse inventory department weekly PDF routes
- Full EVM (13) and portfolio dashboard (16) stay out of scope
- Replace clamp-as-success with reject; update any tests that expected clamp
- [P] = different files, no incomplete deps; every task has checkbox + ID + path

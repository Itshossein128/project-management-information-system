# Tasks: Risk, Quality & Safety

**Input**: Design documents from `/specs/015-risk-quality-safety/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required for every task slice** (user requested). Pattern: write failing pytest (or UI assertion where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = shared score helpers + status/event_type vocabulary + migration skeleton used by all stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/015-risk-quality-safety"` and review `specs/015-risk-quality-safety/plan.md` TDD discipline
- [x] T002 [P] Inventory extension points in `apps/api/core/risk/{models.py,serializers.py,views.py,urls.py,services/matrix_service.py,ENDPOINTS.md}` and UI `apps/web/src/app/{routes/project-risk-register.tsx,lib/api/risk-events.ts}`; note gaps vs `specs/015-risk-quality-safety/research.md`

---

## Phase 2: Foundational — Score helpers & status vocabulary (Blocking)

**Purpose**: Shared composite-score rules (`probability_level` 1–5 × `impact_severity_level` 1–5 → product 1–25; null when either missing) and FR `RiskStatus` / `EventType.ISSUE` vocabulary + migration skeleton. Blocks trustworthy US1–US4 work.

**⚠️ CRITICAL**: No story may invent `composite_score` when a level is missing, or skip status data migration.

### Tests (TDD — write first, must FAIL)

- [x] T003 [P] Write failing unit/pytest: both levels set → score = product; either null → score is `None` (not 0) in `apps/api/core/risk/tests/test_risk_score_and_status.py` per `specs/015-risk-quality-safety/data-model.md` Score rules
- [x] T004 [P] Write failing pytest: incomplete score inputs + omitted status → default status `under_review` via score/status helper in `apps/api/core/risk/tests/test_risk_score_and_status.py`

### Implementation

- [x] T005 Implement `compute_composite_score(probability_level, impact_severity_level) -> int | None` and `default_status_for_incomplete_score(...)` in `apps/api/core/risk/services/score_service.py` (levels constrained to 1–5 when present)
- [x] T006 Add `EventType.ISSUE = 'issue'`, `RiskStatus` choices (`open`, `under_review`, `mitigated`, `closed`, `residual`), and FR fields on `RiskEvent` in `apps/api/core/risk/models.py`: `cause` (text, blank), `consequence` (text, blank), `response` (text, blank), `probability_level` (PositiveSmallInteger 1–5 \| null), `impact_severity_level` (PositiveSmallInteger 1–5 \| null), `composite_score` (PositiveSmallInteger 1–25 \| null), `due_date` (date \| null), `impact_on_quality`/`impact_on_safety`/`impact_on_contract`/`impact_on_liquidity` (bool default False), optional FKs `cost_item` → `cost_control.CostBreakdownNode`, `contract` → `contracts.Contract`, `related_decision_ref` (CharField/UUID null), `related_decision_note` (text blank); replace status choices with `RiskStatus` while keeping barrier display mapping documented
- [x] T007 Create data+schema migration `apps/api/core/risk/migrations/0005_fr_rsk_risk_fields.py`: map `open`→`open`, `in_progress`→`under_review`, `resolved`→`closed`; add new fields; preserve soft-delete
- [x] T008 Add `RiskAction` model in `apps/api/core/risk/models.py` (FK `risk_event` CASCADE, `description` required text, `due_date` date \| null, `owner` FK User \| null, `status` open \| done default open) + migration (same or follow-on `0006_*` if cleaner)
- [x] T009 Re-run `test_risk_score_and_status.py` until green for pure score helpers; existing `apps/api/core/risk/tests/test_risk_register.py` and `test_risk_matrix_unit.py` still collect (may need minimal status-string updates so suite is not broken by migration)

**Checkpoint**: Score + status foundation green; migrations apply; ready for story work

---

## Phase 3: User Story 1 — Register and track risk (Priority: P1) 🎯 MVP

**Goal**: Complete risk register with FR fields, issue as separate `event_type`, impact filters, optional activity/cost/contract/decision links, close-with-open-action warn+acknowledge (FR-001–004, FR-008–010; SC-001–002, SC-005)

**Independent Test**: Create open risk with required FR fields → status to mitigated → link activity → filter by impact; create issue via `event_type=issue` distinguishable from risk; missing level → `composite_score` null

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T010 [P] [US1] Write failing pytest POST risk with both levels → response `composite_score` equals product; GET list `?event_type=risk` returns it in `apps/api/core/risk/tests/test_risk_score_and_status.py` per `specs/015-risk-quality-safety/contracts/risk-issue-register.md`
- [x] T011 [P] [US1] Write failing pytest POST risk with only `probability_level` (or only severity) → `composite_score is None` in `apps/api/core/risk/tests/test_risk_score_and_status.py` (SC-005)
- [x] T012 [P] [US1] Write failing pytest POST `event_type=issue` → appears in `?event_type=issue` and not in risk-only matrix / `?event_type=risk` in `apps/api/core/risk/tests/test_risk_issue_separation.py` (FR-001, SC-002)
- [x] T013 [P] [US1] Write failing pytest impact filter `?impact=quality` (and schedule/cost/safety/contract/liquidity) returns matching risks in `apps/api/core/risk/tests/test_risk_issue_separation.py` (FR-008)
- [x] T014 [P] [US1] Write failing pytest optional same-project links `activity` / `cost_item` / `contract` accepted; cross-project FK rejected in `apps/api/core/risk/tests/test_risk_issue_separation.py` (FR-004)
- [x] T015 [P] [US1] Write failing pytest open `RiskAction` + PATCH `status=closed` without `acknowledge_open_actions` → 400 `open_actions_warning`; with flag true → closed in `apps/api/core/risk/tests/test_risk_score_and_status.py` (FR-009)
- [x] T016 [P] [US1] Write failing pytest FR statuses `open|under_review|mitigated|closed|residual` accepted on risk PATCH in `apps/api/core/risk/tests/test_risk_score_and_status.py` (FR-003)

### Implementation for User Story 1

- [x] T017 [US1] Extend `RiskEventSerializer` / barrier serializer status labels in `apps/api/core/risk/serializers.py` for FR fields, `composite_score` read-only computed via `score_service` on create/update, `acknowledge_open_actions` write-only, `open_actions_count` read-only; validate same-project FKs
- [x] T018 [US1] Extend `RiskEventViewSet` filters (`event_type`, `status`, `impact`, search, dates) and close-acknowledge guard in `apps/api/core/risk/views.py`; ensure matrix uses `event_type=risk` + non-closed FR statuses in `apps/api/core/risk/services/matrix_service.py`
- [x] T019 [US1] Add RiskAction nested or sibling endpoints as needed in `apps/api/core/risk/views.py` and `apps/api/core/risk/urls.py` (minimal: create/list under risk-event or dedicated `/risk-actions/`)
- [x] T020 [US1] Re-run `test_risk_score_and_status.py`, `test_risk_issue_separation.py`, `test_risk_register.py`, `test_risk_matrix_unit.py` until green
- [x] T021 [US1] Frontend types + API client for FR fields/`issue`/impact/`acknowledge_open_actions` in `apps/web/src/app/lib/api/risk-events.ts`; risk vs issue tabs/filters, FR form fields, impact filters, close-acknowledge dialog on `apps/web/src/app/routes/project-risk-register.tsx` (extract `apps/web/src/components/risk/` if needed); i18n in `apps/web/src/app/locales/en.json` and `fa.json`

**Checkpoint**: US1 independently testable — risk + issue register MVP

---

## Phase 4: User Story 2 — Inspection and nonconformity (Priority: P2)

**Goal**: Inspection (plan/request/result) with required WBS + responsible + date; NCR + corrective action with due date linked to inspection (FR-005–006; SC-004)

**Independent Test**: Record failed inspection with NCR + CA due date → all linked to WBS/date; missing inspection date or responsible or WBS → 400

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T022 [P] [US2] Write failing pytest POST inspection without `wbs` or without `responsible_user` or without `inspection_date` → 400 in `apps/api/core/risk/tests/test_inspection_validation.py` (SC-004, FR-006)
- [x] T023 [P] [US2] Write failing pytest POST inspection with wbs + responsible + date → 201 and fields persisted in `apps/api/core/risk/tests/test_inspection_validation.py` per `specs/015-risk-quality-safety/contracts/quality-hse-records.md`
- [x] T024 [P] [US2] Write failing pytest fail inspection → create NCR linked to inspection → create CorrectiveAction with `due_date` + responsible → all linked in `apps/api/core/risk/tests/test_inspection_validation.py` (FR-005)

### Implementation for User Story 2

- [x] T025 [US2] Add models `Inspection` (project, wbs **required**, responsible_user **required**, inspection_date **required**, stage plan\|request\|result, result pass\|fail\|conditional\|pending\|null, description, optional activity), `Nonconformity` (project, inspection FK nullable preferred, wbs, description required, status open\|closed, raised_date required), `CorrectiveAction` (project, nonconformity required, description required, responsible_user \| null, due_date \| null, status open\|done, completed_date \| null) in `apps/api/core/risk/models.py` + migration `apps/api/core/risk/migrations/0007_quality_inspection_ncr.py` (number may vary)
- [x] T026 [US2] Serializers + ViewSets CRUD for inspections/nonconformities/corrective-actions with project tenancy + `view_reports`/`edit_reports` in `apps/api/core/risk/serializers.py` and `apps/api/core/risk/views.py`; wire `apps/api/core/risk/urls.py` per contract paths `/inspections/`, `/nonconformities/`, `/corrective-actions/`
- [x] T027 [US2] Re-run `test_inspection_validation.py` until green
- [x] T028 [US2] Frontend: `apps/web/src/app/lib/api/quality-hse.ts` inspection/NCR/CA clients; capture UI on `apps/web/src/app/routes/project-quality-hse.tsx` (create route + `routeVars.ts` / `routes.ts` / `project-navigation.config.ts`); components under `apps/web/src/components/quality/`; i18n `en.json` / `fa.json`

**Checkpoint**: US2 independently testable — inspection → NCR → CA loop

---

## Phase 5: User Story 3 — Incident, near miss & period report (Priority: P2)

**Goal**: HSE incident/near miss with project + date (WBS optional); project + period quality/safety report (FR-005, FR-007; SC-003)

**Independent Test**: Two HSE events in same month appear in period report; incident without WBS saves; empty period returns empty arrays (not fabricated safety score)

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T029 [P] [US3] Write failing pytest POST `hse-events` kind `incident`/`near_miss` with date + project; WBS optional accepted in `apps/api/core/risk/tests/test_quality_period_report.py` per `contracts/quality-hse-records.md`
- [x] T030 [P] [US3] Write failing pytest two events in October → `GET .../quality-safety/report/?date_from=&date_to=` lists them under `incidents`/`near_misses` with correct `counts` in `apps/api/core/risk/tests/test_quality_period_report.py` per `contracts/quality-safety-period-report.md` (SC-003)
- [x] T031 [P] [US3] Write failing pytest empty period → empty arrays and zero counts (no invented KPIs) in `apps/api/core/risk/tests/test_quality_period_report.py`
- [x] T032 [P] [US3] Write failing pytest period report includes inspections/NCRs in range (seed from US2 models) in `apps/api/core/risk/tests/test_quality_period_report.py`

### Implementation for User Story 3

- [x] T033 [US3] Add `HseEvent` model (`kind` incident\|near_miss, project required, wbs optional, event_date required, description required, severity optional, status open\|closed) in `apps/api/core/risk/models.py` + migration
- [x] T034 [US3] Implement `build_quality_safety_period_report(project_id, date_from, date_to)` in `apps/api/core/risk/services/period_report_service.py` (sections: inspections, nonconformities, corrective_actions, incidents, near_misses, work_permits, trainings — last two empty until US4)
- [x] T035 [US3] Wire HseEvent CRUD + `GET .../quality-safety/report/` in `apps/api/core/risk/views.py` / `urls.py` / serializers
- [x] T036 [US3] Re-run `test_quality_period_report.py` until green
- [x] T037 [US3] Frontend: HSE capture + period report panel on `apps/web/src/app/routes/project-quality-hse.tsx` via `quality-hse.ts`; empty-state i18n (no fake “perfect safety”)

**Checkpoint**: US3 independently testable — HSE + period report

---

## Phase 6: User Story 4 — Work permit & safety training (Priority: P3)

**Goal**: Work permits and safety training records contribute to the same period report (FR-005 P3)

**Independent Test**: Save permit + training in range → both appear in period report sections

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T038 [P] [US4] Write failing pytest POST work-permit with `permit_date` → appears in period report `work_permits` when in range in `apps/api/core/risk/tests/test_quality_period_report.py` (or `test_work_permit_training.py` if split)
- [x] T039 [P] [US4] Write failing pytest POST safety-training with `training_date` + topic → appears in period report `trainings` in same test module

### Implementation for User Story 4

- [x] T040 [US4] Add `WorkPermit` (project, permit_date required, permit_type, responsible_user \| null, description, status active\|closed\|expired) and `SafetyTraining` (project, training_date required, topic required, trainer_or_responsible, attendees_count \| null, description) in `apps/api/core/risk/models.py` + migration
- [x] T041 [US4] CRUD endpoints `/work-permits/`, `/safety-trainings/` in views/serializers/urls; extend `period_report_service.py` to fill those sections
- [x] T042 [US4] Re-run period-report / permit-training tests until green
- [x] T043 [US4] Frontend light forms on `project-quality-hse.tsx` + `quality-hse.ts` clients; i18n

**Checkpoint**: US4 independently testable — permits/training in report

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, matrix polish, locales, full quickstart verification

- [x] T044 [P] Update `apps/api/core/risk/ENDPOINTS.md` for FR risk/issue fields, quality/HSE paths, period report, warning code `open_actions_warning`
- [x] T045 [P] Adapt matrix axes to prefer `probability_level` × `impact_severity_level` when present in `apps/api/core/risk/services/matrix_service.py`; cover with unit assertion in `apps/api/core/risk/tests/test_risk_matrix_unit.py`
- [x] T046 Confirm barrier list/create still works with migrated statuses (label “resolved” ↔ `closed` if needed) in `apps/api/core/risk/tests/test_risk_register.py` and barrier UI paths
- [x] T047 [P] Final locale pass for all new strings in `apps/web/src/app/locales/en.json` and `fa.json`
- [x] T048 Run full quickstart suite from `specs/015-risk-quality-safety/quickstart.md` and record pass/fail evidence
- [x] T049 Mark completed tasks `[x]` in this file as slices land; note any deferred out-of-scope items (daily-report incident merge, workflow decisions, portfolio dashboard)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational — independent of US1 data (shared app only)
- **US3 (Phase 5)**: After Foundational; period report benefits from US2 models for inspection/NCR sections (implement HseEvent first; inspection section tests may follow T025)
- **US4 (Phase 6)**: After US3 period-report service exists (extends same report)
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: No dependency on US2–US4
- **US2 (P2)**: Independent of US1; shares `risk` app
- **US3 (P2)**: Independent HSE path; period report optionally lists US2 entities when present
- **US4 (P3)**: Depends on period-report endpoint from US3

### Within Each User Story

1. Write failing tests → confirm red  
2. Models/migrations → services → serializers/views → re-run green  
3. Frontend after API green for that story  
4. Checkpoint before next priority (or parallel US2 after foundation if staffed)

### Parallel Opportunities

- T003/T004 in parallel (same file OK if coordinated; prefer sequential if conflict)
- T010–T016 US1 tests in parallel (different assertion classes/files)
- T022–T024 US2 tests in parallel
- T029–T032 US3 tests in parallel
- After Foundational: US1 and US2 can proceed in parallel on different files if careful with `models.py` merge
- T044/T045/T047 polish in parallel

---

## Parallel Example: User Story 1

```bash
# Launch US1 failing tests together:
Task: "T010 composite_score product on POST risk"
Task: "T012 issue vs risk separation"
Task: "T013 impact filter"
Task: "T015 close acknowledge"

# After red, implement serializers/views then:
pytest apps/api/core/risk/tests/test_risk_score_and_status.py \
       apps/api/core/risk/tests/test_risk_issue_separation.py -q
```

---

## Parallel Example: User Story 2

```bash
Task: "T022 inspection missing required fields → 400"
Task: "T023 inspection happy path → 201"
Task: "T024 NCR + corrective action chain"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational (CRITICAL)  
3. Phase 3 US1 (TDD)  
4. **STOP and VALIDATE** independent test + SC-001/002/005  
5. Demo risk/issue register

### Incremental Delivery

1. Setup + Foundational  
2. US1 → demo MVP  
3. US2 → inspection/NCR  
4. US3 → HSE + period report  
5. US4 → permits/training  
6. Polish + quickstart

### Parallel Team Strategy

1. Team completes Setup + Foundational together  
2. Dev A: US1 | Dev B: US2 (coordinate `models.py` / migrations)  
3. Then US3 report, then US4 extensions  
4. Shared polish

---

## Notes

- [P] = different files / no incomplete deps  
- Confirm tests **fail** before implementing each slice  
- Daily-report incidents: do **not** merge into period report in v1  
- Decision link: opaque `related_decision_ref` only  
- Commit after each task or logical TDD group when asked  
- Avoid fabricating composite scores or empty-period “perfect safety” metrics

---

## Phase 8: Convergence

**Purpose**: Close gaps found by `/speckit-converge` against current code vs spec/plan/tasks (2026-10-09).

- [x] T050 [US1] Add risk/issue status change UI and close-with-open-actions acknowledge dialog using `updateRiskEvent` in `apps/web/src/app/routes/project-risk-register.tsx` (and `apps/web/src/app/lib/api/risk-events.ts` if needed); i18n in `en.json`/`fa.json` per FR-009 / SC-001 / T021 (partial)
- [x] T051 [US2] Wire nonconformity + corrective-action capture on `apps/web/src/app/routes/project-quality-hse.tsx` via `createNonconformity` / `createCorrectiveAction` in `apps/web/src/app/lib/api/quality-hse.ts` after failed inspection per FR-005 / US2 / T028 (partial)
- [x] T052 [US1] Expose `owner` (user FK) and action text / RiskAction entry on risk create/edit in `apps/web/src/app/routes/project-risk-register.tsx` per FR-002 (partial)
- [x] T053 [US3] Add optional WBS selector on incident/near-miss form in `apps/web/src/app/routes/project-quality-hse.tsx` (WBS recommended edge case) (partial)
- [x] T054 Add barrier list/create regression pytest covering migrated FR statuses (`closed` / legacy normalize) in `apps/api/core/risk/tests/test_risk_register.py` or `test_barriers.py` per T046 (partial)
- [x] T055 Align `AuthUser.id` to UUID string in `apps/web/src/app/lib/auth-types.ts` and ensure inspection `responsible_user` uses that id in `apps/web/src/app/routes/project-quality-hse.tsx` per Constitution III / data integrity (partial)

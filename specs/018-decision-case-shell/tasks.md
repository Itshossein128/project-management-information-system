# Tasks: Decision Support Case Shell (Phase 1)

**Input**: Design documents from `/specs/018-decision-case-shell/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required** (user requested `use TDD`). Pattern for each slice: write failing pytest (or UI assertion where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = Django app skeleton, permissions, `DecisionCase`/`DecisionRun` models + migration + URL mount. No SAW/TOPSIS/AHP/DEMATEL/ISM engines.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and create empty app package layout before TDD slices

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/018-decision-case-shell"` and review TDD discipline in `specs/018-decision-case-shell/plan.md` + `quickstart.md`
- [x] T002 [P] Create empty Django app package layout: `apps/api/core/decision_support/{__init__.py,apps.py,models.py,serializers.py,views.py,urls.py,services/__init__.py,tests/__init__.py,migrations/__init__.py}` and `apps/api/core/decision_support/ENDPOINTS.md` stub listing planned paths from `specs/018-decision-case-shell/contracts/`

---

## Phase 2: Foundational — App registration, permissions, models (Blocking)

**Purpose**: Register app, add `view_decision_support` / `edit_decision_support`, persist `DecisionCase` + `DecisionRun` with field constraints from data-model, mount URLs under project. Blocks all stories.

**⚠️ CRITICAL**: No story may skip project-scoped permissions or invent engines.

### Tests (TDD — write first, must FAIL)

- [x] T003 [P] Write failing pytest: `PERMISSIONS` contains `view_decision_support` and `edit_decision_support`; `project_manager` has both; `viewer` has view in `apps/api/core/decision_support/tests/test_permissions_catalog.py` (or extend existing permissions tests if preferred) asserting keys in `apps/api/core/permissions/constants.py`
- [x] T004 [P] Write failing pytest: create `DecisionCase` with required `title` (non-empty), `project` FK, default empty JSON lists for `selected_methods`, `criteria`, `alternatives`, `weights`, `types`, `performance_matrix`, `ahp_matrix`, `dematel_matrix`, `ism_matrix`; create related `DecisionRun` with `method`, `input_snapshot` dict, `result` dict, `extracted_at`, `extracted_by` in `apps/api/core/decision_support/tests/test_models.py`

### Implementation

- [x] T005 Add `view_decision_support`: `View decision support` and `edit_decision_support`: `Edit decision support` to `PERMISSIONS` in `apps/api/core/permissions/constants.py`; grant both to `project_manager`; grant view+edit to `planning_engineer`; grant `view_decision_support` to `viewer` per `specs/018-decision-case-shell/research.md`
- [x] T006 Implement `DecisionCase` in `apps/api/core/decision_support/models.py` using `AuditSoftDeleteModel` (or project UUID+timestamp base): `project` FK CASCADE; `title` CharField max_length=200 required; `selected_methods` JSONField default=list; `criteria` JSONField default=list; `alternatives` JSONField default=list; `weights` JSONField default=list; `types` JSONField default=list; `performance_matrix` JSONField default=list; `ahp_matrix`/`dematel_matrix`/`ism_matrix` JSONField default=list; indexes `(project, -created_at)`
- [x] T007 Implement `DecisionRun` in `apps/api/core/decision_support/models.py`: `case` FK CASCADE; `project` FK CASCADE (denormalized); `method` CharField; `input_snapshot` JSONField; `result` JSONField; `extracted_at` DateTimeField; `extracted_by` FK User PROTECT; Meta ordering `-extracted_at`; indexes `(case, -extracted_at)`, `(project, -extracted_at)`
- [x] T008 Register `decision_support` in `INSTALLED_APPS` in `apps/api/core/config/settings.py`; create migration `apps/api/core/decision_support/migrations/0001_initial.py`; include `path('<uuid:project_pk>/', include('decision_support.urls'))` in `apps/api/core/projects/urls.py` with empty `urlpatterns` initially in `apps/api/core/decision_support/urls.py`
- [x] T009 Re-run `apps/api/core/decision_support/tests/test_permissions_catalog.py` and `apps/api/core/decision_support/tests/test_models.py` until green

**Checkpoint**: App installed, permissions catalog updated, models migrate, ready for story TDD

---

## Phase 3: User Story 1 — Create and edit a project decision case (Priority: P1) 🎯 MVP

**Goal**: Project members with edit permission create/update cases: title, method multi-select (`saw|topsis|ahp|dematel|ism`), criteria/alternatives lists (max 10, unique non-empty), criteria-only methods may omit alternatives (FR-001–004, FR-012; AC02/AC03 selection shape)

**Independent Test**: Create case → set title → select methods → add ≤10 unique criteria/alternatives → reload persisted; multi-method selection without any engine execution

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T010 [P] [US1] Write failing API pytest POST `/api/v1/projects/{id}/decision-cases/` with title + `selected_methods: ["saw","topsis"]` + criteria/alternatives → 201 and GET returns same ordered lists in `apps/api/core/decision_support/tests/test_case_api.py` per `specs/018-decision-case-shell/contracts/decision-cases.md`
- [x] T011 [P] [US1] Write failing API pytest PATCH case `selected_methods` / criteria / alternatives persists; criteria-only `["ahp"]` with empty `alternatives` accepted in `apps/api/core/decision_support/tests/test_case_api.py` (US1 scenario 4)
- [x] T012 [P] [US1] Write failing API pytest: non-member or missing `edit_decision_support` → 403; case from other project → 404; GET list requires `view_decision_support` in `apps/api/core/decision_support/tests/test_case_api.py` (FR-012, IDOR)
- [x] T013 [P] [US1] Write failing API pytest: empty title, unknown method id, criteria length > 10, duplicate criterion name, empty name after trim → 400 with stable error code in `apps/api/core/decision_support/tests/test_case_api.py` (names mode; full ranking AC suite is US2)

### Implementation for User Story 1

- [x] T014 [US1] Implement names-mode helpers (trim, reject empty, exact uniqueness, max 10) and `create_case` / `update_case` in `apps/api/core/decision_support/services/case_service.py` raising `CodedValidationError` with `details.issues[{code,path,message}]` for name failures; method ids ∈ {`saw`,`topsis`,`ahp`,`dematel`,`ism`}
- [x] T015 [US1] Implement `DecisionCaseSerializer` in `apps/api/core/decision_support/serializers.py` for fields from data-model; thin `DecisionCaseViewSet` in `apps/api/core/decision_support/views.py` with `IsAuthenticated`, `IsProjectMember`, `HasProjectPermission` (`view_decision_support` / `edit_decision_support`); wire list/create/detail/patch/delete in `apps/api/core/decision_support/urls.py` as `decision-cases/`
- [x] T016 [US1] Re-run `apps/api/core/decision_support/tests/test_case_api.py` until green; update `apps/api/core/decision_support/ENDPOINTS.md` for case routes

**Checkpoint**: US1 independently testable — case CRUD + method selection MVP

---

## Phase 4: User Story 2 — Reject invalid shared inputs with locatable errors (Priority: P1)

**Goal**: Shared ranking/criteria validators enforce AC05–AC12; empty cell ≠ 0; `decision_input_invalid` issues include `path` (AC26); invalid payload never creates a run (run create wired in US3 — assert via validator unit + prep hook)

**Independent Test**: Each invalid fixture → coded failure with field/cell path; valid 1×1, 10×10, 2×3 accepted; `normalize_weights([2,3]) == normalize_weights([20,30])` (AC11)

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T017 [P] [US2] Write failing unit tests AC05 valid dims 1×1, 10×10, rectangular 2×3 accept in `apps/api/core/decision_support/tests/test_validators.py` per `specs/018-decision-case-shell/contracts/input-validation.md`
- [x] T018 [P] [US2] Write failing unit tests AC06 zero/over-10 dimensions reject with `path` on `criteria`/`alternatives` in `apps/api/core/decision_support/tests/test_validators.py`
- [x] T019 [P] [US2] Write failing unit tests AC07 short/extra row, weights/types length mismatch → `length_mismatch` + path in `apps/api/core/decision_support/tests/test_validators.py`
- [x] T020 [P] [US2] Write failing unit tests AC08 empty/`null` cell never coerced to 0; non-numeric, negative, NaN, Inf rejected with `performance_matrix.i.j` paths in `apps/api/core/decision_support/tests/test_validators.py`
- [x] T021 [P] [US2] Write failing unit tests AC09 cost zero; AC10 negative/all-zero weights; AC12 empty/duplicate name and invalid type in `apps/api/core/decision_support/tests/test_validators.py`
- [x] T022 [P] [US2] Write failing unit test AC11 `normalize_weights([2,3]) == normalize_weights([20,30])` in `apps/api/core/decision_support/tests/test_validators.py` (or `test_weights.py`)
- [x] T023 [P] [US2] Write failing API pytest: PATCH case with ranking payload containing empty matrix cell → 400 `decision_input_invalid` and `details.issues` include `path` (AC26) in `apps/api/core/decision_support/tests/test_validators.py` or `test_case_api.py`

### Implementation for User Story 2

- [x] T024 [US2] Implement pure `normalize_weights` in `apps/api/core/decision_support/services/weights.py` (`w[j]=weights[j]/sum(weights)` when sum>0)
- [x] T025 [US2] Implement `validate_names`, `validate_ranking_inputs`, `validate_criteria_only` in `apps/api/core/decision_support/services/validators.py` returning/raising `CodedValidationError(code='decision_input_invalid', detail={'issues':[...]})` with stable issue codes from `contracts/input-validation.md`; never coerce empty→0; O04 interim = trim + exact equality only
- [x] T026 [US2] Call ranking validators from `case_service` when ranking fields are present/non-empty on create/update in `apps/api/core/decision_support/services/case_service.py`
- [x] T027 [US2] Re-run `apps/api/core/decision_support/tests/test_validators.py` (and AC26 cases in `apps/api/core/decision_support/tests/test_case_api.py` if used) until green

**Checkpoint**: US2 independently testable — input contract + locatable errors

---

## Phase 5: User Story 3 — Immutable execution history shell (Priority: P1)

**Goal**: Stub `POST …/runs/` freezes deep-copied `input_snapshot` + stub `result`, records actor/time (AC23); new run after case edit leaves prior run unchanged (AC24); PATCH/PUT/DELETE run → `run_immutable` (FR-008–011)

**Independent Test**: Run A snapshot S1 → mutate case → Run B → GET A still S1; mutate A rejected

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T028 [P] [US3] Write failing API pytest: valid ranking case + POST `{"method":"saw"}` → 201 with `input_snapshot` retaining criteria/alternatives/weights/types/matrix names, `result.status=="stub"`, `extracted_by` set in `apps/api/core/decision_support/tests/test_runs_immutability.py` per `contracts/decision-runs.md` (AC23)
- [x] T029 [P] [US3] Write failing API pytest: after run A, PATCH case weight, POST run B → GET A `input_snapshot` deep-equal to original; B differs (AC24) in `apps/api/core/decision_support/tests/test_runs_immutability.py`
- [x] T030 [P] [US3] Write failing API pytest: PATCH/PUT/DELETE run → 400/405 `run_immutable`; invalid ranking POST run → 400 `decision_input_invalid` and **zero** new `DecisionRun` rows (AC26) in `apps/api/core/decision_support/tests/test_runs_immutability.py`
- [x] T031 [P] [US3] Write failing API pytest: POST run with method not in `selected_methods` → 400 `method_not_selected`; criteria-only method `ahp` stub run with criteria and empty alternatives succeeds freezing empty matrix stubs in `apps/api/core/decision_support/tests/test_runs_immutability.py`

### Implementation for User Story 3

- [x] T032 [US3] Implement `create_stub_run(case, method, user)` in `apps/api/core/decision_support/services/execution_service.py`: validate method selected; validate ranking vs criteria_only mode; `copy.deepcopy` live inputs into `input_snapshot`; set `result={"status":"stub","engine":null}`; set `extracted_at`/`extracted_by`/`project`; no engine math
- [x] T033 [US3] Add run serializers + nested ViewSet (list/retrieve/create only) in `apps/api/core/decision_support/serializers.py` and `views.py`; reject update/destroy with `CodedValidationError(code='run_immutable')`; wire `decision-cases/<uuid:case_pk>/runs/` in `apps/api/core/decision_support/urls.py`
- [x] T034 [US3] Re-run `apps/api/core/decision_support/tests/test_runs_immutability.py` until green; update run routes in `apps/api/core/decision_support/ENDPOINTS.md`

**Checkpoint**: US3 independently testable — immutable stub history

---

## Phase 6: User Story 4 — Minimal bilingual project UI shell (Priority: P2)

**Goal**: One project nav entry + route; create/edit case; NamedListEditor for criteria/alternatives (max 10); method multi-select; ValidationIssueList; ExecutionHistoryList + empty placeholders; `en`/`fa` strings; **no** five method calculation UIs; do not touch `project-decisions-workflow` (FR-013–015)

**Independent Test**: Open Decision Support in `fa`/`en` → create/edit case → named lists + method multi-select → empty/history placeholders; no engine panels

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T035 [P] [US4] Write failing Jest/Vitest (or project-equivalent) unit test: `NamedListEditor` rejects adding 11th name and surfaces duplicate/empty locally in `apps/web/src/components/decision-support/NamedListEditor.test.tsx` (create test file alongside component)
- [x] T036 [P] [US4] Write failing unit test: `ValidationIssueList` renders `path` + message from API-shaped issues in `apps/web/src/components/decision-support/ValidationIssueList.test.tsx`
- [x] T037 [P] [US4] Write failing assertion that locale keys `nav.projectDecisionSupport`, `decisionSupport.*` (title, methods, criteria, alternatives, history empty, validation) exist in both `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` via a small test or checklist script under `apps/web/src/components/decision-support/i18n.keys.test.ts`

### Implementation for User Story 4

- [x] T038 [US4] Add API client `apps/web/src/app/lib/api/decision-support.ts` for case CRUD + runs list/create/get matching contracts
- [x] T039 [US4] Implement `NamedListEditor.tsx`, `ValidationIssueList.tsx`, `ExecutionHistoryList.tsx`, and read-only `InputSnapshotViewer.tsx` (as needed) under `apps/web/src/components/decision-support/`; reuse `PageHeader` / `EmptyState` / form kit — no matrix editors
- [x] T040 [US4] Add route `apps/web/src/app/routes/project-decision-support.tsx` (case list/create/edit, method multi-select checkboxes for five methods, history placeholders); register `PATHS` / `routeVars` in `apps/web/src/app/routeVars.ts` and route table (`apps/web/src/app/routes.ts` or equivalent); add nav child **separate from** `decisions-workflow` in `apps/web/src/config/project-navigation.config.ts`
- [x] T041 [US4] Add bilingual strings to `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json`; wire validation issues from API `details.issues`
- [x] T042 [US4] Re-run US4 component/i18n tests until green; manual smoke per `specs/018-decision-case-shell/quickstart.md` UI section

**Checkpoint**: US4 independently testable — bilingual shell without engines

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, spectacular tags, full quickstart verification, confirm open items stay open

- [x] T043 [P] Complete `apps/api/core/decision_support/ENDPOINTS.md` with authz table and example error envelope from `contracts/input-validation.md`
- [x] T044 [P] Ensure drf-spectacular `summary`/`tags` (`Decision Support`) on viewsets in `apps/api/core/decision_support/views.py`
- [x] T045 Run full quickstart pytest trio: `decision_support/tests/test_validators.py`, `test_runs_immutability.py`, `test_case_api.py` (+ permissions/models) from `apps/api/core` per `specs/018-decision-case-shell/quickstart.md`
- [x] T046 Confirm no engine modules (`saw_service` etc.) and no edits to `apps/web/src/app/routes/project-decisions-workflow.tsx`; confirm O01–O10 not hard-coded as final policy in validators/comments referencing `docs/decision-support/11-source-review.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — 🎯 MVP
- **US2 (Phase 4)**: After Foundational; ideally after US1 case endpoints exist for AC26 API test (T023); pure unit tests T017–T022 can start once package exists
- **US3 (Phase 5)**: After US1 + US2 (needs case + ranking validators for stub runs)
- **US4 (Phase 6)**: After US1 API (client); better after US3 for history UI
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1**: No dependency on US2 full ranking suite (names-mode enough for MVP case)
- **US2**: Extends case updates with ranking validation; independent via unit tests
- **US3**: Depends on US1 models/API + US2 validators for ranking runs
- **US4**: Depends on US1 (+ US3 for history); no engine UI

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Services before/with thin views
- Re-run story tests green before checkpoint

### Parallel Opportunities

- T002 with doc review; T003∥T004; T010–T013∥; T017–T023∥; T028–T031∥; T035–T037∥; T043∥T044
- After Foundational: US2 unit tests can proceed in parallel with US1 API implementation if staffed
- US4 component tests can start once API shapes are stable (contracts)

---

## Parallel Example: User Story 2

```bash
# Launch AC fixture tests together (TDD red):
Task: "AC05 valid dims in test_validators.py"
Task: "AC06–AC08 reject fixtures in test_validators.py"
Task: "AC09–AC12 + AC11 normalize in test_validators.py"
Task: "AC26 API empty-cell path in test_case_api.py"

# Then implement:
Task: "weights.py + validators.py"
Task: "Wire case_service ranking validation"
```

---

## Parallel Example: User Story 3

```bash
Task: "AC23 stub run snapshot test"
Task: "AC24 immutability after case patch"
Task: "run_immutable + invalid creates zero rows"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational  
2. Phase 3 US1 (case CRUD) → **STOP and VALIDATE** `test_case_api.py`  
3. Demo: create case + methods + named lists via API

### Incremental Delivery

1. US1 → case shell API  
2. US2 → input contract (AC05–AC12, AC26)  
3. US3 → immutable stub runs (AC23–AC24)  
4. US4 → bilingual minimal UI  
5. Polish → quickstart green

### Parallel Team Strategy

1. Team finishes Foundational together  
2. Dev A: US1 API · Dev B: US2 validators (unit) · then Dev A/B: US3 · Dev C: US4 UI after contracts stable  

---

## Notes

- [P] = different files, no incomplete dependencies  
- Verify tests fail before implementing  
- Leave O01–O10 open; empty ≠ 0; no method engines  
- Do not overload `project-decisions-workflow`  
- Commit after each task or logical TDD group  

## Task count summary

| Phase | Tasks | Notes |
|-------|-------|-------|
| Setup | T001–T002 | 2 |
| Foundational | T003–T009 | 7 (incl. 2 test tasks) |
| US1 | T010–T016 | 7 |
| US2 | T017–T027 | 11 |
| US3 | T028–T034 | 7 |
| US4 | T035–T042 | 8 |
| Polish | T043–T046 | 4 |
| **Total** | **T001–T046** | **46** |

---

## Phase 8: Convergence

**Purpose**: Close gaps found by `/speckit-converge` against spec, plan, tasks, and constitution (2026-10-10). Prior phases T001–T046 left unchanged.

- [x] T047 CRITICAL Localize Decision Support validation messages for Persian and English per FR-014, SC-005, and Constitution III (partial): wrap or replace English `issues[].message` strings in `apps/api/core/decision_support/services/validators.py` (and `case_service` / `execution_service` error texts) with `gettext`/`gettext_lazy`, and/or map stable issue `code`s to `decisionSupport.errors.*` keys in `apps/web/src/components/decision-support/ValidationIssueList.tsx` + `NamedListEditor.tsx` using `apps/web/src/app/locales/en.json` and `fa.json` (keep codes language-independent; cover at least `name_empty`, `name_duplicate`, `dimension_invalid`, `empty_cell`, `decision_input_invalid`, `run_immutable`, `method_not_selected`)
- [x] T048 Review or document the unrequested `**/*.test.ts` exclude in `apps/web/tsconfig.json` added for Node strip-types tests under `apps/web/src/components/decision-support/*.test.ts` (unrequested): keep with a one-line comment justifying exclusion, or remove exclude and relocate/adapt tests so `pnpm typecheck` stays clean

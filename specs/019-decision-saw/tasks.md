# Tasks: Decision Support SAW Ranking (Phase 2)

**Input**: Design documents from `/specs/019-decision-saw/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md  
**Depends on**: Phase 1 `decision_support` app (`specs/018-decision-case-shell`) completed

**Tests**: **TDD required** (user requested `Use TDD`). For each slice: write failing pytest (or UI unit test where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = confirm Phase 1 baseline + shared AC13 guard hook + execution entry rename readiness. No TOPSIS/AHP/DEMATEL/ISM engines.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock feature context and document SAW contracts before TDD slices

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/019-decision-saw"` and review TDD + AC14 sample in `specs/019-decision-saw/plan.md`, `quickstart.md`, and `contracts/saw-engine.md`
- [x] T002 [P] Update `apps/api/core/decision_support/ENDPOINTS.md` to document Phase 2 SAW run behavior (real `result.engine=saw`, snapshot `weights_normalized`, interim ordinal ranks) per `specs/019-decision-saw/contracts/saw-runs.md` while noting non-SAW methods may remain stub

---

## Phase 2: Foundational — Baseline + AC13 readiness (Blocking)

**Purpose**: Prove Phase 1 suite still green; add failing AC13 structural/engine-prep tests and issue-code constants so stories share one rejection path. Blocks all stories.

**⚠️ CRITICAL**: Do not implement TOPSIS. Do not close O01/O02 beyond the interim ordinal rank policy in the spec.

### Tests (TDD — write first, must FAIL)

- [x] T003 [P] Re-run baseline Phase 1 suites green: `apps/api/core/decision_support/tests/test_validators.py`, `test_runs_immutability.py`, `test_case_api.py`, `test_models.py`, `test_permissions_catalog.py` (document any failures; fix only regressions unrelated to SAW)
- [x] T004 [P] Write failing unit test: benefit column all zeros (even with weight `0` on that criterion) raises issue `code=benefit_column_all_zero` and `path=criteria.{j}` in `apps/api/core/decision_support/tests/test_validators.py` (AC13) per `specs/019-decision-saw/contracts/ranking-inputs.md`

### Implementation

- [x] T005 Extend `validate_ranking_inputs` (or add `assert_saw_engine_guards`) in `apps/api/core/decision_support/services/validators.py` to reject all-zero benefit columns with `benefit_column_all_zero` at `criteria.{j}`; keep cost-zero / weight rules aligned with AC09–AC10; never coerce empty→0
- [x] T006 Re-run `apps/api/core/decision_support/tests/test_validators.py` until AC13 (and existing AC05–AC12) green

**Checkpoint**: Shared guards ready; SAW engine/story work can begin

---

## Phase 3: User Story 1 — Enter ranking inputs and run SAW only (Priority: P1) 🎯 MVP

**Goal**: Pure `compute_saw` + `POST …/runs/` with `method=saw` persists immutable run with frozen snapshot (incl. `weights_normalized`) and ordered `{option,score,rank}` matching AC14; TOPSIS never required or executed (AC01, AC11, FR-001–003, FR-007–009, FR-012)

**Independent Test**: Acceptance sample → run SAW only → scores الف=`1.0`, ب=`0.5`, order الف then ب; response has no TOPSIS fields; scaled weights `[2,3]` vs `[20,30]` yield identical scores

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T007 [P] [US1] Write failing unit tests in `apps/api/core/decision_support/tests/test_saw_service.py`: AC14 fixture from `contracts/saw-engine.md` → ranking scores `1.0`/`0.5`, order الف then ب, ranks `1`/`2` (interim ordinal); return includes `weights_normalized`
- [x] T008 [P] [US1] Write failing unit test AC11 in `apps/api/core/decision_support/tests/test_saw_service.py`: identical SAW scores for weights `[2,3]` vs `[20,30]` on otherwise equal valid inputs
- [x] T009 [P] [US1] Write failing unit test in `apps/api/core/decision_support/tests/test_saw_service.py`: `compute_saw` return value has no TOPSIS keys / does not import or call TOPSIS (AC01 pure engine)
- [x] T010 [P] [US1] Write failing API pytest in `apps/api/core/decision_support/tests/test_saw_api.py`: case with `selected_methods:["saw"]` only + acceptance sample → POST `{"method":"saw"}` → 201, `result.status=="ok"`, `result.engine=="saw"`, ranking matches AC14, `input_snapshot.weights_normalized` present, body has no TOPSIS fields (AC01)
- [x] T011 [P] [US1] Write failing API pytest in `apps/api/core/decision_support/tests/test_saw_api.py`: PATCH case weights/types/`performance_matrix` (length `n` / `m×n`, types `benefit|cost`, finite non-negative) persists via existing case API then SAW run uses live values per `contracts/ranking-inputs.md`

### Implementation for User Story 1

- [x] T012 [US1] Implement pure `compute_saw(criteria, alternatives, weights, types, matrix)` in `apps/api/core/decision_support/services/saw_service.py` using formulas from `contracts/saw-engine.md` and `normalize_weights` from `apps/api/core/decision_support/services/weights.py`; sort score-desc with stable input-order ties; assign 1-based ordinal `rank`; raise `CodedValidationError`/`decision_input_invalid` issues for engine guards; **no** TOPSIS code
- [x] T013 [US1] Replace stub path for `method=saw` in `apps/api/core/decision_support/services/execution_service.py`: validate ranking → `compute_saw` → deep-copy snapshot including `weights_normalized` → `result={"status":"ok","engine":"saw","ranking":[...]}`; keep stub behavior for non-SAW methods; update `apps/api/core/decision_support/views.py` to call the upgraded create-run entry (rename `create_stub_run` → `create_run` or branch inside)
- [x] T014 [US1] Ensure case serializers already expose `weights` / `types` / `performance_matrix` for PATCH in `apps/api/core/decision_support/serializers.py`; adjust only if SAW run hydration gaps exist; update `apps/api/core/decision_support/ENDPOINTS.md` SAW success example
- [x] T015 [US1] Re-run `apps/api/core/decision_support/tests/test_saw_service.py` and `apps/api/core/decision_support/tests/test_saw_api.py` until green; confirm Phase 1 stub tests for non-SAW still pass or update expectations only where SAW result shape changed for `method=saw`

**Checkpoint**: US1 independently testable — SAW-only MVP with AC14

---

## Phase 4: User Story 2 — Reject invalid ranking inputs before successful SAW run (Priority: P1)

**Goal**: Cost zeros, bad weights, all-zero benefit columns, empty/non-finite cells stop SAW; locatable `issues[].path`; **zero** new successful runs (AC09–AC10, AC13, AC26, FR-004–006, FR-010, FR-013)

**Independent Test**: Each invalid fixture → 400 with path → DecisionRun count unchanged

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T016 [P] [US2] Write failing API pytest AC09 in `apps/api/core/decision_support/tests/test_saw_api.py`: cost cell `0` → 400 `cost_zero` at `performance_matrix.{i}.{j}`; assert run count unchanged
- [x] T017 [P] [US2] Write failing API pytest AC10 in `apps/api/core/decision_support/tests/test_saw_api.py`: negative weight and all-zero weights → 400 with `weight_negative` / `weights_all_zero`; no run created
- [x] T018 [P] [US2] Write failing API pytest AC13 in `apps/api/core/decision_support/tests/test_saw_api.py`: all-zero benefit column (weight 0 on that column) → 400 `benefit_column_all_zero` path `criteria.{j}`; no run created
- [x] T019 [P] [US2] Write failing API pytest AC08/AC26 in `apps/api/core/decision_support/tests/test_saw_api.py`: empty/`null` matrix cell on SAW run → 400 `decision_input_invalid` with `performance_matrix.i.j` path; never coerced to 0; no run created
- [x] T020 [P] [US2] Write failing unit tests in `apps/api/core/decision_support/tests/test_saw_service.py` mirroring AC09/AC13 engine-level rejects with same issue codes/paths as contracts

### Implementation for User Story 2

- [x] T021 [US2] Ensure `execution_service` SAW path calls structural validation then engine guards before persist; map all failures to `decision_input_invalid` issues; never create `DecisionRun` on failure in `apps/api/core/decision_support/services/execution_service.py` / `saw_service.py` / `validators.py`
- [x] T022 [US2] Re-run `apps/api/core/decision_support/tests/test_saw_api.py` and AC09/AC13 cases in `apps/api/core/decision_support/tests/test_saw_service.py` until green

**Checkpoint**: US2 independently testable — invalid matrices never succeed

---

## Phase 5: User Story 3 — Immutable SAW run history after re-run (Priority: P1)

**Goal**: Successful SAW runs freeze snapshot + ranking; case edit + second SAW run leaves prior run byte-stable; in-place run mutation rejected (AC23–AC24, FR-011)

**Independent Test**: SAW run A → mutate weight/cell → SAW run B → GET A unchanged; PATCH A → `run_immutable`

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T023 [P] [US3] Write failing API pytest in `apps/api/core/decision_support/tests/test_saw_api.py` (or extend `test_runs_immutability.py`): successful SAW run retains criterion/alternative names, frozen weights/types/matrix, `result.ranking` scores, actor/time (AC23)
- [x] T024 [P] [US3] Write failing API pytest AC24: after SAW run A, PATCH one weight or matrix cell, POST SAW run B → GET A `input_snapshot` and `result.ranking` deep-equal to originals; B reflects new inputs
- [x] T025 [P] [US3] Write failing API pytest: PATCH/PUT/DELETE on SAW run → `run_immutable` (400/405) in `apps/api/core/decision_support/tests/test_saw_api.py` or `test_runs_immutability.py`

### Implementation for User Story 3

- [x] T026 [US3] Verify `copy.deepcopy` on snapshot/result at create in `apps/api/core/decision_support/services/execution_service.py`; ensure no shared mutable references between live case JSON and stored run; keep run ViewSet create-only in `apps/api/core/decision_support/views.py`
- [x] T027 [US3] Re-run immutability/SAW API tests until green; adjust Phase 1 `test_runs_immutability.py` expectations for `method=saw` from `result.status=="stub"` to `ok`/`engine=saw` where those tests still use SAW

**Checkpoint**: US3 independently testable — real SAW history immutable

---

## Phase 6: User Story 4 — Ranking input and SAW result UI on the case page (Priority: P2)

**Goal**: Shared ranking editors + `SawMethodPanel` with validate→run, `RankingResultTable`, locatable issues, bilingual strings; no client SAW math (FR-014–017, FR-020 UI portion)

**Independent Test**: Edit weights/types/matrix → run SAW → see scores/ranks; invalid cell shows path; `fa`/`en` labels; editors reusable (no TOPSIS panel yet)

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T028 [P] [US4] Write failing unit tests for matrix/weight helper rules (empty≠0, dimension align) in `apps/web/src/components/decision-support/RectangularMatrixEditor.test.ts` and/or `WeightVectorEditor.test.ts` (or shared `ranking-input-rules.ts` tests)
- [x] T029 [P] [US4] Write failing unit test: `RankingResultTable` renders option/score/rank rows from SAW `result.ranking` in `apps/web/src/components/decision-support/RankingResultTable.test.tsx` (or `.test.ts`)
- [x] T030 [P] [US4] Write failing i18n key presence test for SAW panel/editor/result/validation keys in `apps/web/src/components/decision-support/i18n.keys.test.ts` (extend existing) covering both `en.json` and `fa.json`
- [x] T031 [P] [US4] Write failing structural/unit guard: SAW formula tokens (e.g. benefit `max` normalize / cost `min` divide score loop) absent from `apps/web/src/components/decision-support/SawMethodPanel.tsx` and ranking editors (test file under `apps/web/src/components/decision-support/` or document as `apps/api/core/decision_support/tests/test_no_math_in_views.py` for views + separate web check)

### Implementation for User Story 4

- [x] T032 [P] [US4] Extend types + helpers in `apps/web/src/app/lib/api/decision-support.ts` for SAW `result.ranking`, `result.engine`, snapshot `weights_normalized`; ensure `createDecisionRun` / `patchDecisionCase` hydrate `weights`, `types`, `performance_matrix`
- [x] T033 [P] [US4] Implement `WeightVectorEditor.tsx`, `CriterionTypeToggle.tsx`, `RectangularMatrixEditor.tsx` under `apps/web/src/components/decision-support/` as thin controlled editors (no SAW scoring)
- [x] T034 [P] [US4] Implement `RunActionBar.tsx` and `RankingResultTable.tsx` under `apps/web/src/components/decision-support/`
- [x] T035 [US4] Implement `SawMethodPanel.tsx` composing shared editors + RunActionBar + RankingResultTable + `ValidationIssueList`; wire into `apps/web/src/app/routes/project-decision-support.tsx` when `saw` ∈ selected methods (hydrate/save ranking fields; POST run SAW; show latest/selected run ranking)
- [x] T036 [US4] Add bilingual strings under `decisionSupport` in `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` for weights, types, matrix, run SAW, result columns, engine errors
- [x] T037 [US4] Re-run US4 web unit/i18n tests until green; manually smoke validate→run path per `specs/019-decision-saw/quickstart.md` UI section

**Checkpoint**: US4 independently testable — ranking UX + SAW panel on case page

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, structural guards, quickstart evidence

- [x] T038 [P] Add optional `apps/api/core/decision_support/tests/test_no_math_in_views.py` asserting `views.py` / serializers do not contain SAW normalization loops (FR-020)
- [x] T039 [P] Update `apps/api/core/decision_support/ENDPOINTS.md` and spectacular summaries/tags on run create for SAW success vs validation errors in `apps/api/core/decision_support/views.py` / serializers
- [x] T040 Run full quickstart automated commands from `specs/019-decision-saw/quickstart.md` and record evidence categories (pytest SAW service/API/immutability; note UI smoke separately)
- [x] T041 Confirm O01/O02 remain open as final policy; only interim ordinal ranks shipped — note in `apps/api/core/decision_support/ENDPOINTS.md` or service docstring referencing `specs/019-decision-saw/spec.md` interim policy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Immediate
- **Foundational (Phase 2)**: After Setup — **BLOCKS** all stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational; practically after US1 engine exists (same `saw_service` / run path) but independently testable via invalid fixtures
- **US3 (Phase 5)**: After US1 success path exists (needs real SAW results)
- **US4 (Phase 6)**: After US1 API contract stable (can stub UI against contracts earlier, but integrate after T015)
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

| Story | Depends on | Notes |
|-------|------------|-------|
| US1 | Phase 2 | MVP — pure engine + SAW run |
| US2 | Phase 2 (+ US1 impl for API path) | Invalid fixtures; can write tests in parallel with US1 |
| US3 | US1 | Immutability with real SAW payloads |
| US4 | US1 API | UI consumes run/case contracts |

### Within Each User Story

1. Write failing tests first  
2. Implement minimal production code  
3. Re-run until green  
4. Checkpoint before next story  

### Parallel Opportunities

```text
Phase 2: T004 test || (after T003 baseline)
US1 tests: T007 || T008 || T009 || T010 || T011
US2 tests: T016 || T017 || T018 || T019 || T020
US3 tests: T023 || T024 || T025
US4 tests: T028 || T029 || T030 || T031
US4 impl: T032 || T033 || T034 (then T035 wires them)
Polish: T038 || T039
```

---

## Parallel Example: User Story 1

```bash
# Write failing tests in parallel:
# - apps/api/core/decision_support/tests/test_saw_service.py (AC14, AC11, no TOPSIS)
# - apps/api/core/decision_support/tests/test_saw_api.py (SAW-only POST run)

# Then implement serially:
# - saw_service.py
# - execution_service.py branch for saw
# - re-run until green
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational (AC13 guard)  
3. Phase 3 US1 — pure SAW + run API  
4. **STOP and VALIDATE** AC14 / AC01 / AC11 via pytest  
5. Demo API-level SAW-only ranking  

### Incremental Delivery

1. Setup + Foundational → guards ready  
2. US1 → SAW-only scores (MVP)  
3. US2 → invalid inputs never create runs  
4. US3 → immutability with real results  
5. US4 → shared ranking UI + SawMethodPanel  
6. Polish → quickstart evidence  

### Parallel Team Strategy

- After Phase 2: Dev A on US1 engine/API; Dev B can draft US2 failing tests and US4 editor shells against contracts  
- US3 waits on US1 green  
- US4 integration waits on stable run response shape  

---

## Notes

- [P] = different files, no incomplete dependencies  
- TDD: red → green → refactor; do not skip failing-test proof  
- Interim ordinal ranks only — do not implement shared/tied ranks as final O01  
- No TOPSIS/AHP/DEMATEL/ISM engines; no auto weight import  
- Reuse Phase 1 permissions, case CRUD, ValidationIssueList, history components  
- Suggested MVP scope: **US1 only** (T001–T015 + foundational)

---

## Phase 8: Convergence

**Purpose**: Close gaps found by `/speckit-converge` against spec/plan/tasks (code assessment only).

- [x] T042 Sync `RankingResultTable` in `apps/web/src/components/decision-support/SawMethodPanel.tsx` when `latestRanking` (or selected history run) changes from `apps/web/src/app/routes/project-decision-support.tsx` so selecting a SAW run shows that run's scores/ranks per FR-015 / US4/AC2 / T035 (`partial`)
- [x] T043 Extend client validate in `apps/web/src/components/decision-support/ranking-input-rules.ts` (and `SawMethodPanel` Validate action) to include criterion `types` plus cost-zero and benefit-column-all-zero checks with the same `path`/`code` conventions as `contracts/ranking-inputs.md`, so Validate surfaces blocking issues before Run per US4/AC2–AC3 (`partial`)
- [x] T044 Add pytest in `apps/api/core/decision_support/tests/test_saw_service.py` for equal SAW scores: stable input-order tie-break and distinct interim ordinal ranks (1,2,…) per FR-018 / spec interim O01 policy / edge case Equal SAW scores (`partial`)

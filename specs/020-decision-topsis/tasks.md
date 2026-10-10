# Implementation Tasks: Decision Support TOPSIS Ranking (Phase 3)

**Branch**: `020-decision-topsis` | **Date**: 2026-10-10 | **Approach**: TDD (Test-Driven Development)  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md) | **Quickstart**: [quickstart.md](./quickstart.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Type definitions and bilingual localization entries needed across both backend and frontend layers.

- [x] T001 [P] Define `TopsisRankingRow` (`option: string; d_best: number; d_worst: number; closeness: number; score: number; rank: number;`), `RankingRow` union (`SawRankingRow | TopsisRankingRow`), and update `DecisionRunResult.ranking` to `RankingRow[]` in `apps/web/src/app/lib/api/decision-support.ts`
- [x] T002 [P] Update `rankingRowsFromResult` in `apps/web/src/components/decision-support/ranking-result-rows.ts` to accept `RankingRow[]` and export helper type definitions for TOPSIS rows
- [x] T003 [P] Add TOPSIS panel labels (`topsisPanelTitle: "TOPSIS ranking"`, `topsisPanelHint: "Run TOPSIS alone with manual weights — no other method is required."`), distance headers (`colDBest: "D⁺ (best)"`, `colDWorst: "D⁻ (worst)"`, `colCloseness: "Closeness (C*)"`), and error key (`errors.topsis_denom_zero: "TOPSIS column normalization denominator is zero — all values in this criterion column cannot be zero."`) to `apps/web/src/app/locales/en.json`
- [x] T004 [P] Add TOPSIS Persian panel labels (`topsisPanelTitle: "رتبه‌بندی TOPSIS"`, `topsisPanelHint: "فقط TOPSIS را با وزن دستی اجرا کنید — روش دیگری لازم نیست."`), distance headers (`colDBest: "D⁺ (بهترین)"`, `colDWorst: "D⁻ (بدترین)"`, `colCloseness: "نزدیکی (C*)"`), and error key (`errors.topsis_denom_zero: "مخرج نرمال‌سازی ستون TOPSIS صفر است — مقادیر ستون یک معیار نمی‌توانند همگی صفر باشند."`) to `apps/web/src/app/locales/fa.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core engine scaffold and table component support that block user story execution.

**⚠️ CRITICAL**: Must complete before any user story implementation begins.

- [x] T005 Create module scaffold for pure TOPSIS engine in `apps/api/core/decision_support/services/topsis_service.py` declaring `compute_topsis(criteria, alternatives, weights, types, matrix)` function signature returning `dict[str, Any]` with `ranking` and `weights_normalized`
- [x] T006 Extend `RankingResultTable.tsx` in `apps/web/src/components/decision-support/RankingResultTable.tsx` with a discriminated union on `method: "saw" | "topsis"`, supporting optional `extraColumns: ExtraColumn<TopsisRankingRow>[]` to render D⁺ and D⁻ cells while preserving SAW layout without forking

**Checkpoint**: Foundation ready - user story implementation and TDD cycles can now begin.

---

## Phase 3: User Story 1 - Run TOPSIS only on ranking inputs (Priority: P1) 🎯 MVP

**Goal**: Enable authorized project members to execute TOPSIS alone on ranking inputs, computing column vector normalization, weighted matrix, ideal best/worst solutions, Euclidean distances (`d_best`, `d_worst`), closeness scores, and 1-based ordinal rank, without executing or creating a SAW run (AC01, AC15).

**Independent Test**: Acceptance sample (doc 10 fixture: criteria `['تجربه', 'قیمت']`, alternatives `['پیمانکار الف', 'پیمانکار ب']`, weights `[1, 1]`, types `['benefit', 'cost']`, matrix `[[10, 100], [5, 200]]`) produces closeness scores `1.0` for الف and `0.0` for ب with rank order الف then ب, with zero SAW runs created and no SAW dependency.

### Tests for User Story 1 (TDD) ⚠️
> *Write these tests FIRST and ensure they FAIL before implementation.*

- [x] T007 [P] [US1] Create unit tests in `apps/api/core/decision_support/tests/test_topsis_service.py` covering AC15 acceptance sample (closeness `1.0` for الف and `0.0` for ب, order الف then ب), AC11 scaled weights invariance (weights `[2, 3]` vs `[20, 30]` produce identical closeness), and AC01 method isolation (output dictionary contains no `SAW` keys and does not import SAW module machinery)
- [x] T008 [P] [US1] Create API integration tests in `apps/api/core/decision_support/tests/test_topsis_api.py` verifying POST `/api/v1/projects/{project_id}/decision-cases/{case_id}/runs/` with `{"method": "topsis"}` creates an immutable `DecisionRun` with `method="topsis"`, `status="ok"`, `engine="topsis"`, AC15 scores, normalized weights in `input_snapshot`, and zero SAW runs created (AC01, AC15)

### Implementation for User Story 1

- [x] T009 [US1] Implement column vector normalization `v[i,j] = w[j] * x[i,j] / denom[j]` where `denom[j] = sqrt(sum_i(x[i,j]**2))`, ideal best/worst vectors identification based on criterion types (`benefit`: best=max, worst=min; `cost`: best=min, worst=max), Euclidean distances (`d_best`, `d_worst`), closeness `d_worst / (d_best + d_worst)`, and stable ordinal ranking (score descending, preserving input order on ties) in `apps/api/core/decision_support/services/topsis_service.py`
- [x] T010 [US1] Wire TOPSIS execution into `apps/api/core/decision_support/services/execution_service.py` in `create_run()`, replacing the stub branch with `elif method == 'topsis':`, invoking `compute_topsis()`, snapshotting case inputs with `weights_normalized`, and saving `DecisionRun` with `result={"status": "ok", "engine": "topsis", "ranking": topsis_out["ranking"]}`

**Checkpoint**: User Story 1 is functional and verifiable independently. TOPSIS runs end-to-end via API without SAW dependency (MVP complete).

---

## Phase 4: User Story 2 - Reject invalid TOPSIS inputs; AC16 edge scores (Priority: P1)

**Goal**: Reject invalid TOPSIS inputs with locatable error codes—specifically all-zero column normalization denominator zero (`topsis_denom_zero` at `criteria.{j}`) and shared contract violations—preventing successful run creation (FR-004, AC26), and handle zero total distance returning closeness `0.5` (AC16).

**Independent Test**: All-zero matrix column produces a `400 Bad Request` with `code: "topsis_denom_zero"` at path `criteria.{j}` and no DecisionRun is created; single alternative or identical options row produces closeness `0.5` with rank 1.

### Tests for User Story 2 (TDD) ⚠️
> *Write these tests FIRST and ensure they FAIL before implementation.*

- [x] T011 [P] [US2] Add unit tests in `apps/api/core/decision_support/tests/test_topsis_service.py` verifying that all-zero column matrices raise `CodedValidationError` with `code="topsis_denom_zero"` at path `criteria.{j}`, and that AC16 edge case where `d_best + d_worst == 0` (single alternative or identical rows) returns closeness `0.5`
- [x] T012 [P] [US2] Add API integration tests in `apps/api/core/decision_support/tests/test_topsis_api.py` verifying that POST `/runs/` with all-zero matrix column returns 400 with `issues` containing `code="topsis_denom_zero"` and zero runs created (FR-004, AC26), shared ranking errors (empty cell, cost zero) return 400 with zero runs created, and single-alternative cases return 201 with closeness `0.5` (AC16)

### Implementation for User Story 2

- [x] T013 [US2] Implement `_check_topsis_denominators()` in `apps/api/core/decision_support/services/topsis_service.py` asserting for each column `j` that `sqrt(sum(x[i][j]**2 for i in range(m))) > 0.0`, raising `_issue('topsis_denom_zero', f'criteria.{j}', 'TOPSIS normalization denominator is zero: all values in this column are zero.')` before scoring
- [x] T014 [US2] Implement AC16 zero total distance rule in `apps/api/core/decision_support/services/topsis_service.py` setting `closeness = 0.5` when `d_best + d_worst == 0.0`

**Checkpoint**: User Stories 1 and 2 work independently with full engine guards and locatable error contracts.

---

## Phase 5: User Story 3 - SAW and TOPSIS side-by-side without blending (Priority: P1)

**Goal**: Support executing both SAW and TOPSIS on the same decision case in either order, maintaining distinct `DecisionRun` records and separate result sets without blending or merged ranks (AC03, AC25), while enforcing run immutability (AC23, AC24).

**Independent Test**: Run SAW then TOPSIS (and TOPSIS then SAW) on a single case → exactly two `DecisionRun` records exist with distinct methods; neither modifies the other's result; editing case weights and re-running TOPSIS appends a third run while preserving previous runs' snapshots.

### Tests for User Story 3 (TDD) ⚠️
> *Write these tests FIRST and ensure they FAIL before implementation.*

- [x] T015 [P] [US3] Add API integration tests in `apps/api/core/decision_support/tests/test_topsis_api.py` executing both SAW and TOPSIS on the same case in both execution sequences, verifying two separate `DecisionRun` records exist, method results remain distinct, neither mutates the other, and no blended score or rank is generated (AC03, AC25)
- [x] T016 [P] [US3] Add API integration tests in `apps/api/core/decision_support/tests/test_topsis_api.py` verifying run immutability: modifying case inputs after a TOPSIS run and executing TOPSIS again creates a new run with updated snapshot while preserving the prior run's frozen `input_snapshot` and `result`, and PATCH/PUT/DELETE requests against existing runs return 400 `run_immutable` (AC23, AC24)

### Implementation for User Story 3

- [x] T017 [US3] Validate and verify that `apps/api/core/decision_support/services/execution_service.py` and `apps/api/core/decision_support/views.py` isolate method execution, guarantee that `method="topsis"` and `method="saw"` runs remain decoupled, and enforce run immutability across both methods

**Checkpoint**: Multi-method independence and run immutability verified across SAW and TOPSIS.

---

## Phase 6: User Story 4 - TOPSIS panel reusing shared ranking UI (Priority: P2)

**Goal**: Provide `TopsisMethodPanel` in the frontend that composes existing shared ranking editors (`WeightVectorEditor`, `CriterionTypeToggle`, `RectangularMatrixEditor`, `RunActionBar`), displays distances and closeness via `RankingResultTable`, and provides bilingual feedback without embedding TOPSIS calculation formulas in the UI layer (FR-005, FR-011, FR-012).

**Independent Test**: Open a project decision case with TOPSIS selected → shared editors render with live inputs → trigger TOPSIS run → result table renders option, score (closeness), interim rank, D⁺, and D⁻ columns; test confirms zero math formulas in client files.

### Tests for User Story 4 (TDD) ⚠️
> *Write these tests FIRST and ensure they FAIL before implementation.*

- [x] T018 [P] [US4] Create source inspection test `apps/web/src/components/decision-support/no-client-topsis-math.test.ts` scanning `TopsisMethodPanel.tsx` to assert it contains no client-side TOPSIS scoring formulas (`ideal_best`, `d_best`, `d_worst`, `closeness`, `Math.sqrt`) in compliance with FR-005
- [x] T019 [P] [US4] Add component unit tests in `apps/web/src/components/decision-support/RankingResultTable.test.ts` verifying that `rankingRowsFromResult` extracts `TopsisRankingRow` items and `RankingResultTable` renders `extraColumns` (`d_best`, `d_worst`, `closeness`) when `method="topsis"`

### Implementation for User Story 4

- [x] T020 [US4] Implement `TopsisMethodPanel.tsx` in `apps/web/src/components/decision-support/TopsisMethodPanel.tsx` composing `WeightVectorEditor`, `CriterionTypeToggle`, `RectangularMatrixEditor`, `RunActionBar`, `ValidationIssueList`, and `RankingResultTable` passing `extraColumns` for D⁺ (`colDBest`) and D⁻ (`colDWorst`), invoking `createDecisionRun(projectId, caseId, "topsis")` on run action
- [x] T021 [US4] Integrate `TopsisMethodPanel` into `apps/web/src/app/routes/project-decision-support.tsx` conditionally rendered when `methods.includes("topsis")`, maintaining independent TOPSIS ranking state and synchronizing with `ExecutionHistoryList` on run selection

**Checkpoint**: Frontend TOPSIS panel fully functional, bilingual, integrated, and verified against no-client-math rules.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification across all automated suites, documentation alignment, and end-to-end regression validation.

- [x] T022 [P] Execute full backend pytest suite `apps/api/.venv/bin/python -m pytest decision_support/tests/` in `apps/api/core` ensuring 100% pass rate across SAW, TOPSIS, permissions, and immutability tests
- [x] T023 [P] Execute frontend test suite `pnpm --filter @building-management/web test` and run `pnpm typecheck` to confirm zero regression across decision support components and routes
- [x] T024 Validate all quickstart scenarios in `specs/020-decision-topsis/quickstart.md` (Scenarios A through E: TOPSIS-only run, SAW+TOPSIS side-by-side, AC16 edge case, all-zero denominator rejection, and re-run immutability) in both English and Persian locales

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion - MVP increment.
- **User Story 2 (Phase 4)**: Depends on US1 core engine (Phase 3) completion.
- **User Story 3 (Phase 5)**: Depends on US1 and US2 (Phase 3 & 4) completion.
- **User Story 4 (Phase 6)**: Depends on US1 backend completion and Phase 2 table foundation. Can be developed in parallel with US3.
- **Polish (Phase 7)**: Depends on all user story phases being complete.

```mermaid
flowchart TD
    Setup[Phase 1: Setup] --> Foundational[Phase 2: Foundational]
    Foundational --> US1[Phase 3: User Story 1 - TOPSIS Engine & API (MVP)]
    US1 --> US2[Phase 4: User Story 2 - Zero Denom & AC16 Guards]
    US2 --> US3[Phase 5: User Story 3 - SAW + TOPSIS Side-by-Side]
    US1 --> US4[Phase 6: User Story 4 - Frontend TopsisMethodPanel]
    US2 --> US4
    US3 --> Polish[Phase 7: Polish & Validation]
    US4 --> Polish
```

### Within Each User Story (TDD Flow)

1. **Write Tests First**: Create test tasks (`[P] [USx]`) and verify they fail before writing implementation.
2. **Implement Engine / Services**: Fulfill mathematical and validation logic to turn unit tests green.
3. **Implement Integration / UI**: Wire endpoints and frontend components to turn integration tests green.
4. **Checkpoint Validation**: Verify story independently before advancing to the next priority.

### Parallel Opportunities

- **Phase 1 (Setup)**: Tasks T001, T002, T003, T004 touch disjoint files and can run concurrently.
- **Phase 3 (US1)**: Tests T007 and T008 can be written concurrently.
- **Phase 4 (US2)**: Tests T011 and T012 can be written concurrently.
- **Phase 5 (US3)**: Tests T015 and T016 can be written concurrently.
- **Phase 6 (US4)**: Tests T018 and T019 can be written concurrently.
- **Cross-Story**: Once Phase 4 (US2) is complete, Phase 5 (US3 backend integration) and Phase 6 (US4 frontend panel) can be executed in parallel.

---

## Parallel Execution Examples

### Parallel Example: Phase 1 Setup
```bash
# All setup tasks modify independent files:
Task: "Define TopsisRankingRow in apps/web/src/app/lib/api/decision-support.ts" (T001)
Task: "Update rankingRowsFromResult in apps/web/src/components/decision-support/ranking-result-rows.ts" (T002)
Task: "Add TOPSIS keys to apps/web/src/app/locales/en.json" (T003)
Task: "Add TOPSIS keys to apps/web/src/app/locales/fa.json" (T004)
```

### Parallel Example: User Story 1 TDD Tests
```bash
# Launch both US1 test tasks together:
Task: "Create unit tests in apps/api/core/decision_support/tests/test_topsis_service.py" (T007)
Task: "Create API integration tests in apps/api/core/decision_support/tests/test_topsis_api.py" (T008)
```

### Parallel Example: User Story 2 TDD Tests
```bash
# Launch both US2 test tasks together:
Task: "Add unit tests in apps/api/core/decision_support/tests/test_topsis_service.py" (T011)
Task: "Add API integration tests in apps/api/core/decision_support/tests/test_topsis_api.py" (T012)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete **Phase 1: Setup** (T001–T004)
2. Complete **Phase 2: Foundational** (T005–T006)
3. Execute TDD cycle for **Phase 3: User Story 1** (T007–T010)
4. **STOP and VALIDATE**: Verify AC15 acceptance sample and AC01 independence via `test_topsis_service.py` and `test_topsis_api.py`. At this point, the backend TOPSIS engine is 100% operational as a standalone service.

### Incremental Delivery

1. **Increment 1 (MVP)**: Standalone TOPSIS engine + API execution (US1).
2. **Increment 2**: Input validation guards (zero denominator rejection) and AC16 edge case handling (US2).
3. **Increment 3**: Simultaneous SAW and TOPSIS execution without score blending + run immutability verification (US3).
4. **Increment 4**: Full frontend UI with `TopsisMethodPanel`, distance columns, and bilingual localization (US4).
5. **Increment 5**: Full test suite pass and quickstart verification (Polish).

---

## Notes & Compliance Check

- **Strict Format**: Every task follows `- [ ] [TaskID] [P?] [Story?] Description with file path`.
- **TDD Requirement**: Every user story phase contains test tasks labeled `[USx]` marked with instructions to write and fail first.
- **Constitution Compliance**: Enforces Principle I (server-side authorization), Principle III (Persian/English i18n), Principle IV (run immutability), Principle V (minimal coherent changes, no UI math), and Principle VI (evidence-based verification via pytest and quickstart).

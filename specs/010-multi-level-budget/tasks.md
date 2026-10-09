# Tasks: Multi-Level Budget Gap Closure

**Input**: Design documents from `/specs/010-multi-level-budget/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — FR-BUD success criteria require pytest evidence.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [x] T001 Confirm feature dir `specs/010-multi-level-budget/` and `.specify/feature.json` point here
- [x] T002 [P] Add i18n stubs for budget version/CR/remaining keys in `apps/web/src/app/locales/en.json` and `fa.json`

---

## Phase 2: Foundational (blocking)

- [x] T003 Add `BudgetVersion`, `BudgetChangeRequest`, `BudgetTransfer` models and extend `Budget` (version, level, contract, period) in `apps/api/core/cost_control/models.py`
- [x] T004 Create migration `0005_multi_level_budget.py` including data migration attaching legacy `Budget` rows to a synthetic version per project
- [x] T005 [P] Add serializers for versions, lines, CR, transfer, remaining in `apps/api/core/cost_control/serializers.py`
- [x] T006 Wire URL routes in `apps/api/core/cost_control/urls.py` per contracts

**Checkpoint**: Models + routes exist; user stories can proceed

---

## Phase 3: User Story 1 — Register & submit initial budget (P1) 🎯 MVP

**Goal**: Draft initial version, multi-level lines, submit/approve, lock approved lines

- [x] T007 [US1] Implement `budget_version_service.py` (create, submit, approve, reject, compare, control flag)
- [x] T008 [US1] Implement version-scoped line CRUD + version-aware `bulk_upsert_budgets` / `budget_service.py` with `budget_version_locked`
- [x] T009 [US1] Implement `budget_version_views.py` + extend `BudgetViewSet`/`BudgetBulkView` for `version_id`
- [x] T010 [US1] pytest `cost_control/tests/test_budget_versions.py` — create lines at levels, submit/approve, lock mutation, compare
- [x] T011 [US1] Frontend: version API in `costs.ts`; `BudgetVersionsPanel.tsx`; make `BudgetGrid.tsx` version-aware and read-only when locked
- [x] T012 [US1] Wire panel into `project-costs.tsx` budget tab

**Checkpoint**: SC-BUD-001 / SC-001

---

## Phase 4: User Story 2 — Change request workflow (P1)

**Goal**: CR-only changes to approved baseline; ceiling hard-block

- [x] T013 [US2] Implement `budget_change_service.py` (create/submit/approve/reject/cancel; clone version + apply affected_lines)
- [x] T014 [US2] Implement CR views + ceiling check helper used by allocation/transfer/line paths (`project_ceiling_exceeded`)
- [x] T015 [US2] pytest `cost_control/tests/test_budget_change_requests.py` — direct edit rejected; CR approve creates revised control; reject leaves baseline
- [x] T016 [US2] Frontend: `BudgetChangeRequestPanel.tsx` + API helpers; show lock messaging on grid

**Checkpoint**: SC-BUD-002 / SC-002 / FR-BUD-006

---

## Phase 5: User Story 3 — Remaining & transfers (P2)

**Goal**: Remaining allocatable + controlled transfers

- [x] T017 [US3] Implement `remaining_service.py` (approved − committed − consumed; cbs warning)
- [x] T018 [US3] Implement transfer service + `POST …/budgets/transfers/` and `GET …/budgets/remaining/`
- [x] T019 [US3] pytest `cost_control/tests/test_remaining_transfer.py`
- [x] T020 [US3] Frontend: `RemainingAllocatablePanel.tsx` + transfer UI affordance; update cost summary to prefer control version totals if needed

**Checkpoint**: SC-BUD-003 / SC-003

---

## Phase 6: Polish

- [x] T021 [P] Update `cost_control` ENDPOINTS or schedule ENDPOINTS cross-links if present; ensure spectacular tags
- [x] T022 Run focused pytest suite; fix regressions in `test_cost_control.py` for version-aware budgets
- [x] T023 Mark all tasks complete after verification

---

## Dependency graph

```text
T001–T002 → T003–T006 → US1 (T007–T012) → US2 (T013–T016) → US3 (T017–T020) → T021–T023
```

## Parallel opportunities

- T002 || T001; T005 || T004 (after T003); T011 UI after T009 API; T016 after T014

## Implementation strategy

1. Foundational models/migration first  
2. US1 MVP (versions + lock)  
3. US2 CR + ceiling  
4. US3 remaining/transfer  
5. Polish + regression

---

## Phase 7: Convergence

- [x] T024 CRITICAL: When a control approved budget already exists, block `approve_version` for free-standing `revised` (and other control-eligible kinds except first `initial`) unless the version was produced by an approved `BudgetChangeRequest`; route amount/structure changes through CR only per FR-003 / US2/AC1 (`contradicts`)
- [x] T025 Wire `assert_within_project_ceiling` into allocation and line-mutation paths that can raise spend/committed/allocated totals above the control ceiling (cost-pool allocate and any non–net-zero budget path); fix transfer post-check so it cannot no-op by reading ceiling after mutating control lines per FR-006 / SC-003 / T014 (`partial`)
- [x] T026 Add pytest proving over-ceiling allocation/transfer is rejected with `project_ceiling_exceeded` (and CR approve that raises ceiling still succeeds) per SC-003 (`missing`)
- [x] T027 Extend BudgetGrid / costs UI (or a compact line editor) so draft versions can add lines at `project`, `phase`, `contract`, `cbs`, and optional `period_start`/`period_end` — not only WBS/activity — per FR-001 / US1/AC1 (`partial`)
- [x] T028 UI: allow creating `final_forecast` versions and pass `promote_to_control` on approve when intended per FR-008 (`partial`)
- [x] T029 UI: version compare (left/right + optional FX) using existing compare API per SC-004 (`partial`)
- [x] T030 Document budget-versions, change-requests, remaining, transfers, and compare in `apps/api/core/cost_control/ENDPOINTS.md` (T021 claimed done but file still omits them) per Constitution II / T021 (`partial`)

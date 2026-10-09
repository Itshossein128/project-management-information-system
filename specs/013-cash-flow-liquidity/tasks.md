# Tasks: Cash Flow & Liquidity Allocation Gap Closure

**Input**: Design documents from `/specs/013-cash-flow-liquidity/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required for every task slice** (user instruction). Pattern: write failing pytest (or UI assertion where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = shared portfolio membership filter used by US2–US4.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/013-cash-flow-liquidity"` and review `specs/013-cash-flow-liquidity/plan.md` TDD discipline
- [x] T002 [P] Inventory extension points in `apps/api/core/cash_flow/{models.py,views.py,urls.py,services/cashflow_service.py,ENDPOINTS.md}` and feeds in `contracts` / `cost_control`; note gaps vs `specs/013-cash-flow-liquidity/research.md`

---

## Phase 2: Foundational — Portfolio membership filter (Blocking)

**Purpose**: Shared helper that returns projects the user may see for cash-flow portfolio APIs (`view_cashflow` + active membership). Blocks trustworthy US2–US4 portfolio work.

**⚠️ CRITICAL**: Portfolio stories MUST use this filter (no IDOR).

### Tests (TDD — write first, must FAIL)

- [x] T003 Write failing pytest that a user without membership on project B does not see B in the visible-projects helper in `apps/api/core/cash_flow/tests/test_portfolio_membership.py`

### Implementation

- [x] T004 Implement `projects_visible_for_cashflow(user)` in `apps/api/core/cash_flow/services/portfolio_access.py` (active membership + `view_cashflow`)
- [x] T005 Re-run `apps/api/core/cash_flow/tests/test_portfolio_membership.py` until green; register module import path if needed

**Checkpoint**: Membership filter green; foundation ready for story work

---

## Phase 3: User Story 1 — Project cash flow & net need (Priority: P1) 🎯 MVP

**Goal**: Domain-fed monthly projected in/out separate from actuals; monthly net need; suggested net need FR-004 (FR-001–004, SC-001)

**Independent Test**: Approved IPC with collection due + approved commitment with due_date → projection month shows in/out/net; actual series separate; suggested-need formula holds

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T006 [P] [US1] Write failing pytest IPC remaining due month → `projected_inflow` in `apps/api/core/cash_flow/tests/test_projection_series.py` per `specs/013-cash-flow-liquidity/contracts/projected-cash-series.md`
- [x] T007 [P] [US1] Write failing pytest approved commitment open amount by `due_date` → `projected_outflow` and `net_need` in `apps/api/core/cash_flow/tests/test_projection_series.py`
- [x] T008 [P] [US1] Write failing pytest that response keeps `months` (projected) and `actual_months` as separate keys (never merged) in `apps/api/core/cash_flow/tests/test_projection_series.py`
- [x] T009 [P] [US1] Write failing pytest project without IPCs → `inflow_status=unregistered` (not silent success-zero) in `apps/api/core/cash_flow/tests/test_projection_series.py`
- [x] T010 [P] [US1] Write failing pytest FR-004 formula `due_commitments + essential_costs − certain_planned_receipts` in `apps/api/core/cash_flow/tests/test_net_need.py` per `specs/013-cash-flow-liquidity/contracts/net-need.md`

### Implementation for User Story 1

- [x] T011 [US1] Implement `build_projected_series(project_id, from_month, to_month)` in `apps/api/core/cash_flow/services/projection_service.py` (inflow: approved unpaid IPC remaining by `planned_payment_date`; outflow: approved commitment open = amount − posted payments by `due_date`)
- [x] T012 [US1] Implement `suggested_net_need(project_id, period_start, period_end)` in `apps/api/core/cash_flow/services/net_need_service.py` with meta rules from contract (`essential_costs` default 0 unless approved actuals in configured categories)
- [x] T013 [US1] Add serializers + `GET .../cash-flow/projection/` and `GET .../cash-flow/suggested-need/` in `apps/api/core/cash_flow/views.py` and `apps/api/core/cash_flow/urls.py` with `view_cashflow`
- [x] T014 [US1] Re-run `test_projection_series.py` and `test_net_need.py` until green; ensure existing `apps/api/core/cash_flow/tests/test_cashflow_api.py` still passes
- [x] T015 [US1] Frontend: Projection + NetNeed panels on `apps/web/src/app/routes/project-cash-flow.tsx` / `apps/web/src/components/cashflow/`; API client in `apps/web/src/app/lib/api/cashflow.ts`; i18n in `apps/web/src/app/locales/en.json` and `fa.json` (empty inflow copy)

**Checkpoint**: US1 independently testable — projection + suggested need

---

## Phase 4: User Story 2 — Propose & record liquidity allocation (Priority: P2)

**Goal**: Priority scores (0–100 components; composite equal weights); cycle with `available_liquidity`; ranked proposal; decision with owner + rationale + impact (FR-005–007, SC-002–003 partial)

**Independent Test**: Two scored projects → propose ranks by composite within pool → decision without rationale rejected → decision with owner/rationale saved

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T016 [P] [US2] Write failing pytest PUT/GET priority score and composite `(urgency + return_score + recovery_speed + (100 − risk)) / 4` with components constrained 0–100 in `apps/api/core/cash_flow/tests/test_allocation_proposal_decision.py` per `specs/013-cash-flow-liquidity/contracts/liquidity-allocation.md`
- [x] T017 [P] [US2] Write failing pytest propose ranks complete-score projects by composite and respects `available_liquidity`; incomplete scores in `warnings.incomplete_score_projects` in `apps/api/core/cash_flow/tests/test_allocation_proposal_decision.py`
- [x] T018 [P] [US2] Write failing pytest `available_liquidity=0` → empty `lines` + `message=no_available_liquidity` in `apps/api/core/cash_flow/tests/test_allocation_proposal_decision.py`
- [x] T019 [P] [US2] Write failing pytest decision missing owner or rationale → 400; with both → 201 and history fields in `apps/api/core/cash_flow/tests/test_allocation_proposal_decision.py`

### Implementation for User Story 2

- [x] T020 [US2] Add models in `apps/api/core/cash_flow/models.py`: `ProjectPriorityScore` (unique project; urgency/return_score/recovery_speed/risk Decimal 0–100; computed composite); `LiquidityAllocationCycle` (name, period_start/end, available_liquidity, currency, status draft|proposed|decided|closed); `AllocationProposal` + `AllocationProposalLine`; `AllocationDecision` + `AllocationDecisionLine` (owner FK required, rationale Text required, schedule_impact/cost_impact Text blank OK)
- [x] T021 [US2] Create migration in `apps/api/core/cash_flow/migrations/`
- [x] T022 [US2] Implement score upsert + proposal generation + decision create in `apps/api/core/cash_flow/services/allocation_service.py` (greedy allocate positive suggested need; filter via `projects_visible_for_cashflow`)
- [x] T023 [US2] Wire portfolio URLs under `/api/v1/cash-flow/portfolio/` in `apps/api/core/cash_flow/urls.py` + register in main URLconf; views/serializers for score, cycles, propose, decisions
- [x] T024 [US2] Re-run `test_allocation_proposal_decision.py` until green
- [x] T025 [US2] Frontend portfolio liquidity scaffold: cycle + scores + proposal + decision form in `apps/web/src/app/routes/portfolio-liquidity.tsx` and `apps/web/src/components/cashflow/allocation/`; route registration; i18n

**Checkpoint**: US2 independently testable — propose + auditable decision

---

## Phase 5: User Story 3 — Double allocation warn & simulation (Priority: P2)

**Goal**: Overlapping decision lines warn unless `acknowledge_overlap`; save/compare simulation (FR-008, SC-004)

**Independent Test**: Second overlapping decision without ack → `overlapping_allocation`; with ack → 201; simulation compare diffs vs proposal

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T026 [P] [US3] Write failing pytest overlapping project+period decision without `acknowledge_overlap` → 400 `overlapping_allocation` in `apps/api/core/cash_flow/tests/test_double_allocation_warn.py`
- [x] T027 [P] [US3] Write failing pytest same overlap with `acknowledge_overlap=true` → 201 in `apps/api/core/cash_flow/tests/test_double_allocation_warn.py`
- [x] T028 [P] [US3] Write failing pytest save simulation + compare endpoint returns per-project amount diffs vs latest proposal in `apps/api/core/cash_flow/tests/test_double_allocation_warn.py` (or `test_allocation_simulation.py`)

### Implementation for User Story 3

- [x] T029 [US3] Add `AllocationSimulation` model (cycle FK, name, payload JSON `{lines:[{project_id, amount}]}`, created_by) in `apps/api/core/cash_flow/models.py` + migration
- [x] T030 [US3] Implement overlap detection + ack gate and simulation save/compare in `apps/api/core/cash_flow/services/allocation_service.py`
- [x] T031 [US3] Expose simulation endpoints on portfolio cycle URLs in `apps/api/core/cash_flow/views.py` / `urls.py`
- [x] T032 [US3] Re-run `test_double_allocation_warn.py` until green
- [x] T033 [US3] Frontend: overlap acknowledgment dialog + simulation save/compare UI in `apps/web/src/components/cashflow/allocation/`; i18n

**Checkpoint**: US3 independently testable — overlap warn + simulation

---

## Phase 6: User Story 4 — Portfolio cash & allocation reports (Priority: P2)

**Goal**: Portfolio report of projected cash, net need, scores, and recorded allocations for member-visible projects (FR-009, SC-001–002)

**Independent Test**: Two member projects with projection + one decision → both in `projects`; decision in `allocations`; non-member project excluded

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T034 [P] [US4] Write failing pytest portfolio report includes only membership-visible projects’ projection + suggested need + composite in `apps/api/core/cash_flow/tests/test_portfolio_cash_report.py` per `specs/013-cash-flow-liquidity/contracts/portfolio-report.md`
- [x] T035 [P] [US4] Write failing pytest report lists allocation decisions for cycle and excludes projects user cannot view in `apps/api/core/cash_flow/tests/test_portfolio_cash_report.py`

### Implementation for User Story 4

- [x] T036 [US4] Implement `build_portfolio_report(user, from, to, cycle_id?)` in `apps/api/core/cash_flow/services/portfolio_report_service.py` using projection + net_need + scores + decisions
- [x] T037 [US4] Add `GET /api/v1/cash-flow/portfolio/report/` in `apps/api/core/cash_flow/views.py` / `urls.py`
- [x] T038 [US4] Re-run `test_portfolio_cash_report.py` until green
- [x] T039 [US4] Frontend: portfolio report table on `apps/web/src/app/routes/portfolio-liquidity.tsx` linking to project cash-flow; i18n

**Checkpoint**: US4 independently testable — portfolio report

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, regressions, bilingual polish, quickstart suite

### Tests (TDD / regression)

- [x] T040 Write or extend regression pytest that manual `CashFlowForecast` does not overwrite computed projection keys in `apps/api/core/cash_flow/tests/test_projection_series.py` (FR-010)

### Implementation / docs

- [x] T041 [P] Update `apps/api/core/cash_flow/ENDPOINTS.md` for projection, suggested-need, priority-score, portfolio cycles/propose/decisions/simulations/report
- [x] T042 [P] Ensure all new UI strings in `apps/web/src/app/locales/en.json` and `fa.json`
- [x] T043 Run full FR-CASH pytest subset from `specs/013-cash-flow-liquidity/quickstart.md` and fix regressions
- [ ] T044 [P] Optional: wire projected cumulative gap into existing `cash_gap_detected` alert checker in `apps/api/core/alerts/services/checkers.py` with a focused failing-then-green test if touching alerts

---

## Dependencies & Execution Order

### Phase Dependencies

```text
T001–T002 → T003–T005 (membership filter)
         → US1 (T006–T015) 🎯 MVP
         → US2 (T016–T025)   [needs US1 suggested-need for proposal amounts]
         → US3 (T026–T033)   [needs US2 decision models]
         → US4 (T034–T039)   [needs US1 projection + US2 decisions]
         → T040–T044
```

- **US1**: After Phase 2 only (does not need allocation models)
- **US2**: After Phase 2; uses US1 `suggested_net_need` for proposal line amounts
- **US3**: After US2 decision/cycle models
- **US4**: After US1 + at least one decision path (US2)

### Within Each User Story / Task Slice

1. Failing test first (confirm red)  
2. Minimal model/service/endpoint/UI change  
3. Re-run named test green  
4. Then next task  

### Parallel Opportunities

- T001 ∥ T002
- T006 ∥ T007 ∥ T008 ∥ T009 ∥ T010 (US1 red tests)
- T016 ∥ T017 ∥ T018 ∥ T019 (US2 red tests)
- T026 ∥ T027 ∥ T028 (US3 red tests)
- T034 ∥ T035 (US4 red tests)
- T041 ∥ T042 ∥ T044 after APIs stable
- After Phase 2: A = US1; B drafts US2 models only after coordinating `models.py`

---

## Parallel Example: User Story 1

```bash
# Red
Task: "test_projection_series.py — IPC inflow + commitment outflow + separate actual keys"
Task: "test_net_need.py — FR-004 formula"

# Green (sequential on shared services)
Task: "projection_service.py"
Task: "net_need_service.py"
Task: "views/urls + frontend panels"
```

---

## Implementation Strategy

### MVP First (Phase 2 + User Story 1)

1. Setup + membership filter  
2. Projection + suggested need (TDD)  
3. **STOP and VALIDATE** with `test_projection_series.py` + `test_net_need.py`  
4. Demo project cash projection  

### Incremental Delivery

1. US1 → project cash baseline  
2. US2 → scores + proposal + decision  
3. US3 → overlap + simulation  
4. US4 → portfolio report  
5. Polish → docs + quickstart suite  

### Parallel Team Strategy

1. Together: Phase 1–2  
2. A: US1; B prepares US2 models after US1 net-need exists  
3. B: US2 → US3; A: US4 + polish  

---

## Notes

- **TDD every slice**: no production change without a preceding failing test for that behavior  
- Computed projection on read — do not auto-write `CashTransaction(is_forecast=True)` for IPC/commitment feeds  
- Manual forecast remains side-by-side (FR-010)  
- Double-allocation policy: **warn + `acknowledge_overlap`** (not hard-block without ack)  
- Quote field constraints from `data-model.md` (0–100 scores; owner/rationale required; cycle status enum)  
- Commit after each red→green slice  

# Tasks: Contracts & IPC Gap Closure

**Input**: Design documents from `/specs/011-contracts-ipc/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*

**Tests**: Include for each user story (Constitution).

## Phase 1: Setup

- [x] T001 Confirm feature dir `specs/011-contracts-ipc/` and `.specify/feature.json` point here
- [x] T002 Review existing `contracts` models/views/collection_service and note extension points in research (done in research.md)

## Phase 2: Foundational (blocking)

- [x] T003 [P] Add `Contract.payment_terms` TextField in `apps/api/core/contracts/models.py`
- [x] T004 [P] Add `IPC.submitted_amount`, `IPC.approved_amount`, `IPC.approval_variance_note` in `apps/api/core/contracts/models.py`
- [x] T005 Create migration with backfill of submitted/approved from `gross_amount` by status in `apps/api/core/contracts/migrations/`
- [x] T006 Update serializers in `apps/api/core/contracts/serializers.py` for new fields (read + write rules)
- [x] T007 Wire submit/approve service logic for amount snapshots and variance validation

**Checkpoint**: migrate applies; serializers expose new fields

## Phase 3: User Story 1 — Payment terms & addenda (P1)

**Goal**: FR-CON-001 payment terms + existing change orders  
**Independent Test**: create contract with payment_terms; change order still works

- [x] T008 [US1] Pytest `contracts/tests/test_payment_terms.py` — create/update/retrieve payment_terms
- [x] T009 [US1] Ensure contract create/update serializers and views accept payment_terms
- [x] T010 [US1] Frontend: payment terms textarea on contract form + display in `apps/web/src/components/contracts/` and locales

## Phase 4: User Story 2 — IPC amounts & collection invariant (P1)

**Goal**: FR-CON-002–004, SC-CON-001–002  
**Independent Test**: submit → approve reduced → two collections → status/amounts unchanged

- [x] T011 [US2] Pytest `contracts/tests/test_ipc_amounts.py` — submit freezes submitted; approve sets approved; variance note required
- [x] T012 [US2] Pytest `contracts/tests/test_collection_status_invariant.py` — collection never changes status or submitted/approved
- [x] T013 [US2] Enforce approve body rules + lock gross after submit in service/views
- [x] T014 [US2] Guard in collection_service: do not mutate status/amounts; document no auto-paid
- [x] T015 [US2] Frontend: show submitted/approved/variance on IPC detail; approve dialog supports amount + note

## Phase 5: User Story 3 — Receivables report (P2)

**Goal**: FR-CON-005, SC-CON-003  
**Independent Test**: overdue + near-due bands; fully collected excluded

- [x] T016 [US3] Implement `receivables_service.py` report builder
- [x] T017 [US3] Add `GET .../ipcs/receivables-report/` view + URL + spectacular docs
- [x] T018 [US3] Pytest `contracts/tests/test_receivables_report.py`
- [x] T019 [US3] Frontend ReceivablesPanel on contracts page + API client + i18n

## Phase 6: Polish

- [x] T020 Update `apps/api/core/contracts/ENDPOINTS.md` for payment_terms, amounts, report
- [x] T021 Run full contracts pytest subset and fix regressions
- [x] T022 [P] Quickstart smoke against local API (optional)

## Dependencies

```
T001–T002 → T003–T007 → US1 (T008–T010) ∥ US2 (T011–T015) → US3 (T016–T019) → T020–T022
```

US1 and US2 can proceed in parallel after Phase 2.

## Parallel opportunities

- T003 ∥ T004
- T008 ∥ T011 ∥ T012 (tests)
- T010 ∥ T015 (frontend) after APIs ready

## Implementation strategy

MVP = Phase 2 + US1 + US2 (payment terms + amount split + invariant). Then US3 report. Polish last.

## Phase 7: Convergence

- [x] T023 CRITICAL: Include `submitted_amount` and `approved_amount` on IPC PDF export in `contracts/pdf.py` and extend PDF tests, per Constitution II / FR-002 (`partial`)
- [x] T024 Lock `auto_populate_ipc` / `IPCPopulateView` (and any other gross mutators) so post-submit IPCs cannot rewrite `gross_amount`, per `plan: ipc-amounts` / FR-002 (`contradicts`)
- [x] T025 Add end-to-end pytest: submit → approve → partial collections → remaining receivable 0 while `submitted_amount` is preserved, per SC-001 (`partial`)
- [x] T026 Add pytest that `payment_terms` persist after change-order approve (amount updates, terms unchanged), per US1 independent test / US1/AC2 (`partial`)
- [x] T027 Localize new contracts UI strings (`payment_terms` form label; approve amount/variance labels) via `en.json`/`fa.json`, per Constitution III / plan locales (`partial`)
- [x] T028 Add regression pytest that IPC create rejects a contract from another project (project tenancy), per FR-007 (`missing`)

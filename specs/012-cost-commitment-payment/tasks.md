# Tasks: Cost Commitment & Payment Gap Closure

**Input**: Design documents from `/specs/012-cost-commitment-payment/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required** (plan + prior user instruction). For every story: write failing pytest first → confirm red → implement minimal green → refactor. Do not mark a task done without the named test evidence.

**Organization**: Phases by user story (US1–US4). Foundational = remaining non-double-count (blocks correct budget control for all stories).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/012-cost-commitment-payment"` and review `specs/012-cost-commitment-payment/plan.md` TDD rules
- [x] T002 [P] Inventory extension points in `apps/api/core/cost_control/models.py`, `cbs_services.py`, `services/remaining_service.py`, `cbs_views.py`, `urls.py` and note gaps vs `specs/012-cost-commitment-payment/research.md`

---

## Phase 2: Foundational — Remaining non-double-count (Blocking)

**Purpose**: Fix allocable remaining so commitment + linked actual never double-consume (SC-006). MUST complete before US1–US4 claim remaining behavior.

**⚠️ CRITICAL**: No user story remaining assertions can be trusted until this phase is green.

### Tests (TDD — write first, must FAIL)

- [x] T003 Write failing pytest for open-commitment remaining steps A→C in `apps/api/core/cost_control/tests/test_remaining_no_double_count.py` per `specs/012-cost-commitment-payment/contracts/remaining-and-report.md` (approved=1000, commitment 600, linked actual 400 then 600; assert `committed`/`consumed`/`remaining` semantics)

### Implementation

- [x] T004 Implement open-commitment formula in `apps/api/core/cost_control/services/remaining_service.py`: `committed` = sum over approved commitments of `max(0, amount − sum(approved non-void actuals linked to that commitment))`; `consumed` = sum of approved non-void actuals on heading; `remaining = max(0, approved − consumed − committed)` with `overrun` on raw &lt; 0
- [x] T005 Re-run `apps/api/core/cost_control/tests/test_remaining_no_double_count.py` and existing `apps/api/core/cost_control/tests/test_remaining_transfer.py`; fix regressions only in remaining math

**Checkpoint**: Remaining formula green; foundation ready for story work

---

## Phase 3: User Story 1 — Register a financial commitment (Priority: P1) 🎯 MVP

**Goal**: Commitment with amount, currency, date, party, WBS/CBS, **payment_terms**, status, optional contract link; approve reduces allocable remaining (FR-002–004, SC-001)

**Independent Test**: Create commitment with `payment_terms` + CBS → approve → `budgets/remaining/` shows open committed decrease; missing classification on approve still rejected

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T006 [P] [US1] Write failing pytest create/update/retrieve `payment_terms` and optional `contract` FK in `apps/api/core/cost_control/tests/test_commitment_payment_terms.py` per `specs/012-cost-commitment-payment/contracts/commitment-payment-terms.md`
- [x] T007 [P] [US1] Extend or add failing assertion in `apps/api/core/cost_control/tests/test_commitment_payment_terms.py` that approved commitment with CBS reduces heading remaining via `GET .../budgets/remaining/` (depends on Phase 2 formula)

### Implementation for User Story 1

- [x] T008 [US1] Add `Commitment.payment_terms` TextField (`blank=True`, `default=""`) and optional `Commitment.contract` FK → `contracts.Contract` (`null=True`, `blank=True`) in `apps/api/core/cost_control/models.py`
- [x] T009 [US1] Create migration for commitment fields in `apps/api/core/cost_control/migrations/`
- [x] T010 [US1] Expose `payment_terms` and `contract` on create/update/detail in `apps/api/core/cost_control/serializers.py` and ensure approve path in `apps/api/core/cost_control/cbs_services.py` still enforces `wbs_or_cbs_required`
- [x] T011 [US1] Wire serializers/views if needed in `apps/api/core/cost_control/cbs_views.py` so POST/PATCH/GET `/api/v1/projects/{id}/commitments/` round-trip new fields
- [x] T012 [US1] Add payment-terms textarea + optional contract selector on commitment UI in `apps/web/src/components/costs/CBSCommitmentTab.tsx` (and API types in `apps/web/src/app/lib/api/` costs/central-data module) with i18n keys in `apps/web/src/locales/en.json` and `apps/web/src/locales/fa.json`
- [x] T013 [US1] Re-run `apps/api/core/cost_control/tests/test_commitment_payment_terms.py` and `apps/api/core/cost_control/tests/test_commitment_payment.py` until green

**Checkpoint**: US1 independently testable — payment terms + remaining reduce on approve

---

## Phase 4: User Story 2 — Actual cost separate from commitment (Priority: P1)

**Goal**: Actual cost as distinct value with occurrence/register dates, approval status, classification + optional document policy (FR-005–007, FR-010, SC-005)

**Independent Test**: Commitment then linked actual; both reportable separately; approve without WBS/CBS rejected; policy-on without document rejected

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T014 [P] [US2] Write failing pytest for occurrence=`cost_date`, `registered_at`, draft→approve→void, and `wbs_or_cbs_required` on approve in `apps/api/core/cost_control/tests/test_actual_cost_lifecycle.py` per `specs/012-cost-commitment-payment/contracts/actual-cost-lifecycle.md`
- [x] T015 [P] [US2] Write failing pytest for `cost_document_required` when project policy `require_cost_document=True` and empty invoice/document in `apps/api/core/cost_control/tests/test_actual_cost_lifecycle.py`
- [x] T016 [P] [US2] Write failing pytest that ledger/list shows commitment amount and actual amount as separate figures for same commitment link in `apps/api/core/cost_control/tests/test_actual_cost_lifecycle.py` (or shared helper until ledger endpoint exists in US3)

### Implementation for User Story 2

- [x] T017 [US2] Add `ActualCost.registered_at` DateField, `ActualCost.status` (`draft` \| `approved` \| `void`, default `draft`), optional `ActualCost.document_ref` CharField in `apps/api/core/cost_control/models.py`; keep `cost_date` as occurrence
- [x] T018 [US2] Add project cost policy flag `require_cost_document` (bool, default `False`) on existing project capability/settings model in `apps/api/core/projects/models.py` (or cost_control settings if that is the established pattern) — quote constraint: default False
- [x] T019 [US2] Create migration(s) in `apps/api/core/cost_control/migrations/` (and projects if needed): backfill existing ActualCost `status='approved'`, `registered_at=cost_date` when null
- [x] T020 [US2] Implement approve/void services and validation (`wbs_or_cbs_required`, `cost_document_required`, `invalid_status_transition`) in `apps/api/core/cost_control/` services (extend `cbs_services.py` or new `services/actual_cost_service.py`)
- [x] T021 [US2] Add `POST .../costs/{id}/approve/` and `POST .../costs/{id}/void/` in `apps/api/core/cost_control/views.py` + `urls.py`; update `ActualCostSerializer` in `apps/api/core/cost_control/serializers.py` for new fields; new creates default `status=draft`
- [x] T022 [US2] Ensure remaining formula only counts **approved** non-void actuals in `apps/api/core/cost_control/services/remaining_service.py` (align with data-model); extend `test_remaining_no_double_count.py` if draft actuals incorrectly consumed
- [x] T023 [US2] Frontend: occurrence/register dates + status + approve/void actions on costs ledger UI under `apps/web/src/app/routes/project-costs.tsx` / related cost components; i18n in `en.json` / `fa.json`
- [x] T024 [US2] Re-run `apps/api/core/cost_control/tests/test_actual_cost_lifecycle.py` until green

**Checkpoint**: US2 independently testable — actual lifecycle + no silent double-count with Phase 2

---

## Phase 5: User Story 3 — Pay without duplicate; contract/order remaining; ledger (Priority: P1)

**Goal**: Payments linked to commitment/cost; duplicate `document_ref` blocked unless authorized exception; contract remaining; document-traceable ledger (FR-008–009, FR-011–012, SC-002–004)

**Independent Test**: Second payment same document rejected; exception path works; remaining = approved − valid payments; ledger shows three row types

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T025 [P] [US3] Write failing pytest duplicate `document_ref` → `duplicate_payment_document` and exception ack path in `apps/api/core/cost_control/tests/test_payment_duplicate_guard.py` per `specs/012-cost-commitment-payment/contracts/payment-duplicate-guard.md`
- [x] T026 [P] [US3] Write failing pytest partial installments (distinct refs) preserve source amount and decrease commitment remaining in `apps/api/core/cost_control/tests/test_payment_duplicate_guard.py`
- [x] T027 [P] [US3] Write failing pytest contract remaining = approved_amount − posted payments on commitments with that contract FK in `apps/api/core/cost_control/tests/test_contract_order_remaining.py` per `specs/012-cost-commitment-payment/contracts/remaining-and-report.md`
- [x] T028 [P] [US3] Write failing pytest ledger report returns `commitment` \| `actual` \| `payment` rows with document refs in `apps/api/core/cost_control/tests/test_ledger_report.py`

### Implementation for User Story 3

- [x] T029 [US3] Add `Payment.duplicate_exception_reason` TextField (`blank=True`) and `Payment.duplicate_exception_by` FK to user (`null=True`) in `apps/api/core/cost_control/models.py` + migration in `apps/api/core/cost_control/migrations/`
- [x] T030 [US3] Enforce duplicate guard in `apps/api/core/cost_control/cbs_services.py` `create_payment` (same project, non-empty trimmed `document_ref`, status posted, not deleted): reject unless `acknowledge_duplicate_exception` + non-empty `exception_reason`; persist exception fields
- [x] T031 [US3] Accept exception flags on `POST .../payments/` in `apps/api/core/cost_control/cbs_views.py` / serializers (`PaymentSerializer` in `apps/api/core/cost_control/serializers.py`)
- [x] T032 [US3] Implement contract cost-remaining builder + `GET` endpoint (e.g. `.../costs/contract-remaining/?contract_id=` or `.../contracts/{id}/cost-remaining/`) in `apps/api/core/cost_control/` (new service module preferred) + `urls.py`
- [x] T033 [US3] Implement `ledger_report_service.py` and `GET .../costs/ledger-report/` in `apps/api/core/cost_control/` per contract row shape; register in `urls.py` with `view_costs`
- [x] T034 [US3] Frontend Payments panel + ledger report panel on `apps/web/src/app/routes/project-costs.tsx` / `apps/web/src/components/costs/`; API client methods; duplicate-exception dialog; i18n `en.json` / `fa.json`
- [x] T035 [US3] Re-run `test_payment_duplicate_guard.py`, `test_contract_order_remaining.py`, `test_ledger_report.py` until green

**Checkpoint**: US3 independently testable — duplicate-safe payments + remaining + ledger

---

## Phase 6: User Story 4 — Purchase request → order/contract handoff (Priority: P2)

**Goal**: Approved requisition converts to commitment origin; block if not approved (FR-001)

**Independent Test**: Non-approved requisition → 400 `requisition_not_approved`; approved → commitment with `requisition` FK set

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T036 [P] [US4] Write failing pytest create-commitment from non-approved requisition → 400 in `apps/api/core/procurement/tests/test_requisition_create_commitment.py` per `specs/012-cost-commitment-payment/contracts/requisition-to-commitment.md`
- [x] T037 [P] [US4] Write failing pytest approved requisition → 201 with `requisition` FK and optional contract; can approve commitment with CBS in `apps/api/core/procurement/tests/test_requisition_create_commitment.py`

### Implementation for User Story 4

- [x] T038 [US4] Add optional `Commitment.requisition` FK → `procurement.RequisitionHeader` (`null=True`, `blank=True`) in `apps/api/core/cost_control/models.py` + migration (if not already added earlier; otherwise skip duplicate)
- [x] T039 [US4] Implement `create_commitment_from_requisition` in `apps/api/core/cost_control/services/commitment_origin_service.py` (gate: requisition.status must be `approved`; same project); default new commitment `status=draft`
- [x] T040 [US4] Add `POST .../requisitions/{id}/create-commitment/` in `apps/api/core/procurement/urls.py` + view; also validate `requisition` on direct `POST .../commitments/` when provided
- [x] T041 [US4] Frontend “Create commitment” on approved requisition detail under `apps/web/src/app/routes/procurement/` linking to costs commitment form with origin; i18n
- [x] T042 [US4] Re-run `apps/api/core/procurement/tests/test_requisition_create_commitment.py` until green

**Checkpoint**: US4 independently testable — requisition handoff

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, regressions, bilingual polish, quickstart validation

- [x] T043 [P] Update `apps/api/core/cost_control/ENDPOINTS.md` for payment_terms, actual approve/void, payment duplicate exception, contract remaining, ledger-report, create-commitment
- [x] T044 [P] Ensure all new user-facing strings exist in `apps/web/src/locales/en.json` and `apps/web/src/locales/fa.json` (payment terms, payments, ledger, exceptions, requisition handoff)
- [x] T045 Run full FR-CST pytest subset from `specs/012-cost-commitment-payment/quickstart.md` and fix regressions
- [x] T046 [P] Manual/API smoke checklist in `specs/012-cost-commitment-payment/quickstart.md` (optional Playwright only after API green)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: After Setup — **BLOCKS** trustworthy remaining for all stories
- **US1 (Phase 3)**: After Phase 2 — MVP
- **US2 (Phase 4)**: After Phase 2; benefits from US1 commitment but independently testable with fixtures
- **US3 (Phase 5)**: After Phase 2; uses commitments/actuals fixtures; ledger completes US2 separation visibility
- **US4 (Phase 6)**: After Phase 2; ideally after US1 fields (`payment_terms`/`contract`) exist
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

```text
T001–T002 → T003–T005 (remaining)
         → US1 (T006–T013) 🎯 MVP
         → US2 (T014–T024)   [can parallel US1 after Phase 2 if separate owners]
         → US3 (T025–T035)   [after commitments/actuals usable]
         → US4 (T036–T042)   [after US1 commitment fields preferred]
         → T043–T046
```

- **US1**: No dependency on US2–US4
- **US2**: No hard dependency on US1 (can create commitment in fixtures)
- **US3**: Needs commitment (± actual) fixtures; duplicate/ledger independent of US4
- **US4**: Prefers US1 model fields; gate is requisition APPROVED only

### Within Each User Story

1. Failing tests first (confirm red)
2. Model/migration
3. Service
4. Endpoint/serializer
5. Frontend + i18n
6. Re-run story tests green

### Parallel Opportunities

- T001 ∥ T002
- T006 ∥ T007 (US1 tests)
- T014 ∥ T015 ∥ T016 (US2 tests)
- T025 ∥ T026 ∥ T027 ∥ T028 (US3 tests)
- T036 ∥ T037 (US4 tests)
- After Phase 2: Developer A = US1, Developer B = US2 tests+impl (watch `models.py` / migrations conflicts)
- T043 ∥ T044 ∥ T046 after APIs stable

---

## Parallel Example: User Story 3

```bash
# Red: launch US3 failing tests together
Task: "test_payment_duplicate_guard.py"
Task: "test_contract_order_remaining.py"
Task: "test_ledger_report.py"

# Green: implement services then endpoints (sequential on shared create_payment)
Task: "duplicate guard in cbs_services.py"
Task: "contract remaining + ledger_report_service.py"
Task: "urls/views + frontend Payments/ledger panels"
```

---

## Implementation Strategy

### MVP First (Phase 2 + User Story 1)

1. Phase 1 Setup  
2. Phase 2 Remaining TDD (critical)  
3. Phase 3 US1 commitment payment terms + remaining  
4. **STOP and VALIDATE** with `test_remaining_no_double_count.py` + `test_commitment_payment_terms.py`  
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational → correct remaining  
2. US1 → commitments with terms  
3. US2 → actual lifecycle  
4. US3 → payments + ledger (finance-complete P1)  
5. US4 → requisition handoff (P2)  
6. Polish → docs + quickstart suite

### Parallel Team Strategy

1. Together: Phase 1–2  
2. Then: A → US1, B → US2 (coordinate migrations on `cost_control/models.py`)  
3. Then: C → US3, A → US4  
4. Together: Polish pytest subset

---

## Notes

- **TDD**: Every story phase starts with failing tests; verify red before green
- Commitment / ActualCost / Payment remain the single financial spine — no parallel ledger
- Employer IPC collections stay in `011-contracts-ipc` — do not reuse `cost_control.Payment` for IPC
- Quote field constraints from data-model when implementing (blank defaults, status enums, FK nullability)
- Commit after each logical TDD slice (red→green)
- Avoid vague tasks; keep file paths exact

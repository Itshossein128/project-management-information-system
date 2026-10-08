---
description: "Task list for Central Data Model (FR-DATA)"
---

# Tasks: Central Data Model

**Input**: Design documents from `/specs/003-central-data-model/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: `002-core-domain-principles` patterns (`AuditSoftDeleteModel`, `common.money`)

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD recommended; same bar as feature 002). This Spec Kit pass does **not** implement code.

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold test modules and confirm 002 prerequisites

- [X] T001 Verify `common.money` and soft-delete base available from 002 (or document backport) in `apps/api/core/common/money.py` / `common/models.py`
- [X] T002 [P] Create placeholder test modules `apps/api/core/projects/tests/test_central_data_navigation.py`, `apps/api/core/contracts/tests/test_ipc_collections.py`, `apps/api/core/cost_control/tests/test_cbs_commitment.py`, `apps/api/core/master_data/tests/test_org_refs.py`
- [X] T003 [P] Add i18n stub keys for CBS/commitment/stakeholder/collection under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared reference models and Project FK used by later stories

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing tests for OrganizationUnit CRUD uniqueness/parent rules in `apps/api/core/master_data/tests/test_org_refs.py`
- [X] T005 [P] Write failing tests for ContractType catalog create/list in `apps/api/core/master_data/tests/test_contract_types.py`

### Implementation

- [X] T006 Implement `OrganizationUnit` model (code unique max_length 30, name max_length 200, parent self-FK null, status active|inactive) in `apps/api/core/master_data/models.py` + migration
- [X] T007 Implement `ContractType` model (code unique max_length 40, name_fa, name_en, is_active) in `apps/api/core/master_data/models.py` + migration
- [X] T008 [P] Add `Project.owning_unit` FK (null=True, SET_NULL) in `apps/api/core/projects/models.py` + migration; expose on project serializers
- [X] T009 Wire org-wide URLs `/api/v1/organization-units/` and `/api/v1/contract-types/` per `contracts/org-stakeholder-refs.md` in `apps/api/core/master_data/` + root `config/urls.py`
- [X] T010 Re-run T004–T005 until PASS

**Checkpoint**: Org unit + contract type + project owning_unit ready

---

## Phase 3: User Story 1 - Trace activity → project & portfolio (Priority: P1) 🎯 MVP

**Goal**: Explicit drill-up chain and portfolio aggregation across projects

**Independent Test**: navigation payload + portfolio summary for ≥2 projects

### Tests for User Story 1

> Write failing tests first at implement time

- [X] T011 [P] [US1] Failing test: activity serialize includes `project_id`, `wbs_id`, `wbs_code` in `apps/api/core/schedule/tests/test_central_data_activity_embeds.py` (or projects/tests)
- [X] T012 [P] [US1] Failing test: daily-report navigation endpoint returns report/activities/project in `apps/api/core/field_reports/tests/test_central_data_navigation.py`
- [X] T013 [P] [US1] Failing test: portfolio summary returns ≥2 projects for permitted user in `apps/api/core/projects/tests/test_central_data_portfolio.py`

### Implementation for User Story 1

- [X] T014 [US1] Extend activity serializers in `apps/api/core/schedule/serializers.py` (or projects) to embed project/wbs identifiers
- [X] T015 [US1] Implement `GET .../daily-reports/{id}/navigation/` in `apps/api/core/field_reports/` per `contracts/navigation-portfolio.md`
- [X] T016 [US1] Implement `GET /api/v1/portfolio/summary/` in `apps/api/core/projects/portfolio_views.py` with currency-safe totals via `common.money`
- [X] T017 [P] [US1] Add minimal portfolio UI or overview entry in `apps/web/src/app/routes/` (e.g. home/projects aggregate) consuming portfolio API
- [X] T018 [US1] Re-run T011–T013 until PASS

**Checkpoint**: US1 independently verifiable

---

## Phase 4: User Story 2 - Partial IPC collections (Priority: P1)

**Goal**: Append-only collection rows; IPC original amounts immutable

**Independent Test**: two collections; submitted/net unchanged; remaining computed

### Tests for User Story 2

- [X] T019 [P] [US2] Failing tests: POST collection does not change IPC submitted/net; lists collections; remaining in `apps/api/core/contracts/tests/test_ipc_collections.py`
- [X] T020 [P] [US2] Failing test: over-collection rejected with `collection_exceeds_payable` in same file

### Implementation for User Story 2

- [X] T021 [US2] Add `IPCCollection` model per data-model.md in `apps/api/core/contracts/models.py` + migration
- [X] T022 [US2] Implement collection services (append, soft-delete, remaining) in `apps/api/core/contracts/services/` without mutating IPC amount fields
- [X] T023 [US2] Expose REST endpoints under `.../ipcs/{ipc_id}/collections/` and include collections summary on IPC detail serializer
- [X] T024 [US2] UI: collection list + add form on `apps/web/src/app/routes/project-ipc-detail.tsx` / contracts components
- [X] T025 [US2] Re-run T019–T020 until PASS

**Checkpoint**: US2 independently verifiable

---

## Phase 5: User Story 3 - CBS, Commitment, Payment (Priority: P1)

**Goal**: CBS tree + commitment distinct from actual cost + payment remaining

**Independent Test**: create CBS; commitment; payment; assert amounts remain separate

### Tests for User Story 3

- [X] T026 [P] [US3] Failing CBS tree create/list/soft-delete-guard tests in `apps/api/core/cost_control/tests/test_cbs.py`
- [X] T027 [P] [US3] Failing commitment approve requires wbs|cbs; payment cannot exceed commitment in `apps/api/core/cost_control/tests/test_commitment_payment.py`
- [X] T028 [P] [US3] Failing test: ActualCost/Budget accept optional `cbs` FK in `apps/api/core/cost_control/tests/test_cbs_links.py`

### Implementation for User Story 3

- [X] T029 [US3] Implement `CostBreakdownNode` (treebeard) in `apps/api/core/cost_control/models.py` with cbs_code max_length 30 unique per project among non-deleted, cost_type aligned to CostCategory + migration
- [X] T030 [US3] Implement `Commitment` and `Payment` models per data-model.md + migration
- [X] T031 [US3] Add optional `cbs` on Budget/ActualCost and optional `commitment` on ActualCost + migration
- [X] T032 [US3] Services + URLs for `cbs/`, `commitments/`, `payments/` per `contracts/cbs-commitment-payment.md`
- [X] T033 [P] [US3] Frontend CBS tree page + commitment/payment minimal screens under `apps/web/src/app/routes/` and API clients
- [X] T034 [US3] Re-run T026–T028 until PASS

**Checkpoint**: US3 independently verifiable

---

## Phase 6: User Story 4 - Managed reference catalogs (Priority: P2)

**Goal**: Critical refs from catalogs; Unit already exists — wire ContractType into contract create

**Independent Test**: new ContractType used on contract; unit still from catalog

### Tests for User Story 4

- [X] T035 [P] [US4] Failing test: create contract with `contract_type_ref` persists FK in `apps/api/core/contracts/tests/test_contract_type_ref.py`
- [X] T036 [P] [US4] Failing test: free-text-only path not required when ref provided (serializer validation) in same module

### Implementation for User Story 4

- [X] T037 [US4] Add nullable `contract_type_ref` FK on `contracts.Contract` + dual-read serializer; optional data migration seeding ContractType from distinct strings
- [X] T038 [US4] Ensure Unit catalog remains the source for activity/material unit fields on touched serializers (no new free-text-only mandatory unit)
- [X] T039 [US4] Frontend contract form: select from contract-types API in `apps/web/src/app/routes/project-contract-form.tsx`
- [X] T040 [US4] Re-run T035–T036 until PASS

**Checkpoint**: US4 independently verifiable

---

## Phase 7: User Story 5 - Stakeholders & OBS linkage (Priority: P2)

**Goal**: Stakeholder CRUD on project; owning_unit usable end-to-end

**Independent Test**: create stakeholder + set owning_unit; list back

### Tests for User Story 5

- [X] T041 [P] [US5] Failing stakeholder CRUD + influence/interest 1–5 validation in `apps/api/core/projects/tests/test_central_data_stakeholders.py`
- [X] T042 [P] [US5] Failing test: PATCH project `owning_unit` round-trip in `apps/api/core/projects/tests/test_central_data_owning_unit.py`

### Implementation for User Story 5

- [X] T043 [US5] Implement `Stakeholder` model (fields per data-model.md; influence/interest PositiveSmallInteger 1–5 null ok) in `apps/api/core/projects/models.py` + migration
- [X] T044 [US5] Stakeholder viewset + URLs `.../stakeholders/` per contract
- [X] T045 [US5] UI stakeholders tab/page + owning unit select on project settings in `apps/web/src/app/routes/`
- [X] T046 [US5] Re-run T041–T042 until PASS

**Checkpoint**: All stories independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T047 [P] OpenAPI/drf-spectacular summaries for new endpoints
- [X] T048 [P] Verification checklist `specs/003-central-data-model/checklists/verification.md` mapping SC-001–SC-005 to tests
- [X] T049 Run quickstart pytest selection; fix regressions only in touched modules
- [X] T050 [P] `pnpm typecheck` for new TS API types
- [X] T051 Confirm soft-delete/currency rules reused from 002 on Commitment/Payment/Collection/CBS/Stakeholder

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup → Foundational (blocks stories)
- US1, US2, US3 can proceed in parallel after Foundational (different apps)
- US4 depends on Foundational ContractType (T007/T009)
- US5 depends on Foundational OrganizationUnit (T006/T008)
- Polish last

### User Story Dependencies

- **US1**: Independent of US2–US5 after foundation
- **US2**: Independent (contracts app)
- **US3**: Independent (cost_control); may later feed portfolio totals in US1 (optional integration)
- **US4**: Needs ContractType from Phase 2
- **US5**: Needs OrganizationUnit from Phase 2

### Parallel Opportunities

```bash
# After Phase 2:
# A: US1 navigation/portfolio
# B: US2 IPC collections
# C: US3 CBS/commitment/payment
# Then: US4 || US5
```

---

## Implementation Strategy

### MVP

1. Phase 1–2  
2. US1 + US2 + US3 (P1 data chains)  
3. Stop and validate SC-002, SC-003, SC-005 subset  

### Incremental

4. US4 references  
5. US5 stakeholders/OBS  
6. Polish  

### Notes

- Total tasks: **T001–T051** (51)
- Per story approx: US1 8 · US2 7 · US3 9 · US4 6 · US5 6 (+ setup/foundation/polish)
- Suggested MVP: Phases 1–5 (through US3)
- **No implementation in this Spec Kit specify/plan/tasks pass**

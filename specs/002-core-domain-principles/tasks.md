---
description: "Task list for Core Domain Principles & Glossary (TDD)"
---

# Tasks: Core Domain Principles & Glossary

**Input**: Design documents from `/specs/002-core-domain-principles/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: **REQUIRED (TDD)** — for every user story, write failing tests first, confirm FAIL, then implement minimal code, then confirm PASS. Do **not** start implementation until explicitly requested; this file is planning output only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `apps/api/core/`
- Frontend: `apps/web/src/`
- Specs: `specs/002-core-domain-principles/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align feature scaffolding and test layout without implementing domain behavior

- [x] T001 Create test package directories `apps/api/core/common/tests/`, `apps/api/core/projects/tests/` stubs as needed for `test_core_principles_*.py` naming, and note frontend touch points under `apps/web/src/app/locales/` + `apps/web/src/app/lib/money.ts` per plan.md
- [x] T002 [P] Add glossary term key inventory checklist file `specs/002-core-domain-principles/checklists/glossary-keys.md` listing canonical keys from data-model.md (WBS, commitment, actualCost, ipc, ev, pv, ac, risk, issue, baseline, cbs, obs)
- [x] T003 [P] Document TDD run recipe in `specs/002-core-domain-principles/quickstart.md` (already present — verify paths match final test module names)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared helpers and permission codes that all stories need; still TDD for helpers

**⚠️ CRITICAL**: No user story implementation beyond shared helpers until this phase’s tests pass

### Tests first

- [x] T004 [P] Write failing unit tests for currency mix guard in `apps/api/core/common/tests/test_money.py` (same currency sum OK; IRR+IRT without rate → `currency_mix_forbidden`; with explicit rate → converts)
- [x] T005 [P] Write failing unit tests for unset-vs-zero helper behavior in `apps/api/core/common/tests/test_unset.py` (None preserved; 0 preserved; empty string / missing → null mapping rules)

### Implementation

- [x] T006 Implement money helpers (`assert_same_currency`, `sum_amounts`, `convert_explicit`) in `apps/api/core/common/money.py` until T004 passes
- [x] T007 Implement unset/null numeric helpers in `apps/api/core/common/unset.py` until T005 passes
- [x] T008 [P] Add/confirm permission codes needed for capabilities & fiscal lock in `apps/api/core/permissions/constants.py` (reuse `view_project` / `edit_project` where possible; document any new codes)
- [x] T009 Register URL namespaces placeholders only after story tests demand them (do not wire empty endpoints yet)

**Checkpoint**: Money + unset helpers green under pytest; ready for user stories

---

## Phase 3: User Story 1 - Shared glossary in product labels (Priority: P1) 🎯 MVP

**Goal**: Critical FA/EN labels match the FR-CORE glossary for WBS, commitment vs actual cost, and IPC/صورت‌وضعیت

**Independent Test**: Locale/glossary tests pass; spot-check WBS/cost/IPC UI strings

### Tests for User Story 1 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Write failing glossary key assertion tests in `apps/api/core/common/tests/test_glossary_locale_keys.py` (or web test if preferred) that load `apps/web/src/app/locales/fa.json` and `en.json` and assert required glossary strings for WBS, IPC, commitment, actual cost
- [x] T011 [P] [US1] Write failing regression test that commitment and actual-cost labels are distinct keys (not identical copy) in `apps/api/core/common/tests/test_glossary_locale_keys.py`

### Implementation for User Story 1

- [x] T012 [P] [US1] Update Persian glossary/module labels in `apps/web/src/app/locales/fa.json` for WBS («ساختار شکست کار (WBS)»), صورت‌وضعیت, تعهد مالی, هزینه واقعی per data-model.md
- [x] T013 [P] [US1] Update English glossary/module labels in `apps/web/src/app/locales/en.json` to match canonical EN terms
- [x] T014 [US1] Fix any hard-coded conflicting labels on WBS/cost/IPC surfaces under `apps/web/src/app/routes/project-wbs.tsx`, `apps/web/src/app/routes/project-costs.tsx`, `apps/web/src/app/routes/project-contracts.tsx` / IPC components to use locale keys
- [x] T015 [US1] Re-run T010–T011 until PASS; record evidence note in PR/description

**Checkpoint**: US1 glossary consistency independently verifiable

---

## Phase 4: User Story 2 - Universal project record hygiene (Priority: P1)

**Goal**: Project-scoped core records expose id/project/audit fields; approved/final rows cannot be hard-deleted (WBS soft-delete + tenancy)

**Independent Test**: Soft-delete + tenancy pytest on WBS (and sample approved path) pass at 100% deny for unauthorized access

### Tests for User Story 2 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US2] Write failing tests for WBS soft-delete (delete sets `is_deleted`, excluded from default list, restore path if applicable) in `apps/api/core/projects/tests/test_core_principles_wbs_soft_delete.py`
- [x] T017 [P] [US2] Write failing tests that WBS create response includes unique `id`, `project` binding, and creator/timestamp fields in `apps/api/core/projects/tests/test_core_principles_wbs_audit.py`
- [x] T018 [P] [US2] Write failing authorization tests: non-member cannot read/mutate another project’s WBS in `apps/api/core/projects/tests/test_core_principles_wbs_tenancy.py`

### Implementation for User Story 2

- [x] T019 [US2] Extend `apps/api/core/projects/models.py` `WBS` with soft-delete + audit fields (`is_deleted`, `deleted_at`, `created_by`, `updated_by`) per data-model.md constraints
- [x] T020 [US2] Create migration under `apps/api/core/projects/migrations/` backfilling audit fields safely (nullable creators where historical rows lack user)
- [x] T021 [US2] Update WBS delete service/views in `apps/api/core/wbs/services.py` and `apps/api/core/wbs/views.py` to soft-delete only (no physical delete of nodes)
- [x] T022 [US2] Ensure serializers expose audit fields in `apps/api/core/wbs/serializers.py` (or projects serializers used by WBS)
- [x] T023 [US2] Re-run T016–T018 until PASS

**Checkpoint**: US2 record hygiene independently verifiable

---

## Phase 5: User Story 3 - Currency unit safety (Priority: P1)

**Goal**: Project has `currency`; APIs/UI label amounts; mixed IRR/IRT aggregation forbidden without explicit rate

**Independent Test**: Contract tests for project currency + mix guard; UI shows unit beside amounts on costs/cash

### Tests for User Story 3 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US3] Write failing API tests that project create/retrieve includes `currency` default `IRR` and accepts `IRT` in `apps/api/core/projects/tests/test_core_principles_currency_api.py`
- [x] T025 [P] [US3] Write failing service/API tests for `currency_mix_forbidden` when aggregating mixed units without rate in `apps/api/core/projects/tests/test_core_principles_currency_mix.py`
- [x] T026 [P] [US3] Write failing frontend unit/helper tests (or typed helper assertions) for display labeling in `apps/web/src/app/lib/money.test.ts` (create if test runner present; otherwise document API-only gate and UI checklist)

### Implementation for User Story 3

- [x] T027 [US3] Add `currency` field (`IRR`|`IRT`, default `IRR`, max_length 3) to `apps/api/core/projects/models.py` `Project` + migration
- [x] T028 [US3] Expose `currency` on project serializers/views in `apps/api/core/projects/serializers.py` and related create wizard payload
- [x] T029 [US3] Wire financial aggregate call sites that this feature owns to `common.money` guards (minimum: a shared helper used by cost summary or cash summary service — pick one primary path in `apps/api/core/cost_control/services/` or `apps/api/core/cash_flow/services/`)
- [x] T030 [P] [US3] Implement `apps/web/src/app/lib/money.ts` formatters that always append currency label
- [x] T031 [US3] Update costs/cash-flow UI surfaces under `apps/web/src/components/costs/` and `apps/web/src/components/cashflow/` to display currency from project
- [x] T032 [US3] Re-run T024–T026 until PASS

**Checkpoint**: US3 currency safety independently verifiable

---

## Phase 6: User Story 4 - Distinguish unset, zero, and approval states (Priority: P2)

**Goal**: Representative numeric field round-trips null vs 0; approval states remain distinct in API/UI

**Independent Test**: Serializer/API tests for chosen field; UI empty ≠ 0

### Tests for User Story 4 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T033 [P] [US4] Write failing tests for a chosen representative nullable quantity (e.g. daily report `quantity_measured` or activity progress field) proving null ≠ 0 in `apps/api/core/field_reports/tests/test_core_principles_unset_vs_zero.py` (or schedule progress tests if that field is chosen)
- [x] T034 [P] [US4] Write failing tests that unapproved vs approved status values remain distinct in list filters for the same module in the same test module

### Implementation for User Story 4

- [x] T035 [US4] Adjust model/serializer nullability and defaults for the chosen field so blank → `null` not `0` in the owning app serializers
- [x] T036 [US4] Update corresponding form control in `apps/web/src/components/daily_reports/` (or progress drawer) to submit `null` for empty inputs and show distinct empty vs zero
- [x] T037 [US4] Re-run T033–T034 until PASS

**Checkpoint**: US4 unset/approval distinction independently verifiable

---

## Phase 7: User Story 5 - Actionable notifications (Priority: P2)

**Goal**: Notifications include responsible party, due date when time-bound, and deep link

**Independent Test**: Create/list contract tests per `contracts/notifications-actionable.md`

### Tests for User Story 5 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US5] Write failing API/service tests requiring `responsible_user` + `link` for actionable types and `due_at` for time-bound types in `apps/api/core/notifications/tests/test_actionable_notifications.py`
- [x] T039 [P] [US5] Write failing serialization tests that list/detail returns `responsible_user`, `due_at`, `link` in the same file

### Implementation for User Story 5

- [x] T040 [US5] Add `responsible_user` (FK, null=True) and `due_at` (DateTime, null=True) to `apps/api/core/notifications/models.py` + migration
- [x] T041 [US5] Enforce create rules in notification services/serializers under `apps/api/core/notifications/`
- [x] T042 [US5] Update `apps/web/src/components/notifications/NotificationPanel.tsx` (and related) to render owner, deadline, and link
- [x] T043 [US5] Re-run T038–T039 until PASS

**Checkpoint**: US5 actionable notifications independently verifiable

---

## Phase 8: User Story 6 - Optional capability toggles per project (Priority: P2)

**Goal**: Admin can disable a capability; history readable; new mutations blocked; other flows intact

**Independent Test**: Capabilities API + mutate-block tests per `contracts/project-capabilities.md`

### Tests for User Story 6 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T044 [P] [US6] Write failing CRUD/list tests for `/capabilities/` in `apps/api/core/projects/tests/test_core_principles_capabilities_api.py`
- [x] T045 [P] [US6] Write failing tests: disabled capability → domain POST returns `capability_disabled`; GET history still 200 in `apps/api/core/projects/tests/test_core_principles_capabilities_enforce.py` (target one module e.g. risk)

### Implementation for User Story 6

- [x] T046 [US6] Add `ProjectCapabilitySetting` model (fields per data-model.md: `capability_key` max_length 64, unique with project, `enabled`, `mode` in `required|optional|disabled`) in `apps/api/core/projects/` + migration
- [x] T047 [US6] Implement list/update endpoints and seed defaults per `specs/002-core-domain-principles/contracts/project-capabilities.md`
- [x] T048 [US6] Add enforcement helper used by at least one domain create path (e.g. `apps/api/core/risk/`) returning `403/409` with `capability_disabled`
- [x] T049 [US6] Add capability toggles UI on `apps/web/src/app/routes/project-settings.tsx` and hide nav entry when disabled via `apps/web/src/components/navigation/` config consumers
- [x] T050 [US6] Re-run T044–T045 until PASS

**Checkpoint**: US6 capability toggles independently verifiable

---

## Phase 9: User Story 7 - Fiscal period lock and duplicate transaction warning (Priority: P3)

**Goal**: Closed periods block ordinary financial edits; corrective path audited; duplicate document refs warn until acknowledged

**Independent Test**: Fiscal lock + duplicate warning tests per `contracts/fiscal-period-lock.md`

### Tests for User Story 7 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T051 [P] [US7] Write failing API tests for creating fiscal period locks (overlap rejected; fields `period_start`/`period_end`/`reason`) in `apps/api/core/projects/tests/test_core_principles_fiscal_lock_api.py`
- [x] T052 [P] [US7] Write failing tests: mutate in locked period → `fiscal_period_locked`; with `corrective=true` + `correction_reason` → allowed + audited in `apps/api/core/projects/tests/test_core_principles_fiscal_lock_enforce.py`
- [x] T053 [P] [US7] Write failing tests for duplicate `document_ref` warning and `acknowledge_warnings` gate in `apps/api/core/cost_control/tests/test_core_principles_duplicate_document.py` (or cash_flow equivalent)

### Implementation for User Story 7

- [x] T054 [US7] Add `FiscalPeriodLock` model per data-model.md in `apps/api/core/projects/` + migration (`period_end >= period_start`, `reason` min length 3, `is_active`)
- [x] T055 [US7] Implement fiscal lock endpoints per `specs/002-core-domain-principles/contracts/fiscal-period-lock.md`
- [x] T056 [US7] Enforce lock on at least one financial write path (`apps/api/core/cost_control/` ActualCost create/update and/or `apps/api/core/cash_flow/` transaction write)
- [x] T057 [US7] Implement duplicate document warning + `acknowledge_warnings` on the same write path
- [x] T058 [US7] Add minimal settings UI for closing a period on `apps/web/src/app/routes/project-settings.tsx`
- [x] T059 [US7] Re-run T051–T053 until PASS

**Checkpoint**: All user stories independently functional under TDD

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Evidence, docs, and regression sweep — still no speculative refactors

- [x] T060 [P] Run full feature pytest selection from quickstart.md and attach evidence summary in `specs/002-core-domain-principles/checklists/verification.md`
- [x] T061 [P] Run `pnpm typecheck` and fix only type errors introduced by this feature in `apps/web/`
- [x] T062 [P] Update Scope Map note (optional short bullet) only if user requests docs sync — otherwise skip
- [x] T063 Execute bilingual manual smoke for US1/US3/US5 from quickstart.md and record pass/fail in verification checklist
- [x] T064 Confirm SC-001–SC-008 mapped to tests in `specs/002-core-domain-principles/checklists/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS story implementation (helpers)
- **US1 / US2 / US3 (P1)**: Depend on Foundational; can proceed in parallel after T009
- **US4 / US5 / US6 (P2)**: Depend on Foundational; US4 may use unset helpers from Phase 2; US6 independent of US5
- **US7 (P3)**: Depends on Foundational; may reuse money/project settings UI from US3/US6 but must remain testable alone
- **Polish**: After desired stories complete

### User Story Dependencies

- **US1**: Independent (locales)
- **US2**: Independent (WBS hygiene)
- **US3**: Uses Phase 2 money helpers
- **US4**: Uses Phase 2 unset helpers
- **US5**: Independent (notifications)
- **US6**: Independent (capabilities)
- **US7**: Independent financially; settings UI may share page with US6

### Within Each User Story

1. Write failing tests  
2. Confirm FAIL  
3. Implement models → migrations → services → endpoints → UI  
4. Confirm PASS  
5. Checkpoint before next story

### Parallel Opportunities

```bash
# After Phase 2:
# Dev A: US1 glossary tests+locales
# Dev B: US2 WBS soft-delete tests+model
# Dev C: US3 currency tests+field

# Later parallel:
# US5 notifications || US6 capabilities
# US4 unset || US7 fiscal (different apps preferred)
```

---

## Parallel Example: User Story 2

```bash
Task: "T016 failing WBS soft-delete tests in apps/api/core/projects/tests/test_core_principles_wbs_soft_delete.py"
Task: "T017 failing WBS audit field tests in apps/api/core/projects/tests/test_core_principles_wbs_audit.py"
Task: "T018 failing WBS tenancy tests in apps/api/core/projects/tests/test_core_principles_wbs_tenancy.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Phase 1–2  
2. US1 glossary  
3. US2 soft-delete/tenancy  
4. US3 currency  
5. **STOP** — validate P1 acceptance + SC-001–SC-004 subset  

### Incremental Delivery

1. Add US4 unset/zero  
2. Add US5 notifications  
3. Add US6 capabilities  
4. Add US7 fiscal + duplicate warnings  
5. Polish / verification checklist  

### TDD reminder

- No story is “done” without a previously failing test that now passes  
- Do **not** implement any of T004+ until the user explicitly asks to implement  

---

## Notes

- Total tasks: **T001–T064** (64)
- Per story (approx): US1 6 · US2 8 · US3 9 · US4 5 · US5 6 · US6 7 · US7 9 (+ setup/foundation/polish)
- Suggested MVP: Phases 1–5 (US1–US3)
- Format validation: all tasks use `- [ ]`, Task IDs, story labels where required, and file paths
- **No implementation started in this Spec Kit pass**

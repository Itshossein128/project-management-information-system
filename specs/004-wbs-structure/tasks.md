---
description: "Task list for WBS Structure (FR-WBS)"
---

# Tasks: WBS Structure

**Input**: Design documents from `/specs/004-wbs-structure/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: `002-core-domain-principles` (soft-delete/audit), existing `wbs` + `project_templates`

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002/003). Implemented via `/speckit-implement` (TDD).

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold tests and confirm baseline WBS APIs

- [X] T001 Verify existing WBS tree CRUD/move/soft-delete baseline in `apps/api/core/wbs/` (smoke read of services/views)
- [X] T002 [P] Create placeholder test modules `apps/api/core/wbs/tests/test_wbs_structure_fields.py`, `apps/api/core/wbs/tests/test_wbs_delete_guards.py`, `apps/api/core/wbs/tests/test_wbs_cycle_move.py`, `apps/api/core/project_templates/tests/test_wbs_template_immutability.py`
- [X] T003 [P] Add i18n stub keys for WBS status/acceptance/responsible/delete reasons under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema fields all stories share

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing serializer/model expectations for `responsible`, `acceptance_criteria`, `status` on create/list in `apps/api/core/wbs/tests/test_wbs_structure_fields.py`

### Implementation

- [X] T005 Add `responsible` FK (User, null), `acceptance_criteria` TextField, `status` CharField with choices on `projects.WBS` in `apps/api/core/projects/models.py` + migration
- [X] T006 Extend `WBSCreateSerializer` / `WBSUpdateSerializer` / tree+flat serializers in `apps/api/core/wbs/serializers.py` to expose new fields
- [X] T007 Wire create/update services in `apps/api/core/wbs/services.py` / views to persist new fields with project-scoped responsible user validation
- [X] T008 Re-run T004 until PASS

**Checkpoint**: Node metadata fields available on API

---

## Phase 3: User Story 1 - Multi-level tree + package metadata (Priority: P1) 🎯 MVP

**Goal**: ≥3-level tree; responsible + acceptance on work package; cycle rejected

**Independent Test**: create three levels; set package fields; move under descendant fails

### Tests for User Story 1

- [X] T009 [P] [US1] Failing test: create three-level tree and set responsible/acceptance/status on leaf in `apps/api/core/wbs/tests/test_wbs_structure_fields.py`
- [X] T010 [P] [US1] Failing test: move node under its descendant returns cycle error in `apps/api/core/wbs/tests/test_wbs_cycle_move.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement explicit cycle pre-check in `move_wbs_node` (`apps/api/core/wbs/services.py`) with stable error code `wbs_cycle`
- [X] T012 [US1] Ensure tree list response includes new fields end-to-end (views already use serializers)
- [X] T013 [P] [US1] UI: expose responsible, acceptance criteria, status on `apps/web/src/app/routes/project-wbs.tsx` / WBS form components
- [X] T014 [US1] Re-run T009–T010 until PASS

**Checkpoint**: US1 independently verifiable

---

## Phase 4: User Story 2 - Delete dependency protection (Priority: P1)

**Goal**: Reject delete when cost, progress, documents (plus existing children/activities)

**Independent Test**: seeded dependencies → 409 with reason; clean leaf → soft-delete

### Tests for User Story 2

- [X] T015 [P] [US2] Failing tests: delete blocked for Budget/ActualCost, Document.related_wbs, ActivityProgress path in `apps/api/core/wbs/tests/test_wbs_delete_guards.py`
- [X] T016 [P] [US2] Failing test: clean leaf delete still 204 / soft-deleted in same module

### Implementation for User Story 2

- [X] T017 [US2] Extend `delete_wbs_node` dependency matrix per `contracts/wbs-delete-guards.md` in `apps/api/core/wbs/services.py`
- [X] T018 [US2] Map conflicts to structured API responses in `apps/api/core/wbs/views.py` (stable `code` values)
- [X] T019 [P] [US2] UI: show localized conflict message on delete failure in WBS UI
- [X] T020 [US2] Re-run T015–T016 until PASS

**Checkpoint**: US2 independently verifiable

---

## Phase 5: User Story 3 - Template immutability (Priority: P2)

**Goal**: Template edits never silently rewrite applied project WBS; force-replace is explicit and safe

**Independent Test**: apply → mutate template → project unchanged; force blocked when dependencies exist

### Tests for User Story 3

- [X] T021 [P] [US3] Failing/regression test: after apply, changing `ProjectTemplateWBS` does not change project nodes in `apps/api/core/project_templates/tests/test_wbs_template_immutability.py`
- [X] T022 [P] [US3] Failing test: `force=True` apply refuses (or soft-deletes safely) when project WBS has cost/document dependencies

### Implementation for User Story 3

- [X] T023 [US3] Confirm copy-on-write path in `project_templates/services.py`; document no live sync
- [X] T024 [US3] Harden `force=True` replace: no hard-delete of dependent nodes; align with soft-delete + FR-WBS-006 guards
- [X] T025 [P] [US3] Optional UI copy clarifying templates do not auto-update live projects (`settings-templates` / create wizard)
- [X] T026 [US3] Re-run T021–T022 until PASS

**Checkpoint**: All stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T027 [P] OpenAPI/drf-spectacular summaries for updated WBS endpoints
- [X] T028 [P] Verification checklist `specs/004-wbs-structure/checklists/verification.md` mapping SC-001–SC-004 to tests
- [X] T029 Run quickstart pytest selection; fix regressions only in touched modules
- [X] T030 [P] `pnpm typecheck` for touched TS
- [X] T031 Empty-WBS warning hook for schedule/progress entry points (API flag or UI banner) per edge case
- [X] T032 Confirm soft-delete + code propagate still pass existing `wbs/tests/` suite

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup → Foundational (blocks stories)
- US1 and US2 can proceed in parallel after Foundational (same app — coordinate on `services.py`)
- US3 depends on delete guards (T017) if force-replace reuses them
- Polish last

### User Story Dependencies

- **US1**: Foundational fields + cycle guard
- **US2**: Independent of US1 UI; shares `delete_wbs_node`
- **US3**: Template service; force path should call US2 guards

### Parallel Opportunities

```bash
# After Phase 2:
# A: US1 fields UI + cycle tests
# B: US2 delete guard tests/impl
# Then: US3 immutability
```

---

## Implementation Strategy

### MVP

1. Phase 1–2  
2. US1 + US2 (P1 tree metadata + delete safety)  
3. Stop and validate SC-001, SC-002, SC-004  

### Incremental

4. US3 template immutability / force harden  
5. Polish  

### Notes

- Total tasks: **T001–T032** (32)
- Per story approx: US1 6 · US2 6 · US3 6 (+ setup/foundation/polish)
- Suggested MVP: Phases 1–4
- Implementation completed for T001–T032

---

## Phase 7: Convergence

**Purpose**: Close remaining gaps found by `/speckit-converge` against spec, plan, and constitution (post T001–T032 implement).

- [X] T033 Enforce project-scoped `responsible` (active ProjectMember) in `apps/api/core/wbs/services.py` `_resolve_responsible_id` + tests per plan:T007 / Constitution II (partial)
- [X] T034 [P] [US1] Expose `responsible` select and show responsible/acceptance_criteria in view mode on `apps/web/src/components/wbs/wbs-node.tsx` (and API client if needed) per US1/AC3, FR-004 (partial)
- [X] T035 [P] Add empty-WBS warning on schedule/progress (and/or activities) entry routes when project has no non-deleted WBS packages per Edge case / T031 (partial)
- [X] T036 [P] Soft-warn when progress/budget flows use a work package missing responsible or acceptance_criteria (non-blocking) per Edge case SHOULD (partial)


---
description: "Task list for Project Registration & Kickoff Gap Closure (FR-PRJ)"
---

# Tasks: Project Registration & Kickoff Gap Closure

**Input**: Design documents from `/specs/008-project-registration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: existing `projects` CRUD/create wizard; soft-delete/audit + currency (002); owning unit / stakeholders (003); schedule baseline lock hooks (005) for FR-PRJ-004 gates

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002–007). Implemented via `/speckit-implement` (TDD).

**Organization**: By user story for independent delivery. Priority order: US1 (P1) → US3 (P1) → US2 (P2) → US4 (P2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 maps to spec user stories
- Exact file paths required

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm project baseline and scaffold test/i18n stubs

- [X] T001 Verify existing `ProjectViewSet`, `ProjectCreateSerializer`/`ProjectUpdateSerializer`, `create_project_with_creator`, and `ProjectStatus` choices in `apps/api/core/projects/` (read `models.py`, `serializers.py`, `views.py`, `services.py`)
- [X] T002 [P] Create placeholder test modules `apps/api/core/projects/tests/test_project_registration_lifecycle.py`, `test_project_registration_charter.py`, `test_project_registration_change_request.py`, `test_project_registration_gates.py`
- [X] T003 [P] Add i18n stub keys for project lifecycle statuses (draft, pending_approval, active, suspended, completed, archived), activation gate errors, kickoff charter labels, change-request status/actions, protected-field messages under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema, permission, and route mounts all stories need

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing expectations for expanded `ProjectStatus` values `draft|pending_approval|active|suspended|completed|archived` and create default `draft` in `apps/api/core/projects/tests/test_project_registration_lifecycle.py`
- [X] T005 [P] Write failing expectations for Project identity fields `purpose` Text blank, `scope_description` Text blank, `main_deliverables` Text blank, `contract_number` Char(60) blank, `budget_approved_at` DateTime null, `budget_approved_by` FK User null in same module
- [X] T006 [P] Write failing expectation that `approve_project` exists in `PERMISSIONS` / role seeds in `apps/api/core/projects/tests/test_project_registration_lifecycle.py` or `permissions/tests/`

### Implementation

- [X] T007 Expand `ProjectStatus` in `apps/api/core/projects/models.py` to `draft|pending_approval|active|suspended|completed|archived`; default new projects to `draft`; migration maps `handed_over`→`completed`; backfill existing `active` with `contract_amount` set → `budget_approved_at≈created_at` per research D9
- [X] T008 Add Project fields `purpose`, `scope_description`, `main_deliverables`, `contract_number` Char(60) blank, `budget_approved_at`, `budget_approved_by` in `apps/api/core/projects/models.py` + migration
- [X] T009 Add stub models `ProjectKickoffCharter` (OneToOne) and `ProjectChangeRequest` (reason Text min 10, status `draft|submitted|approved|rejected|cancelled`, `proposed_changes` JSON, `previous_values` JSON) per `data-model.md` in `apps/api/core/projects/models.py` + migration
- [X] T010 Add `approve_project` to `apps/api/core/permissions/constants.py` and seed default roles (e.g. `project_manager`) via migration pattern used for HR perms
- [X] T011 [P] Scaffold service modules `apps/api/core/projects/services/lifecycle_service.py`, `charter_service.py`, `change_request_service.py`, and `readiness.py` (baseline/commitment assert helpers) with URL stubs in `apps/api/core/projects/urls.py` for `submit/`, `approve/`, `reject/`, `suspend/`, `resume/`, `complete/`, `archive/`, `kickoff-charter/`, `change-requests/`
- [X] T012 Re-run T004–T006 until schema/permission smoke PASS (views may still be incomplete)

**Checkpoint**: Shared schema + permission + route mounts ready

---

## Phase 3: User Story 1 - Create draft and submit for approval (Priority: P1) 🎯 MVP

**Goal**: Create as draft with identity fields; submit/approve/reject; activation gates (PM + scope + budget); block definitive baseline/commitment while draft/pending

**Independent Test**: Create draft → submit → approve without gates fails with `missing`; complete gates → active; draft cannot lock baseline

### Tests for User Story 1

- [X] T013 [P] [US1] Failing API tests for `POST /api/v1/projects/` returns `status=draft` and persists purpose/scope/deliverables/contract_number per `contracts/project-lifecycle.md` in `apps/api/core/projects/tests/test_project_registration_lifecycle.py`
- [X] T014 [P] [US1] Failing tests for `submit/` → `pending_approval`; `approve/` without PM/scope/amount → 400 `activation_gates_failed`; with gates → `active` + `budget_approved_at` set
- [X] T015 [P] [US1] Failing tests for draft/pending: lock baseline → 400 `project_not_active_for_baseline`; binding commitment create → 400 `project_not_active_for_commitment` in `apps/api/core/projects/tests/test_project_registration_gates.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement `lifecycle_service.submit_for_approval|approve|reject` with activation gate check (`project_manager`, nonempty `scope_description`, `contract_amount` not null → stamp `budget_approved_at`) in `apps/api/core/projects/services/lifecycle_service.py`
- [X] T017 [US1] Wire serializers + ViewSet actions (`submit`, `approve`, `reject`) and strip free-form illegal `status` PATCH in `apps/api/core/projects/serializers.py`, `views.py`; extend create/update field lists for identity fields
- [X] T018 [US1] Implement `readiness.assert_project_allows_definitive_baseline` / `assert_project_allows_binding_commitment` (allow only `status==active`) in `apps/api/core/projects/services/readiness.py`; call from `apps/api/core/schedule/services/baseline_service.py` and binding commitment create entry (Contract or cost_control Commitment per research D7)
- [X] T019 [P] [US1] UI: create wizard defaults/saves draft; status bar Submit/Approve/Reject; surface `activation_gates_failed.missing` in `apps/web/src/app/routes/project-create-wizard.tsx`, project overview/settings status UI, `apps/web/src/app/lib/api/projects.ts`
- [X] T020 [US1] Re-run T013–T015 until PASS

**Checkpoint**: US1 independently verifiable (MVP)

---

## Phase 4: User Story 3 - Controlled change of approved fields (Priority: P1)

**Goal**: Block direct PATCH of protected fields when active; project change-request lifecycle with reason and approval

**Independent Test**: Active project PATCH employer → 400; CR create→submit→approve updates field; second open CR → 409

### Tests for User Story 3

- [X] T021 [P] [US3] Failing tests: active project PATCH of `start_date|planned_finish_date|contract_amount|employer|scope_description` → 400 `protected_field_requires_change_request` in `apps/api/core/projects/tests/test_project_registration_change_request.py`
- [X] T022 [P] [US3] Failing tests for CR create (reason min 10, proposed_changes keys ⊆ protected set), submit, approve applies values + sets previous_values, reject/cancel leave project unchanged, `change_request_already_open` 409 per `contracts/project-change-requests.md`

### Implementation for User Story 3

- [X] T023 [US3] Implement `change_request_service` create/update/submit/approve/reject/cancel in `apps/api/core/projects/services/change_request_service.py`; enforce one open CR per project
- [X] T024 [US3] Wire CR ViewSet/urls + serializers; enforce protected-field block on `ProjectUpdateSerializer` when status in `active|suspended|completed|archived` in `apps/api/core/projects/serializers.py`, `views.py`, `urls.py`
- [X] T025 [P] [US3] UI: settings shows Request change for protected fields; CR list/form/approve in `apps/web/src/app/routes/project-settings.tsx` and/or `apps/web/src/components/projects/`; API helpers in `apps/web/src/app/lib/api/projects.ts`
- [X] T026 [US3] Re-run T021–T022 until PASS

**Checkpoint**: US3 independently verifiable

---

## Phase 5: User Story 2 - Project kickoff charter (Priority: P2)

**Goal**: Persist and display kickoff charter (justification, success criteria, constraints, assumptions, key stakeholders summary, PM authority)

**Independent Test**: PUT charter → GET returns all six fields; visible on project detail

### Tests for User Story 2

- [X] T027 [P] [US2] Failing API tests for GET 404 when absent; PUT/PATCH upsert with fields justification, success_criteria, constraints, assumptions, key_stakeholders_summary, pm_authority per `contracts/kickoff-charter.md` in `apps/api/core/projects/tests/test_project_registration_charter.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement `charter_service` get/upsert and views/serializers under `…/kickoff-charter/` in `apps/api/core/projects/services/charter_service.py`, `serializers.py`, `views.py`, `urls.py`; deny mutate when archived (non-admin)
- [X] T029 [P] [US2] UI charter panel on overview or settings in `apps/web/src/app/routes/project-overview.tsx` (or dedicated component under `apps/web/src/components/projects/`); wire `apps/web/src/app/lib/api/projects.ts`
- [X] T030 [US2] Re-run T027 until PASS

**Checkpoint**: US2 independently verifiable

---

## Phase 6: User Story 4 - Lifecycle statuses and archive rules (Priority: P2)

**Goal**: suspend/resume/complete/archive; suspended blocks new locked baseline; archived read-only for non–system-admin; duplicate code message

**Independent Test**: suspend → baseline lock 400; archive → non-admin PATCH 403; duplicate code clear error

### Tests for User Story 4

- [X] T031 [P] [US4] Failing tests for `suspend/`/`resume/`/`complete/`/`archive/` transitions and `invalid_status_transition` in `apps/api/core/projects/tests/test_project_registration_lifecycle.py`
- [X] T032 [P] [US4] Failing tests: suspended → baseline lock 400; archived non-admin mutate → 403 `project_archived`; duplicate `project_code` → clear uniqueness error in `test_project_registration_gates.py` / lifecycle module

### Implementation for User Story 4

- [X] T033 [US4] Complete lifecycle actions suspend/resume/complete/archive + archive mutation guard (system admin = superuser or global `admin` group) in `apps/api/core/projects/services/lifecycle_service.py` and views
- [X] T034 [P] [US4] UI status actions + list `?status=` filter + archived read-only UX in `apps/web/src/app/routes/project-list.tsx`, overview status bar, settings
- [X] T035 [US4] Re-run T031–T032 until PASS

**Checkpoint**: US4 independently verifiable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, localization completeness, validation evidence

- [X] T036 [P] Update project API docs / outline (if present) or add brief endpoint notes under `apps/api/core/projects/` for lifecycle, charter, change-requests, gates
- [X] T037 [P] Ensure fa/en labels for all new statuses, gate codes, CR statuses used in UI are complete in `apps/web/src/app/locales/fa.json` and `en.json`
- [X] T038 Run `apps/api/core` pytest for `projects/tests/test_project_registration_*.py` and confirm migration applies; optionally Playwright smoke for create→approve→CR per `quickstart.md`
- [X] T039 Mark all completed tasks `[X]` in `specs/008-project-registration/tasks.md` and record verification evidence categories (pytest, migration, UI smoke if run)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US3 (Phase 4)**: After Foundational (ideally after US1 so “active” projects exist for CR tests); can use factory to force `active` if parallel
- **US2 (Phase 5)**: After Foundational; independent of US3
- **US4 (Phase 6)**: After US1 lifecycle actions exist (extends same service)
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: No story dependency — MVP
- **US3 (P1)**: Needs active project semantics from US1 (or test factory setting status=active + budget_approved_at)
- **US2 (P2)**: Independent after Foundational models
- **US4 (P2)**: Extends US1 lifecycle_service; shares readiness gates with US1

### Parallel Opportunities

- T002/T003; T004–T006; T013–T015; T021–T022; T027; T031–T032
- US2 UI (T029) can proceed in parallel with US3 backend if models exist
- Do **not** parallelize conflicting edits to `models.py` / `serializers.py` / `views.py` without coordination

### Parallel Example: User Story 1

```bash
# Tests in parallel:
Task: T013 create draft contract tests
Task: T014 submit/approve gate tests
Task: T015 baseline/commitment gate tests

# After T016–T018 backend:
Task: T019 UI wizard + status bar
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational  
3. Phase 3 US1  
4. **STOP and VALIDATE** via Scenario A in `quickstart.md`  
5. Demo draft→approve + baseline gate  

### Incremental Delivery

1. US1 → lifecycle MVP  
2. US3 → protected field CR  
3. US2 → charter  
4. US4 → suspend/archive polish  
5. Phase 7 docs + full pytest  

### Suggested MVP scope

**US1 only** (draft create, submit/approve, activation gates, baseline/commitment block while unapproved).

---

## Notes

- Project change requests ≠ schedule change requests (`schedule.ScheduleChangeRequest`)
- `contract_amount` remains budget ceiling; do not rename broadly
- Constitution: server-side gates; bilingual copy; migration preserves legacy actives
- No Spec Kit implement until `/speckit-implement` is requested

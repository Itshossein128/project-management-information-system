# Tasks: Stakeholders, Documents, Decisions & Workflow

**Input**: Design documents from `/specs/016-stakeholders-docs-workflow/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*, quickstart.md

**Tests**: **TDD required for every task slice** (user requested). Pattern: write failing pytest (or UI assertion where noted) → confirm red → minimal production change → re-run green → refactor. Do not mark a task done without the named test evidence for that slice.

**Organization**: Phases by user story (US1–US4). Foundational = `workflow` app shell + `view_sensitive_contacts` permission + shared URL/registration used by later stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 for story phases only
- Exact file paths in every task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature context and extension points before coding

- [x] T001 Confirm `.specify/feature.json` has `"feature_directory": "specs/016-stakeholders-docs-workflow"` and review `specs/016-stakeholders-docs-workflow/plan.md` TDD discipline
- [x] T002 [P] Inventory extension points in `apps/api/core/projects/{models.py,stakeholder_views.py}`, `apps/api/core/documents/{models.py,views.py,urls.py,services/document_service.py}`, `apps/api/core/permissions/constants.py`, and UI `apps/web/src/app/{routes/project-stakeholders.tsx,routes/project-documents.tsx,lib/api/documents.ts}`; note gaps vs `specs/016-stakeholders-docs-workflow/research.md`

---

## Phase 2: Foundational — Permissions & workflow app shell (Blocking)

**Purpose**: Add `view_sensitive_contacts` permission and a registered empty `workflow` Django app with URL mount so US1–US4 can land models/endpoints without redoing project wiring. Blocks trustworthy story work that depends on ACL or workflow imports.

**⚠️ CRITICAL**: No story may expose stakeholder email/phone without the redact rule, or invent a second workflow engine outside `workflow`.

### Tests (TDD — write first, must FAIL)

- [x] T003 [P] Write failing pytest: `view_sensitive_contacts` is present in `PERMISSIONS` / `ALL_PERMISSION_CODENAMES` and included in `project_manager` (and `document_controller`) default role lists in `apps/api/core/permissions/tests/test_view_sensitive_contacts_permission.py` (create file; assert against `apps/api/core/permissions/constants.py`)
- [x] T004 [P] Write failing pytest: `workflow` app is importable and listed in `INSTALLED_APPS` (`from workflow.apps import WorkflowConfig`) in `apps/api/core/workflow/tests/test_app_registered.py`

### Implementation

- [x] T005 Add `'view_sensitive_contacts': 'View stakeholder sensitive contact fields'` to `PERMISSIONS` in `apps/api/core/permissions/constants.py` and grant it on `project_manager` + `document_controller` (and any role that already has full project edit if needed for parity)
- [x] T006 Scaffold `apps/api/core/workflow/` (`apps.py`, `__init__.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `services/__init__.py`, `tests/__init__.py`, `migrations/__init__.py`, `ENDPOINTS.md` stub); register `'workflow'` in `apps/api/core/config/settings.py` `INSTALLED_APPS`; include project-nested urls from `apps/api/core/config/urls.py` (or projects include pattern used by other apps) under `/api/v1/projects/<uuid:project_pk>/`
- [x] T007 Re-run `apps/api/core/permissions/tests/test_view_sensitive_contacts_permission.py` and `apps/api/core/workflow/tests/test_app_registered.py` until green

**Checkpoint**: Permission + workflow shell green; ready for story work

---

## Phase 3: User Story 1 — Stakeholders, meetings, and actions (Priority: P1) 🎯 MVP

**Goal**: Stakeholder with relationship owner + contact redaction; structured meeting actions with open-actions report (FR-001, FR-003, FR-013; SC-001, SC-005). Communication plan / matrix deferred to US4.

**Independent Test**: Create stakeholder with relationship_owner → list shows it; viewer without contact permission sees redacted email/phone; create meeting with two open actions → `GET .../meeting-actions/open/` lists both with owners

### Tests for User Story 1 (TDD — FAIL before implement)

- [x] T008 [P] [US1] Write failing pytest POST stakeholder with `relationship_owner` → appears in GET list with that field in `apps/api/core/projects/tests/test_stakeholder_contacts_acl.py` per `specs/016-stakeholders-docs-workflow/contracts/stakeholders-meetings.md` (FR-001)
- [x] T009 [P] [US1] Write failing pytest: user with `view_project` but without `view_sensitive_contacts`/`edit_project` gets `email`/`phone` null (or omitted) and `contacts_redacted: true`; user with `view_sensitive_contacts` gets full values in `apps/api/core/projects/tests/test_stakeholder_contacts_acl.py` (FR-013)
- [x] T010 [P] [US1] Write failing pytest POST meeting then two nested actions (`description` required, `owner` FK User \| null, `due_date` date \| null, `status` open\|done default open) → `GET .../meeting-actions/open/` returns both in `apps/api/core/documents/tests/test_meeting_open_actions.py` (FR-003, SC-005)
- [x] T011 [P] [US1] Write failing pytest mark action `status=done` → leaves open report; `?overdue=true` returns only open actions with `due_date` &lt; today in `apps/api/core/documents/tests/test_meeting_open_actions.py`

### Implementation for User Story 1

- [x] T012 [US1] Add `relationship_owner` FK User \| null on `Stakeholder` in `apps/api/core/projects/models.py` + migration `apps/api/core/projects/migrations/00xx_fr_col_stakeholder_owner.py`
- [x] T013 [US1] Extend `StakeholderSerializer` / `StakeholderViewSet` in `apps/api/core/projects/stakeholder_views.py` to accept `relationship_owner` and redact `email`/`phone` unless request user has `view_sensitive_contacts` or `edit_project`; set `contacts_redacted` flag
- [x] T014 [US1] Add `MeetingAction` model in `apps/api/core/documents/models.py` (FK `meeting` CASCADE, FK `project` required denormalized, `description` required text, `owner` FK User \| null, `due_date` date \| null, `status` open\|done default open, `completed_at` datetime \| null) + migration `apps/api/core/documents/migrations/00xx_fr_col_meeting_actions.py`; optional meeting `topic` CharField if missing
- [x] T015 [US1] Implement serializers + nested create/list under meetings and open-actions report endpoint in `apps/api/core/documents/{serializers.py,views.py,urls.py}` and thin helper `apps/api/core/documents/services/meeting_action_service.py` per `contracts/stakeholders-meetings.md` (`/meetings/{id}/actions/`, `/meeting-actions/open/`); permissions `view_documents` / `upload_documents`
- [x] T016 [US1] Re-run `apps/api/core/projects/tests/test_stakeholder_contacts_acl.py`, `apps/api/core/documents/tests/test_meeting_open_actions.py`, and `apps/api/core/projects/tests/test_central_data_stakeholders.py` until green
- [x] T017 [US1] Frontend: extend `apps/web/src/app/lib/api/stakeholders.ts` (or create) for owner + redacted contacts; update `apps/web/src/app/routes/project-stakeholders.tsx`; meetings/actions + open-actions UI on `apps/web/src/app/routes/project-documents.tsx` or new `apps/web/src/app/routes/project-meetings.tsx` + `apps/web/src/app/lib/api/documents.ts`; wire `routeVars.ts` / `routes.ts` / `project-navigation.config.ts` if new route; i18n `apps/web/src/app/locales/en.json` and `fa.json`

**Checkpoint**: US1 independently testable — stakeholder ACL + open meeting actions MVP

---

## Phase 4: User Story 2 — Versioned documents (Priority: P1)

**Goal**: Document unique identity, status, approver, date/type/status filters; revise creates new version without physically deleting prior revision (FR-005, FR-014; SC-004)

**Independent Test**: Upload version 1 and 2 → both revisions retained with distinct `file_url`s; list filters by status/date/type work

### Tests for User Story 2 (TDD — FAIL before implement)

- [x] T018 [P] [US2] Write failing pytest: create document then POST revision → prior `DocumentRevision` row still exists with original `file_url` unchanged in `apps/api/core/documents/tests/test_document_revision_retention.py` (SC-004, FR-005)
- [x] T019 [P] [US2] Write failing pytest: document create/update accepts `status` ∈ {`draft`,`in_review`,`approved`,`superseded`,`obsolete`} (default `draft`) and `approver` FK User \| null; `doc_code` unique per project when non-empty in `apps/api/core/documents/tests/test_document_revision_retention.py` per `data-model.md`
- [x] T020 [P] [US2] Write failing pytest list filters `?status=` and `?date_from=`/`?date_to=` (on revision_date) and existing `doc_type` return matching docs in `apps/api/core/documents/tests/test_document_revision_retention.py` (FR-014)
- [x] T021 [P] [US2] Write failing pytest revise without `upload_documents` → 403 and revision count unchanged in `apps/api/core/documents/tests/test_document_revision_retention.py`

### Implementation for User Story 2

- [x] T022 [US2] Add `status` enum and `approver` FK User \| null on `ProjectDocument` in `apps/api/core/documents/models.py`; enforce unique `(project, doc_code)` when `doc_code` non-empty; migration `apps/api/core/documents/migrations/00xx_fr_col_document_status.py`
- [x] T023 [US2] Harden `create_document_revision` in `apps/api/core/documents/services/document_service.py` to append-only (never delete prior revision rows/files); update serializers/views filters in `apps/api/core/documents/{serializers.py,views.py}` per `contracts/documents-correspondence.md`
- [x] T024 [US2] Re-run `apps/api/core/documents/tests/test_document_revision_retention.py` and `apps/api/core/documents/tests/test_documents.py` until green
- [x] T025 [US2] Frontend: status/approver fields, revision history, filters in `apps/web/src/app/lib/api/documents.ts` and `apps/web/src/app/routes/project-documents.tsx`; i18n `en.json` / `fa.json`

**Checkpoint**: US2 independently testable — non-destructive versioning + filters

---

## Phase 5: User Story 3 — Decisions with rationale & workflow engine (Priority: P1)

**Goal**: ManagementDecision with mandatory rationale + execution owner; configurable WorkflowDefinition/Stage/Instance/ActionLog; activate gate; reject/return then approve with full history; budget_change sample path (FR-006–011, FR-015; SC-002–003, SC-006)

**Independent Test**: Decision without rationale → 400; definition with stage missing approver cannot activate; run budget_change instance reject then approve → log reconstructible

### Tests for User Story 3 (TDD — FAIL before implement)

- [x] T026 [P] [US3] Write failing pytest POST decision without `rationale` (blank/whitespace) → 400 `rationale_required`; with non-blank `rationale` + `execution_owner` → 201 in `apps/api/core/workflow/tests/test_decision_rationale.py` per `contracts/decisions-workflow.md` (SC-002, FR-006)
- [x] T027 [P] [US3] Write failing pytest decision requires `project`; optional `related_risk`/`related_activity`/`related_contract` same-project accepted, cross-project rejected in `apps/api/core/workflow/tests/test_decision_rationale.py` (FR-007)
- [x] T028 [P] [US3] Write failing pytest activate definition when any stage lacks both `approver_user` and `approver_role` → 400 `incomplete_stages` in `apps/api/core/workflow/tests/test_workflow_activate_gate.py` (SC-006, FR-015)
- [x] T029 [P] [US3] Write failing pytest activate valid multi-stage `budget_change` definition → status `active` in `apps/api/core/workflow/tests/test_workflow_activate_gate.py`
- [x] T030 [P] [US3] Write failing pytest start instance → reject (stage `on_reject=return_previous` or stop) → approve path → `GET .../log/` contains actor, acted_at, action, from_status, to_status, stage_order for every transition in `apps/api/core/workflow/tests/test_workflow_reject_approve_log.py` (SC-003, FR-011)
- [x] T031 [P] [US3] Write failing pytest concurrent stage `approval_mode=all` requires all assignees before advance; `any` advances on first approve in `apps/api/core/workflow/tests/test_workflow_reject_approve_log.py` (FR-009)
- [x] T032 [P] [US3] Write failing pytest overdue filter `?overdue=true` returns in-progress instances with `current_due_at` in the past in `apps/api/core/workflow/tests/test_workflow_reject_approve_log.py`

### Implementation for User Story 3

- [x] T033 [US3] Implement models in `apps/api/core/workflow/models.py` per `specs/016-stakeholders-docs-workflow/data-model.md`: `ManagementDecision` (`rationale` required non-blank text, `execution_owner` required on save, impact bools default False, execution_status pending\|in_progress\|done\|cancelled, optional same-project FKs); `WorkflowDefinition` (project-scoped, `workflow_type` enum including `budget_change` + samples, status draft\|active\|retired); `WorkflowStage` (`order` unique per definition, `approver_user` \| null, `approver_role` string \| null, `approval_mode` all\|any default any, `on_reject` stop\|return_previous\|return_to, `return_to_order` \| null, `deadline_days` \| null); `WorkflowInstance` (`subject_type` string, `subject_id` UUID, statuses pending\|in_progress\|approved\|rejected\|returned\|cancelled, `current_stage_order`, `current_due_at`); `WorkflowStageAssignment` (optional concurrent support); `WorkflowActionLog` append-only (actor, acted_at, action, from_status, to_status, stage_order, comment); migration `apps/api/core/workflow/migrations/0001_initial.py`
- [x] T034 [US3] Implement `apps/api/core/workflow/services/decision_service.py` (rationale/execution_owner validation), `definition_service.py` (activate gate), `instance_service.py` (start/approve/reject/return/cancel + log append + due_at from `deadline_days`)
- [x] T035 [US3] Wire serializers/views/urls for `/decisions/`, `/workflows/definitions/` (+ activate/retire), `/workflows/instances/` (+ approve/reject/cancel), `/workflows/instances/{id}/log/` in `apps/api/core/workflow/{serializers.py,views.py,urls.py}` with permissions: GET decisions/instances `view_documents` or `view_project`; mutate decisions + manage definitions `edit_project` per research
- [x] T036 [US3] Re-run `apps/api/core/workflow/tests/test_decision_rationale.py`, `apps/api/core/workflow/tests/test_workflow_activate_gate.py`, `apps/api/core/workflow/tests/test_workflow_reject_approve_log.py` until green; document budget_change sample subject binding in `apps/api/core/workflow/ENDPOINTS.md`
- [x] T037 [US3] Frontend: `apps/web/src/app/lib/api/workflow.ts`; route `apps/web/src/app/routes/project-decisions-workflow.tsx` (decision form with required rationale, definition editor, instance actions + log); register in `apps/web/src/app/routes.ts`, `routeVars.ts`, `project-navigation.config.ts`; components under `apps/web/src/components/workflow/`; i18n `en.json` / `fa.json`

**Checkpoint**: US3 independently testable — decisions + shared workflow engine with audit log

---

## Phase 6: User Story 4 — Correspondence & communication plan (Priority: P2)

**Goal**: Communication plan CRUD; influence–interest matrix; correspondence `related_contract` same-project link (FR-002, FR-004)

**Independent Test**: Two communication-plan rows + one correspondence with contract link listed; matrix groups stakeholders by influence×interest

### Tests for User Story 4 (TDD — FAIL before implement)

- [x] T038 [P] [US4] Write failing pytest POST communication plan (`audience` required, `message` required, `channel_type`, `frequency` required, `owner` FK \| null, optional `stakeholder`, status active\|inactive) → listed on GET in `apps/api/core/projects/tests/test_communication_plan.py` per `contracts/stakeholders-meetings.md` (FR-002)
- [x] T039 [P] [US4] Write failing pytest `GET .../stakeholders/matrix/` returns cells with influence/interest buckets and stakeholder ids/names in `apps/api/core/projects/tests/test_communication_plan.py` (FR-002)
- [x] T040 [P] [US4] Write failing pytest correspondence with same-project `related_contract` → 201; cross-project contract → 400 in `apps/api/core/documents/tests/test_correspondence_contract_link.py` (FR-004)

### Implementation for User Story 4

- [x] T041 [US4] Add `CommunicationPlan` model in `apps/api/core/projects/models.py` per data-model + migration `apps/api/core/projects/migrations/00xx_fr_col_communication_plan.py`; serializers/views/urls for `/communication-plans/` and matrix action on stakeholders in `apps/api/core/projects/stakeholder_views.py` and `apps/api/core/projects/urls.py`
- [x] T042 [US4] Add optional FK `related_contract` → contracts model on `Correspondence` in `apps/api/core/documents/models.py` + migration; validate same-project in `apps/api/core/documents/serializers.py` / views
- [x] T043 [US4] Re-run `apps/api/core/projects/tests/test_communication_plan.py` and `apps/api/core/documents/tests/test_correspondence_contract_link.py` until green
- [x] T044 [US4] Frontend: communication plan + matrix on `apps/web/src/app/routes/project-stakeholders.tsx`; contract link on correspondence UI in documents route; API clients; i18n

**Checkpoint**: US4 independently testable — plan, matrix, correspondence contract link

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs, consumer readiness note, overdue notifications hook, full quickstart verification

- [x] T045 [P] Update `apps/api/core/documents/ENDPOINTS.md` and `apps/api/core/workflow/ENDPOINTS.md` for all new/changed paths matching contracts
- [x] T046 [P] Document consumer attachment (`subject_type` / `subject_id` / `workflow_type`) for domains 09–11/14 in `apps/api/core/workflow/ENDPOINTS.md` (no full IPC/payment/inspection wiring)
- [x] T047 Best-effort overdue stage notification via existing alerts patterns (e.g. emit when `current_due_at` passed) in `apps/api/core/workflow/services/instance_service.py` or task module; skip hard dependency on Celery worker (eager OK)
- [x] T048 Run full quickstart pytest set from `specs/016-stakeholders-docs-workflow/quickstart.md` and fix regressions across US1–US4
- [x] T049 [P] UI smoke on seeded project: `apps/web/src/app/routes/project-stakeholders.tsx` (owner + redaction), meetings/open actions + `project-documents.tsx` revise retention, `project-decisions-workflow.tsx` rationale validation + reject→approve log (fa/en via `en.json`/`fa.json`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After Foundational — independent of US1 (documents app); can parallel US1 if staffed
- **US3 (Phase 5)**: After Foundational — needs `workflow` shell from Phase 2; independent of US1/US2 for engine core
- **US4 (Phase 6)**: After Foundational — benefits from US1 stakeholder fields but independently testable with its own fixtures
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

| Story | Depends on | Notes |
|-------|------------|-------|
| US1 Stakeholders & meeting actions | Phase 2 | MVP; contact ACL uses new permission |
| US2 Versioned documents | Phase 2 | Parallel-safe vs US1 |
| US3 Decisions & workflow | Phase 2 | Uses workflow app; sample budget_change only |
| US4 Comm plan & correspondence | Phase 2 | Matrix uses Stakeholder influence/interest (existing + US1 owner optional) |

### Within Each User Story

1. Write failing tests → confirm red  
2. Models/migrations → services → endpoints  
3. Re-run story tests green  
4. Frontend + i18n  
5. Checkpoint before next story

### Parallel Opportunities

- T001–T002 setup inventory parallel
- T003–T004 foundational tests parallel
- After Phase 2: US1 / US2 / US3 test-writing can proceed in parallel on different files
- Within a story, all `[P]` test tasks can be written together before implementation
- US4 can start once Phase 2 done (does not wait for US3)

---

## Parallel Example: User Story 1

```bash
# TDD tests first (parallel):
Task: "T008 stakeholder relationship_owner in projects/tests/test_stakeholder_contacts_acl.py"
Task: "T009 contact redaction ACL in projects/tests/test_stakeholder_contacts_acl.py"
Task: "T010 meeting open actions in documents/tests/test_meeting_open_actions.py"
Task: "T011 overdue/done filters in documents/tests/test_meeting_open_actions.py"

# Then implement models → serializers/views → re-run green → UI
```

## Parallel Example: User Story 3

```bash
Task: "T026 decision rationale in workflow/tests/test_decision_rationale.py"
Task: "T028 activate gate in workflow/tests/test_workflow_activate_gate.py"
Task: "T030 reject/approve log in workflow/tests/test_workflow_reject_approve_log.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational (permission + workflow shell)  
3. Phase 3 US1 (stakeholders + meeting actions)  
4. **STOP and VALIDATE** independent test / SC-005  
5. Demo MVP

### Incremental Delivery

1. Setup + Foundational  
2. US1 → demo open-actions + contact ACL  
3. US2 → demo revision retention  
4. US3 → demo decision + workflow audit  
5. US4 → communication plan + matrix + contract link  
6. Polish + quickstart suite

### Parallel Team Strategy

1. Team completes Phase 1–2 together  
2. Then: Dev A → US1, Dev B → US2, Dev C → US3; US4 after US1 contact surfaces stable  
3. Integrate via shared permissions and URL mounts only

---

## Notes

- TDD: every story phase starts with failing tests; do not implement first
- Quote field constraints from `data-model.md` are embedded in task text — do not weaken (e.g. never invent composite scores; never delete prior document revisions)
- Consumer domains attach later via `subject_type`/`subject_id` — do not fully rewire IPC/payment/inspection in this feature
- Commit after each logical TDD slice (red → green)
- Suggested MVP: **US1 only** after Phase 2

# Tasks: نقش، سمت و مجوز مؤثر در محدوده پروژه (A6-P2)

**Input**: Design documents from `/specs/046-a6-p2-project-roles/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. Assert the desired behavior. Do not leave the tests as expected failures.

## Phase 1: Setup

- [X] T001 Add the project link, protected assignment, several job titles, title defaults, and base history in `apps/api/core/master_data/models.py` and a migration under `apps/api/core/master_data/migrations/`

## Phase 2: Foundational

- [X] T002 Extend effective permissions with title defaults and `origin` values `inherit`, `grant`, and `deny` in `apps/api/core/permissions/services.py`
- [X] T003 Add assignment-safe custom role deletion, impact counts, and base history writes in `apps/api/core/permissions/role_services.py`

## Phase 3: User Story 1 - Local role boundary (Priority: P1)

- [X] T004 [P] [US1] Write failing-then-passing tests in `apps/api/core/projects/tests/test_local_roles.py` for two projects, cross-project assignment, and project authority not deleting a global role
- [X] T005 [US1] Serve local roles from `apps/api/core/projects/local_role_views.py` and register them in `apps/api/core/projects/urls.py`
- [X] T006 [US1] Reject a role from another project in `apps/api/core/projects/services/__init__.py` without changing the saved roles

## Phase 4: User Story 2 - Global and system roles (Priority: P1)

- [X] T007 [US2] Keep global role writes on the existing organization administrators and built-in roles immutable in `apps/api/core/projects/role_views.py`
- [X] T008 [US2] Show assignment impact and block delete while assignments remain in `apps/web/src/app/routes/settings-roles.tsx`

## Phase 5: User Story 3 - Permission origin (Priority: P1)

- [X] T009 [P] [US3] Write tests in `apps/api/core/permissions/tests/test_permission_origin.py` for union, deny, reset, invalid codes, and removing one of two roles
- [X] T010 [US3] Use `origin` for inherit, grant, and deny in `apps/web/src/components/projects/add-member-drawer.tsx`

## Phase 6: User Story 4 - Job titles (Priority: P2)

- [X] T011 [P] [US4] Write tests in `apps/api/core/projects/tests/test_positions_and_history.py` for several titles, public and local choices, and rejection of another project's title
- [X] T012 [US4] Accept `position_ids` and selectable titles in `apps/api/core/projects/member_serializers.py` and `apps/api/core/business_meta/views.py`
- [X] T013 [US4] Select several titles without clearing roles in `apps/web/src/components/projects/add-member-drawer.tsx`

## Phase 7: User Story 5 - Blocked deletion and base history (Priority: P2)

- [X] T014 [US5] Record before/after access changes and expose recent project records in `apps/api/core/projects/local_role_views.py`
- [X] T015 [US5] Create a local role and show recent changes in `apps/web/src/app/routes/project-members.tsx`
- [X] T016 Add Persian and English refusal text in `apps/api/core/locale/fa/LC_MESSAGES/django.po`, `apps/web/src/app/locales/fa.json`, and `apps/web/src/app/locales/en.json`

## Phase 8: Polish

- [X] T017 Run the pytest modules in `specs/046-a6-p2-project-roles/quickstart.md` and check the member form in the browser
- [X] T018 Record requirement results in `specs/046-a6-p2-project-roles/traceability.md`

## Dependencies

- T001 blocks every later task
- T002 and T003 follow T001 and block the stories
- T005 depends on T003 and T004
- T010 depends on T002
- T014 depends on T003
- User Story 1 can be tested before the job-title story

## MVP

User Story 1: a local role in project A does not appear or apply in project B.

## Phase 9: Convergence

- [X] T019 Deliver the Persian role and permission matrix for the current catalog in `specs/046-a6-p2-project-roles/role-matrix.md` per FR-003 (partial)

## Phase 10: Convergence

- [X] T020 Show the assignment count before deleting a local role and before saving its permissions in `apps/web/src/app/routes/project-members.tsx` per FR-008 (partial)
- [X] T021 Present each base role as Persian allow and deny lists in `specs/046-a6-p2-project-roles/role-matrix.md`, and use the same Persian permission labels in the local role editor, per FR-003 (partial)
- [X] T022 Include global roles in the project role list without matching another project's local role in `apps/api/core/projects/local_role_views.py` per FR-001 (contradicts)
- [X] T023 Let an authorized project manager rename and describe an existing local role from `apps/web/src/app/routes/project-members.tsx` per FR-001 (partial)

## Phase 11: Convergence

- [X] T024 CRITICAL: Restrict the global role route in `apps/api/core/projects/role_views.py` to global roles so a project-local role cannot be retrieved, renamed, repermissioned, or deleted through `PATCH`, `PUT` `…/permissions/`, or `DELETE` `/api/v1/roles/{id}/` by an organizational actor without project authority, adding a failing-then-passing test in `apps/api/core/projects/tests/test_local_roles.py` per Constitution I, FR-001, FR-002 (contradicts)
- [X] T025 Record `role_created` and `role_renamed` base history entries in `apps/api/core/projects/local_role_views.py` when a local role is created and when its name or description changes, using `record_access_change` with actor, project, and before/after role names, and verify through `apps/api/core/projects/tests/test_local_roles.py` per FR-009 (partial)

## Phase 12: Convergence

- [X] T026 Record base history when a global custom role is created or its name or description changes in `apps/api/core/projects/role_views.py`, and record a role-level permission change in `apps/api/core/permissions/role_services.py` even when no member's inherited permissions change, per FR-009 (partial)

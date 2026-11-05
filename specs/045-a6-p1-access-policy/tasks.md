# Tasks: تثبیت سیاست دسترسی و رفع نقص‌های فوری (A6-P1)

**Input**: Design documents from `/specs/045-a6-p1-access-policy/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required. The specification demands failing-then-passing checks for the three defects, and quickstart.md names the pytest modules. Do not mark a test expected-failure and do not delete the assertion.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature docs: `specs/045-a6-p1-access-policy/`
- Git branch remains `develop`. Do not create a feature branch in these tasks.
- Do not drop or recreate the development database. Pytest must use its own test database.
- Do not upgrade Django off the 4.2 line.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Register the one new permission name and the bilingual error text. No new application and no new authorization package.

- [X] T001 [P] Add codename `delete_activities` to the permission catalog in `apps/api/core/permissions/constants.py`, keeping `RolePermission.permission_codename` maximum length 60
- [X] T002 [P] Add gettext msgid `One or more selected roles do not exist.` with a Persian translation in `apps/api/core/locale/fa/LC_MESSAGES/django.po`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared checks and the permission backfill that later stories call. No story starts before this phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add `has_organizational_observation` and `active_member_has_codename` to `apps/api/core/permissions/project.py`. Observation is only `is_superuser` or Django group `admin`. `is_staff` alone and group `hr` do not qualify. Membership status values remain `active`, `inactive`, `invited`, `suspended`, and `archived`; only `active` satisfies the strict helper. Do not change the write behavior of `_is_global_admin` for its existing callers
- [X] T004 Add a data migration under `apps/api/core/master_data/migrations/` that grants `delete_activities` to every role that already has `edit_activities`, and reverses by deleting only the rows this migration inserted

**Checkpoint**: Strict checks and the delete backfill exist. Existing editors still have delete. Unselected modules still use the old full bypass.

---

## Phase 3: User Story 1 - رد نقش ناموجود بدون اثر نیمه‌کاره (Priority: P1) 🎯 MVP

**Goal**: An unknown or mixed role list is rejected before any membership, role assignment, or individual override changes. Create still requires at least one role id. Update may omit `role_ids`.

**Independent Test**: As an active team manager, submit one unknown role id and a mix of a real role and an unknown role on create and on update. Expect HTTP 400, code `unknown_role`, no new membership, and unchanged previous roles and overrides. Persian and English locales each return a clear message.

### Tests for User Story 1

- [X] T005 [P] [US1] Write a failing pytest, with the desired behavior asserted rather than expected-failure, in `apps/api/core/projects/tests/test_member_role_atomicity.py` for `POST /api/v1/projects/{project_id}/members/` and `PATCH /api/v1/projects/{project_id}/members/{user_id}/` covering unknown ids, mixed ids, unchanged overrides, and both locales

### Implementation for User Story 1

- [X] T006 [US1] Replace role assignment in `apps/api/core/projects/services/__init__.py` with one `transaction.atomic` operation that rejects the whole request when any role id is missing, before deleting existing `ProjectMemberRole` rows
- [X] T007 [US1] Validate the full `role_ids` list in `apps/api/core/projects/member_serializers.py` and return the `unknown_role` envelope from `apps/api/core/projects/member_views.py` using the gettext message, without inserting a `ProjectMember` on create or clearing roles on update
- [X] T008 [US1] Keep `apps/web/src/components/projects/add-member-drawer.tsx` open on failure, show the message already extracted by `apps/web/src/app/lib/api-client.ts`, and leave the saved member list unchanged

**Checkpoint**: User Story 1 is testable with an already-authorized active manager.

---

## Phase 4: User Story 2 - بازدیدکننده در کاتالوگ قدیمی کالا فقط می‌خواند (Priority: P1)

**Goal**: An organization visitor can read the legacy item catalog and cannot use its existing write operations. A non-visitor who can write today still can. The catalog is not project-private data.

**Independent Test**: Visitor `GET /api/items/` succeeds. Visitor `POST`, `PATCH`, `DELETE`, and `POST /api/items/import/` do not change data. A non-visitor writer still succeeds.

### Tests for User Story 2

- [X] T009 [P] [US2] Write a failing pytest, with the desired behavior asserted rather than expected-failure, in `apps/api/core/inventory/test_visitor_item_writes.py` for visitor read, visitor create/update/delete/import, and a non-visitor write

### Implementation for User Story 2

- [X] T010 [US2] Add the existing `IsVisitorReadOnly` gate to `ItemViewSet`, including its import action, in `apps/api/core/inventory/views.py`. Do not treat a project viewer role as the organization visitor group

**Checkpoint**: User Story 2 is testable without the membership changes.

---

## Phase 5: User Story 3 - عضو غیرفعال سمت‌های پروژه را نمی‌بیند (Priority: P1)

**Goal**: An ordinary inactive member cannot list or retrieve positions for that project. An active allowed member still can. Direct callers of the same helper follow the same active-membership rule. Historical documents and the recorded author stay.

**Independent Test**: Deactivate an ordinary member and request the position list and detail. Access is refused. An active member of the same project still receives the positions. The same inactive member is refused on the direct project-scoped reads that use this helper, while the active member is not.

### Tests for User Story 3

- [X] T011 [P] [US3] Write a failing pytest, with the desired behavior asserted rather than expected-failure, in `apps/api/core/business_meta/tests/test_position_access_policy.py` for inactive versus active position list and detail, plus the direct reads in `apps/api/core/inventory/views.py` and `apps/api/core/inventory/department_activity_data_views.py`. Assert the position payload does not add wage, rate, email, or phone fields

### Implementation for User Story 3

- [X] T012 [US3] Change `CanViewProjectMembers` in `apps/api/core/business_meta/permissions.py` so an ordinary caller must have membership status exactly `active`, while `has_organizational_observation` may read without that membership. Remove the shortcut for `is_staff`, group `hr`, and group `business-setup`. Keep the alias `CanViewBusinessAssignments` pointed at this same class

**Checkpoint**: User Story 3 is testable on positions and the direct helper callers. Their write rules are not redesigned here.

---

## Phase 6: User Story 4 - اختیار پروژه با اختیار سازمان یکی نیست (Priority: P1)

**Goal**: System administrator and superuser may read general position information without an active membership, including when their own membership is inactive. They cannot create, update, or delete positions, and cannot add or change project members, without an active membership and `manage_members`. Staff and human resources get neither the read nor the write. A project manager in one project does not manage the other project or the organization.

**Independent Test**: On two projects, compare staff, human resources, inactive ordinary member, system administrator without membership, and superuser without membership. Only the last two read positions. None of staff, human resources, administrator, or superuser can write positions or members without an active `manage_members` membership. Project manager authority stays inside that project.

### Tests for User Story 4

- [X] T013 [P] [US4] Write a failing pytest, with the desired behavior asserted rather than expected-failure, in `apps/api/core/permissions/tests/test_observation_exception.py` for the five account kinds, inactive observer read, refused position writes, refused member create, and the two-project manager boundary

### Implementation for User Story 4

- [X] T014 [US4] Require active membership plus `manage_members` for position create, update, and delete in `apps/api/core/business_meta/views.py` by calling `active_member_has_codename`, not `IsHrOrAdmin` and not `_is_global_admin`
- [X] T015 [US4] Require that same strict `manage_members` check for member create, role update, and permission override writes in `apps/api/core/projects/member_views.py`, so group `admin` and superuser without an active membership are refused

**Checkpoint**: User Story 4 is testable on positions and team membership. Other modules that still call `_is_global_admin` stay unchanged.

---

## Phase 7: User Story 5 - ماتریس اولیه عملیات و جدایی ویرایش از حذف و تأیید (Priority: P2)

**Goal**: One existing activity shows that edit, delete, and approval are separate. Roles that already had edit keep delete through the backfill. The rest of the module matrix is not claimed complete.

**Independent Test**: A member whose role has `edit_activities` but not `delete_activities` or `approve_reports` can update the activity and cannot delete it or approve its measurement basis. A role that had `edit_activities` before the migration can still delete.

### Tests for User Story 5

- [X] T016 [P] [US5] Write a failing pytest, with the desired behavior asserted rather than expected-failure, in `apps/api/core/schedule/tests/test_activity_action_split.py` for activity update, activity delete, and `POST /api/v1/projects/{project_id}/activities/{activity_id}/measurement/approve/`

### Implementation for User Story 5

- [X] T017 [US5] Require `delete_activities` for destroy in `apps/api/core/schedule/activity_views.py` through `active_member_has_codename`, leave update on `edit_activities`, and leave measurement approval on `approve_reports` in `apps/api/core/schedule/measurement_views.py`

**Checkpoint**: The representative split passes. No other module's edit permission is split in this phase.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Evidence and traceability across the selected paths.

- [X] T018 [P] Write the A6-R10, A6-R29, A6-R31, A6-R32, A6-R36, and A6-R37 map to story, task, and test in `specs/045-a6-p1-access-policy/traceability.md`, including the single-realm limit and the rows left for P4 and P6
- [X] T019 Run the pytest command in `specs/045-a6-p1-access-policy/quickstart.md` on the final tree and record the command result beside that file without resetting the development database
- [X] T020 Exercise the member form in the browser: submit an unknown role, confirm the visible Persian or English error, and confirm the member list is unchanged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup and blocks every user story
- **User Stories (Phase 3+)**: Depend on Foundational
- **Polish (Phase 8)**: Depends on the user stories selected for the final check

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on other stories
- **User Story 2 (P1)**: Starts after Foundational. Independent of the membership stories
- **User Story 3 (P1)**: Starts after Foundational. Independent of User Story 1 and User Story 2
- **User Story 4 (P1)**: Starts after Foundational. T015 edits `apps/api/core/projects/member_views.py` after T007. T014 does not need User Story 1
- **User Story 5 (P2)**: Starts after Foundational, including the `delete_activities` backfill. Independent of the membership stories

### Within Each User Story

- Write the story test first and confirm it fails for the current behavior
- Keep the assertion of the desired result
- Service changes before the view that calls them
- Do not start the next edit of the same file until the earlier edit is finished

### Parallel Opportunities

- T001 and T002 can run together
- T003 and T004 can run together after Setup
- After Foundational, T005, T009, T011, T013, and T016 can be written together because they use different test files
- T010 can proceed beside User Story 1
- T014 can proceed beside T015 only after T015's file is free of the User Story 1 edit

---

## Parallel Example: User Story 1

```bash
# After Foundational, write the independent failing tests together:
Task: "T005 member role atomicity in apps/api/core/projects/tests/test_member_role_atomicity.py"
Task: "T009 visitor item writes in apps/api/core/inventory/tests/test_visitor_item_writes.py"
Task: "T011 position access in apps/api/core/business_meta/tests/test_position_access_policy.py"

# Then implement User Story 1 in order:
Task: "T006 atomic role service in apps/api/core/projects/services/__init__.py"
Task: "T007 unknown_role response in apps/api/core/projects/member_views.py"
Task: "T008 visible form error in apps/web/src/components/projects/add-member-drawer.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3
3. Stop and run `apps/api/core/projects/tests/test_member_role_atomicity.py`
4. Continue only after that test shows the desired refusal

### Incremental Delivery

1. Setup and Foundational unlock the strict helper and the delete backfill
2. User Story 1 closes partial membership saves
3. User Story 2 closes visitor writes on the legacy catalog
4. User Story 3 closes inactive reads through the shared helper
5. User Story 4 applies the named observation exception on positions and team writes
6. User Story 5 proves edit, delete, and approval on one activity
7. Polish records evidence without calling the whole product covered

### Parallel Team Strategy

After Foundational, one person can take User Story 1 and User Story 4's member file in that order, another can take User Story 2, and another can take User Story 3 then User Story 4's position file. User Story 5 can proceed beside them.

---

## Notes

- Selected paths only. Do not retune every caller of `_is_global_admin`; that coverage is P4
- Do not add an organization tenant or compare free-text organization labels
- Do not add multiple job titles per membership; that is a later phase
- PM-16 and PM-17 stay unresolved and must not be filled in by these tasks
- Commit only when the user asks

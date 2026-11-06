# Tasks: تکمیل ممیزی و تاریخچه قابل استفاده (A6-P5)

**Input**: Design documents from `/specs/049-a6-p5-access-history/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/access-history.md, quickstart.md

**Tests**: Required by the specification and quickstart. Write the failing test before the behavior it names.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature docs: `specs/049-a6-p5-access-history/`

## Phase 1: Setup

**Purpose**: Prepare the existing history row for filtered reads without a second store

- [X] T001 Add indexes `(project, created_at)`, `(subject_user, created_at)`, and `(actor, created_at)` on `role_access_changes` in a new migration under `apps/api/core/master_data/migrations/` without rewriting existing `RoleAccessChange` rows in `apps/api/core/master_data/models.py`

---

## Phase 2: Foundational

**Purpose**: Shared write rules that every story uses

**⚠️ CRITICAL**: No user story work begins until this phase is complete

- [X] T002 Redact nested password, recovery-token, access-token, refresh-token, and secret values to a fixed marker inside `before` and `after` before insert in `record_access_change` in `apps/api/core/permissions/role_services.py`
- [X] T003 Commit a sensitive access change and its `RoleAccessChange` insert in one database transaction in `apps/api/core/permissions/role_services.py`, rolling back the change when the insert fails
- [X] T004 Derive `origin` only as `role`, `exception`, `membership`, `account`, or `event` from the stored `action` in `apps/api/core/permissions/role_services.py`

**Checkpoint**: New writes are redacted, transactional, and classifiable

---

## Phase 3: User Story 1 - بازسازی تغییر دسترسی یک شخص (Priority: P1) 🎯 MVP

**Goal**: A team manager can reconstruct role, exception, and membership-status changes with before and after

**Independent Test**: Change roles, set and clear one exception, and change membership status. History shows actor, subject, project, time, before, after, and whether the origin is `role` or `exception`. A viewer is refused. Earlier rows remain after the member leaves and after a controlled role deletion.

### Tests for User Story 1

- [X] T005 [P] [US1] Write failing tests for before/after, `origin` `role` versus `exception`, viewer refusal, and retained rows after member exit and controlled role deletion in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 1

- [X] T006 [US1] Return `id`, `action`, `origin`, `role_name`, `actor_name`, `subject_name`, `project_id`, `before`, `after`, `unknown`, and `created_at` from `ProjectAccessChangeListView` in `apps/api/core/projects/local_role_views.py`
- [X] T007 [US1] Pass real before and after for role replacement, override set, override clear, and membership-status change in `apps/api/core/permissions/services.py` and `apps/api/core/projects/member_views.py`

**Checkpoint**: User Story 1 is readable on the current project endpoint

---

## Phase 4: User Story 2 - تغییر نقش سراسری به پروژه تصادفی نسبت داده نمی‌شود (Priority: P1)

**Goal**: A global role change stays organizational and a project manager cannot read another project's subjects

**Independent Test**: Change a global role used by project A and project B. Organization history keeps `project` null. The project A manager does not receive project B subjects.

### Tests for User Story 2

- [X] T008 [P] [US2] Write failing tests that a global role change stores a null project and that a project A manager receives neither project B subjects nor a success response for project B in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 2

- [X] T009 [US2] Keep global role create, rename, and permission changes on a null project in `apps/api/core/projects/role_views.py` and `apps/api/core/permissions/role_services.py`
- [X] T010 [US2] Add `GET /api/v1/access-changes/` for the `admin` group and superuser only, excluding other organizations, in `apps/api/core/projects/local_role_views.py` and `apps/api/core/projects/urls.py`

**Checkpoint**: Global changes are not attached to a random project

---

## Phase 5: User Story 3 - فیلتر تاریخچه در حد اختیار (Priority: P1)

**Goal**: Authorized readers filter by person, actor, and time, with stable pages in Persian and English

**Independent Test**: Combined filters and the next page stay inside the filter and the caller's authority. A caller without permission receives 403 from a direct request.

### Tests for User Story 3

- [X] T011 [P] [US3] Write failing tests for `subject`, `actor`, inclusive `since`, inclusive `until`, `page` default 1, and `page_size` default 50 maximum 100 in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 3

- [X] T012 [US3] Apply those filters and the paged `{count, page, page_size, results}` object to both history endpoints in `apps/api/core/projects/local_role_views.py`
- [X] T013 [P] [US3] Add Persian and English labels for history filters, origins, unknown values, and the forbidden error in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`
- [X] T014 [US3] Read `results` from the paged project history response in `apps/web/src/app/lib/api/members.ts` and `apps/web/src/app/routes/project-members.tsx`
- [X] T015 [US3] Add the project history screen with subject, actor, and time filters in `apps/web/src/app/routes/access-history.tsx` and register it from `apps/web/src/app/routes.ts`

**Checkpoint**: Filtering and both languages work for a team manager

---

## Phase 6: User Story 4 - راز داخل تغییر دیده نمی‌شود (Priority: P1)

**Goal**: Nested passwords and tokens are redacted in storage and in the response without erasing the access difference

**Independent Test**: A nested password and token are stored only as the redacted marker. Actor, time, and the access difference remain. Organizational observation does not reveal the secret.

### Tests for User Story 4

- [X] T016 [P] [US4] Write a failing nested password and token test for save and read in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 4

- [X] T017 [US4] Apply the same secret walk to history responses in `apps/api/core/projects/local_role_views.py`, leaving sibling access-difference keys in place

**Checkpoint**: Stored and displayed history cannot reveal the secret

---

## Phase 7: User Story 5 - خرابی ثبت ممیزی نتیجه مبهم نمی‌سازد (Priority: P1)

**Goal**: A sensitive access change is not announced as successful when its trail cannot be stored

**Independent Test**: A forced insert failure returns 503 `audit_unavailable`, leaves the previous permission in place, and does not write a success row.

### Tests for User Story 5

- [X] T018 [P] [US5] Write a failing test that a forced `RoleAccessChange` insert failure returns `audit_unavailable` and does not persist the permission change in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 5

- [X] T019 [US5] Map that transactional failure to HTTP 503 `audit_unavailable` with Persian and English text in `apps/api/core/projects/role_views.py` and `apps/api/core/projects/local_role_views.py`

**Checkpoint**: Success and a missing trail cannot occur together

---

## Phase 8: User Story 6 - ورود، تأیید نهایی و خروجی حساس ردپا دارند (Priority: P2)

**Goal**: Successful login, recovery, final approval, and sensitive export have explicit rows

**Independent Test**: Successful login writes `login_succeeded`. A wrong password writes nothing. Recovery writes `recovery_requested` with the requester as `actor` and the target account as `subject_user`, and without the token. One final approval and one sensitive export each write their own row.

### Tests for User Story 6

- [X] T020 [P] [US6] Write failing tests for `login_succeeded`, no row on a wrong password, `recovery_requested` without a token, `final_approval`, and `sensitive_export` in `apps/api/core/permissions/tests/test_access_history.py`

### Implementation for User Story 6

- [X] T021 [P] [US6] Write `login_succeeded` only after a successful sign-in, with a null project and the signed-in account as `subject_user`, in `apps/api/core/authentication/services.py`
- [X] T022 [P] [US6] Write `recovery_requested` with the requester as `actor` and the target account as `subject_user`, omitting the token, in `apps/api/core/authentication/services.py`
- [X] T023 [US6] Write `final_approval` from the existing final-approve path that does not already record a more specific row, and `sensitive_export` when a sensitive export succeeds, in `apps/api/core/workflow/services/instance_service.py` and `apps/api/core/projects/services/report_export_service.py`

**Checkpoint**: These events are proven on their own paths, not by generic write logging

---

## Phase 9: Polish

**Purpose**: Confirm the quickstart and the response-shape change together

- [X] T024 Run the pytest command in `specs/049-a6-p5-access-history/quickstart.md` and record that it uses the synchronous test database
- [X] T025 Check the Persian and English history screens and a direct forbidden request against `specs/049-a6-p5-access-history/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on T001 and blocks every story
- **User Stories (Phase 3+)**: Depend on Phase 2. US2 through US5 can proceed after US1's response shape exists. US6 can proceed after Phase 2.
- **Polish**: Depends on the stories being present

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2. No dependency on later stories.
- **User Story 2 (P1)**: Starts after Phase 2. Uses the same row and read helper as US1.
- **User Story 3 (P1)**: Starts after the list response exists in T006.
- **User Story 4 (P1)**: Starts after T002. The read walk in T017 follows T006.
- **User Story 5 (P1)**: Starts after T003.
- **User Story 6 (P2)**: Starts after T002 so new rows are redacted. It does not require the screen.

### Within Each User Story

- The failing test comes before the implementation that should make it pass
- Shared write rules in Phase 2 come before story endpoints
- The web screen comes after the paged contract

### Parallel Opportunities

- T011 and T013 touch different files and can run together after T006
- T021 and T022 are marked parallel only if they edit disjoint functions in `apps/api/core/authentication/services.py`; otherwise finish T021 first
- Story tests stay in one file, so they are sequential rather than parallel with each other

---

## Parallel Example: User Story 3

```bash
# After T006, these touch different files:
Task: "T011 filters and pagination tests in apps/api/core/permissions/tests/test_access_history.py"
Task: "T013 Persian and English history labels in apps/web/src/app/locales/fa.json and en.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Finish Phase 1 and Phase 2
2. Finish Phase 3
3. Stop and run the User Story 1 tests in `apps/api/core/permissions/tests/test_access_history.py`

### Incremental Delivery

1. Foundation makes every new row redacted and transactional
2. User Story 1 shows a reconstructable person trail
3. User Story 2 keeps global changes off a random project
4. User Story 3 adds filters, pages, and both languages
5. User Story 4 and User Story 5 close secrets and failure behavior
6. User Story 6 adds the explicit sensitive events

### Parallel Team Strategy

After Phase 2, one person can continue US1 and US2 on the API while another prepares US3 locale strings. Do not edit `test_access_history.py` from two stories at the same time.

---

## Notes

- Tests are required because the specification and `quickstart.md` name `permissions/tests/test_access_history.py`
- Do not add a second history table or a new permission codename
- Do not backfill unknown historical values
- Synchronous pytest does not prove a later asynchronous audit worker

---

## Phase 10: Convergence

- [X] T026 Add organization access history screen and route at `/settings/access-history`, update `fetchAccessChanges` in `apps/web/src/app/lib/api/members.ts` to support querying `/v1/access-changes/`, and support organization scope with optional `project` filter in `apps/web/src/app/routes/access-history.tsx` and `apps/web/src/app/routes/business-setup.routes.ts` per plan Scale/Scope, quickstart Browser, US2, and FR-002 (partial)
- [X] T027 Add test coverage for `final_approval` and `sensitive_export` `RoleAccessChange` records in `apps/api/core/permissions/tests/test_access_history.py` per T020, US6, quickstart Scenario 7, and Constitution VI (partial)
- [X] T028 Add Persian translations and compile gettext for `audit_unavailable` and access history forbidden messages in `apps/api/core/locale/fa/LC_MESSAGES/django.po` and `django.mo` per Constitution III, FR-011, and T019 (partial)

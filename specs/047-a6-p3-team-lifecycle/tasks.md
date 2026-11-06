---
description: "Task list for A6-P3 team and account lifecycle"
---

# Tasks: گردش حساب و تیم پروژه (A6-P3)

**Input**: Design documents from `/specs/047-a6-p3-team-lifecycle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the spec acceptance scenarios, quickstart, and constitution. Assert the desired behavior. Write the new test first and make it fail before the implementation. Do not leave a test as an expected failure. Re-run the existing member and credential tests; do not replace them with copies of the implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1–US7)
- Setup, foundational, and polish tasks have no story label

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Tests use the repository `.env` and the test database. Do not drop or recreate the development database. Django stays on 4.2.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Name the existing delivery setting without choosing a provider

- [X] T001 Add `TEAM_DELIVERY_TEST_RECIPIENT` with an empty default in `apps/api/core/config/settings.py`. Do not add an SMS vendor, price, or new sending policy. Console, locmem, and dummy email, and `SMS_PROVIDER=console`, stay non-operational.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared person, membership, sign-in, and delivery rules that every story uses

**⚠️ CRITICAL**: No user story work starts until this phase is complete

- [X] T002 [P] Extend `ProjectMember` in `apps/api/core/master_data/models.py` and add a migration under `apps/api/core/master_data/migrations/`. Keep one row per project and person through the existing partial uniqueness on project plus user. Keep status values `active`, `inactive`, `invited`, `suspended`, and `archived`. Add optional `invited_mobile`; `invite_expires_at`; `invite_token_hash` (hash only, raw token is not stored); nullable `invite_cancelled_at`; nullable `invite_accepted_at`; and `delivery_status` limited to `not_configured`, `not_sent`, or `sent`. Pending invitations are unique for the same project and email, and for the same project and mobile. Change `user` from cascade delete to `PROTECT`. Give an existing open invitation seven days from the migration time and do not invent a token. `joined_at` stays the creation time.
- [X] T003 [P] Add a data migration under `apps/api/core/authentication/migrations/` that aligns the existing user status and sign-in flag without turning sign-in on. Visible status remains `active`, `inactive`, or `suspended`. An `active` person who cannot sign in becomes `inactive` and stays unable to sign in. An `inactive` or `suspended` person who can sign in keeps that status and loses sign-in. An `active` person who can sign in stays unchanged. The reverse migration must not turn sign-in back on.
- [X] T004 [P] Add `account_can_authenticate` in `apps/api/core/authentication/services.py`: sign-in is allowed only when status is `active` and the existing sign-in flag is on. Use it from `UsernameOrMobileBackend.user_can_authenticate` in `apps/api/core/authentication/backends.py`, from `LoginService.authenticate_and_issue_tokens`, and as `SIMPLE_JWT['USER_AUTHENTICATION_RULE']` in `apps/api/core/config/settings.py`.
- [X] T005 [P] Add an operational-delivery helper in `apps/api/core/notifications/services/delivery.py`. Email is operational only when `EMAIL_BACKEND` is not the console, locmem, or dummy backend. SMS is operational only when `SMS_PROVIDER` is not `console` and a non-console backend exists. Return `not_configured`, `not_sent`, or `sent`. Do not log a reset or invitation secret. Do not treat in-app notification or the console SMS helper as `sent`.

**Checkpoint**: Schema, sign-in rule, and delivery classification are ready. User stories can proceed.

---

## Phase 3: User Story 1 - Select the same existing person (Priority: P1) 🎯 MVP

**Goal**: A team manager adds an existing person to a project without creating a second account or gaining account administration.

**Independent Test**: Create one person and add that same id to two projects. No second account is created. A viewer, non-member, inactive member, and a member with an explicit deny cannot add a member.

### Tests for User Story 1

- [X] T006 [US1] Write failing tests in `apps/api/core/projects/tests/test_team_lifecycle.py` for one user id added to two projects, no second user row, and HTTP 403 from `POST /api/v1/projects/{project_id}/members/` for a viewer, a non-member, an inactive member, and an explicit deny of `manage_members`.

### Implementation for User Story 1

- [X] T007 [US1] Keep selection on `POST /api/v1/projects/{project_id}/members/` with `user_id` in `apps/api/core/projects/member_views.py`. Require an active member with `manage_members`. Return the same user id and do not create a user.
- [X] T008 [P] [US1] Keep search and select on the existing lookup in `apps/web/src/components/projects/add-member-drawer.tsx` and `apps/web/src/app/lib/api/members.ts`. This path must not call `POST /api/auth/users/`.

**Checkpoint**: User Story 1 is testable alone.

---

## Phase 4: User Story 2 - Create a person only within account authority (Priority: P1)

**Goal**: An account administrator creates a usable person from the team screen. A project manager without that authority is refused and can still select an existing person.

**Independent Test**: HR or admin creates a person and the team manager adds that person. A project manager with only `manage_members`, and an ordinary user, receive HTTP 403. Duplicate mobile, duplicate username, an invalid password, and a mismatched confirmation are rejected on create and on a later edit.

### Tests for User Story 2

- [X] T009 [P] [US2] Write failing tests in `apps/api/core/authentication/tests/test_account_lifecycle.py` for `POST /api/auth/users/`: an `hr` or `admin` caller succeeds; a project manager with only `manage_members` and an ordinary user receive HTTP 403 code `account_forbidden`; duplicate `username` and duplicate `mobile` return HTTP 400; a mismatched `password_confirm` and an invalid password return HTTP 400; the new person receives the `visitor` group only.

### Implementation for User Story 2

- [X] T010 [US2] Keep person creation on `UserListView` in `apps/api/core/authentication/views.py` behind `IsHrOrAdmin`. Preserve the current registration body: name, mobile, username or email, password, and password confirmation. Do not let `manage_members` pass this gate and do not assign `admin` or `hr` from this request. Keep the translated field errors from `apps/api/core/authentication/serializers.py` for a later edit as well as create.
- [X] T011 [US2] From `apps/web/src/components/projects/add-member-drawer.tsx`, submit the same fields to `POST /api/auth/users/` and add the membership only after HTTP 201. On HTTP 403, show the translated refusal and leave search and select usable.
- [X] T012 [P] [US2] Add the Persian and English text for `account_forbidden`, duplicate mobile, duplicate username, and password confirmation in `apps/web/src/app/locales/fa.json`, `apps/web/src/app/locales/en.json`, and `apps/api/core/locale/fa/LC_MESSAGES/django.po`.

**Checkpoint**: User Stories 1 and 2 both work. Story 2 does not grant account authority to a project manager.

---

## Phase 5: User Story 3 - Invitation until acceptance, or the secure account path (Priority: P1)

**Goal**: An invitation without a person can be accepted by the matching identity, connected, or cancelled. Access starts only after the account can sign in and the membership is active. A missing channel is not reported as sent.

**Independent Test**: Before acceptance there is no project access. Matching acceptance creates one manageable membership. Expired, cancelled, used, and mismatched invitations grant nothing. Console delivery returns `not_configured` or `not_sent`.

### Tests for User Story 3

- [X] T013 [US3] Add failing invitation tests to `apps/api/core/projects/tests/test_team_lifecycle.py`: create with email or mobile and no `user_id`; the list includes membership `id` and `user_id` null; connect and cancel work; `POST /api/auth/invitations/accept/` with the matching signed-in identity activates that same row; expired, cancelled, used, and mismatched tokens return `invitation_invalid` and grant nothing; console email and console SMS do not return `sent`; `sent` happens only for `TEAM_DELIVERY_TEST_RECIPIENT` on an operational channel. The response and history contain no raw token.

### Implementation for User Story 3

- [X] T014 [US3] Implement invitation create, `POST /api/v1/projects/{project_id}/members/invitations/{member_id}/connect/` with `user_id`, and `POST .../cancel/` in `apps/api/core/projects/member_views.py`, `apps/api/core/projects/member_serializers.py`, and `apps/api/core/projects/urls.py`. Implement `POST /api/auth/invitations/accept/` with `token` in `apps/api/core/authentication/views.py` and `apps/api/core/authentication/urls.py`. Store only the token hash, set expiry to seven days, and require a matching email or mobile. Activate the membership only when `account_can_authenticate` is true. Record `invitation_created`, `invitation_cancelled`, and `invitation_accepted` through `record_access_change` in `apps/api/core/permissions/role_services.py`, with actor, person, project, time, and difference, and without a password or token.
- [X] T015 [US3] In `apps/web/src/components/projects/add-member-drawer.tsx` and `apps/web/src/app/routes/project-members.tsx`, invite by email or mobile, show `delivery_status`, and connect or cancel a row whose `user_id` is null. Do not leave that row without an action.

**Checkpoint**: Invitation and the secure connect path are usable without a configured channel.

---

## Phase 6: User Story 4 - Repeated and concurrent adds (Priority: P1)

**Goal**: Two adds for one person and one project leave one consistent membership and an actionable response.

**Independent Test**: Two overlapping creates return one membership and HTTP 409 `already_member`. No role rows remain from the failed attempt. A second request after success does not create another membership.

### Tests for User Story 4

- [X] T016 [US4] Add failing tests to `apps/api/core/projects/tests/test_team_lifecycle.py` for a repeated add, a forced uniqueness conflict inside the create transaction, and connecting an invitation to a person who already has a membership. Expect HTTP 409 code `already_member`, one membership, and no partial `ProjectMemberRole` rows. The existing rows stay unchanged when connect is refused.

### Implementation for User Story 4

- [X] T017 [US4] In `apps/api/core/projects/member_views.py` and `apps/api/core/projects/services/__init__.py`, create the membership and assign roles inside one `transaction.atomic` block. Assign roles only after the membership insert. Turn `IntegrityError` into HTTP 409 `already_member` with a translated message that the membership already exists. Roll back the failed attempt so roles cannot remain without the membership.

**Checkpoint**: Conflict handling is testable without the later status stories.

---

## Phase 7: User Story 5 - Two projects, suspension, and exit (Priority: P2)

**Goal**: Ending membership in project A leaves project B and the organizational account unchanged. History and the author name remain. Delegated team management can be granted and revoked for one project.

**Independent Test**: The person can edit in A and only read in B. Suspending or archiving A does not change B or the account. A document and its author remain. After `manage_members` is removed, the next request is refused.

### Tests for User Story 5

- [X] T018 [US5] Add failing tests to `apps/api/core/projects/tests/test_team_lifecycle.py` and `apps/api/core/authentication/tests/test_account_lifecycle.py` for different roles in two projects, suspending A without changing B or account status, archiving A without changing `joined_at`, restoring `archived` on the same row, a role change on an inactive member not granting access, delegated `manage_members` limited to A, and HTTP 403 after that authority is removed. Admin deletion of a person who has a membership is refused.

### Implementation for User Story 5

- [X] T019 [US5] In `apps/api/core/projects/member_views.py`, accept status `active`, `inactive`, `invited`, `suspended`, and `archived` on the existing user-id patch. Only `active` grants project authority. Do not change `joined_at`, the other project's membership, or account status. Restoring `archived` updates the same row. Record `member_status_changed` through `record_access_change` with actor, person, project, time, and the status difference.
- [X] T020 [P] [US5] Refuse Django admin deletion in `apps/api/core/authentication/admin.py` when the person has a membership, an audit row, an access-change row, or any other related history row. Unused password-reset tokens may be removed with an unused account. Do not add a delete action to the team or account screens.
- [X] T021 [US5] Show all five membership statuses and the status action in `apps/web/src/app/routes/project-members.tsx`. Use Persian and English labels in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`: active, inactive, invited, suspended, and archived. Archived is the left-project label, not a second inactive label.

**Checkpoint**: Two-project authority and exit with history are testable.

---

## Phase 8: User Story 6 - Account status, recovery, and account switch (Priority: P2)

**Goal**: Inactive and suspended accounts cannot sign in or continue a later request. Logout and password change follow the current one-hour rule. The next account does not receive the previous account's project cache or offline queue.

**Independent Test**: An active person signs in with username and with mobile. A wrong password fails. An inactive or suspended account fails login and the next request. Logout refuses the old refresh token. A used reset token fails. The next account does not show the previous project data or submit the previous queue.

### Tests for User Story 6

- [X] T022 [US6] Add failing account-status tests to `apps/api/core/authentication/tests/test_account_lifecycle.py`: `PATCH /api/auth/users/{user_id}/account-status/` accepts only `active`, `inactive`, and `suspended`; a non-administrator receives HTTP 403; `inactive` and `suspended` set the sign-in flag off and fail login and a later authenticated request; returning to `active` sets the sign-in flag on; the alignment migration does not re-enable a blocked person; memberships remain.
- [X] T023 [P] [US6] Extend `apps/api/core/authentication/tests/test_credential_security.py` and `apps/api/core/authentication/tests/test_auth_api.py` to re-check the current behavior: logout blacklists the presented refresh token; password change and reset reject the old password, a used or expired reset token, and refresh tokens issued before the change; unused reset tokens are retired; the reset response uses the same message for an unknown and a known mobile and does not say a message was sent unless `delivery_status` is `sent`.

### Implementation for User Story 6

- [X] T024 [US6] Add `PATCH /api/auth/users/{user_id}/account-status/` in `apps/api/core/authentication/views.py` and `apps/api/core/authentication/urls.py`, limited to `IsHrOrAdmin`. The body is `status` with `active`, `inactive`, or `suspended`. Set the sign-in flag from that status and do not accept a separate sign-in flag. Record `account_status_changed` with no project, no password, and no token.
- [X] T025 [US6] In `apps/api/core/authentication/services.py`, call `update_last_login` only after a successful login, not after refresh and not after a failed login. Include `delivery_status` on password reset and use the helper from T005. Keep the one-hour access lifetime and the existing refresh blacklist. Do not add immediate revocation of an already issued access credential.
- [X] T026 [US6] In `apps/api/core/authentication/admin.py`, save the visible status as the authority: `active` turns sign-in on, and `inactive` or `suspended` turns it off. Reject a saved pair that contradicts that result.
- [X] T027 [US6] Add the account-status action for an account administrator in `apps/web/src/app/routes/hr/users.tsx`. In `apps/web/src/app/contexts/auth-context.tsx`, logout must clear the stored session and call `prepareQueryActor()` with no actor before a different account can sign in, so the previous project queries and the previous actor-scoped offline queue are not used for the next account. Do not redesign `apps/web/src/app/lib/offlineDB.ts`.

**Checkpoint**: Account closure and the session boundary are testable without the team-list labels.

---

## Phase 9: User Story 7 - Team list with real times (Priority: P3)

**Goal**: The team list shows roles, membership status, join time, and last sign-in. Last sign-in is only a successful login, and an empty value stays empty.

**Independent Test**: Members with different roles and statuses are visible and searchable. After login, last sign-in matches that login. A person who has never signed in has no last-sign-in value. A later project action does not change it.

### Tests for User Story 7

- [X] T028 [US7] Add failing list tests to `apps/api/core/projects/tests/test_team_lifecycle.py`: the member list includes roles, status, `joined_at`, and `last_login`; `last_login` is null before a successful login; a successful login sets it; a membership update does not change it; a null value is not replaced with `joined_at` or the current time.

### Implementation for User Story 7

- [X] T029 [US7] In `apps/api/core/projects/member_serializers.py`, return membership `id`, roles, status, `joined_at`, `delivery_status`, `invite_expires_at`, and `last_login` from `user.last_login` only. Return null when the person has never signed in.
- [X] T030 [US7] In `apps/web/src/app/routes/project-members.tsx`, filter the loaded team by name and render a blank last-sign-in cell when `last_login` is null. Do not show an em dash or the join date in that cell. Keep the label `projectMembers.lastLogin` as last sign-in in `apps/web/src/app/locales/en.json` and `آخرین ورود` in `apps/web/src/app/locales/fa.json`.

**Checkpoint**: All seven stories are independently testable.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Localized text, regression commands, and the browser check

- [X] T031 [P] Check that every new refusal and status label exists in both Persian and English in `apps/web/src/app/locales/fa.json`, `apps/web/src/app/locales/en.json`, and `apps/api/core/locale/fa/LC_MESSAGES/django.po`. Permission codes and status identifiers stay language-independent.
- [X] T032 Run the pytest modules named in `specs/047-a6-p3-team-lifecycle/quickstart.md` from `apps/api/core` against the test database. Do not reset the development database and do not upgrade Django.
- [X] T033 Perform the browser scenarios in `specs/047-a6-p3-team-lifecycle/quickstart.md` on two projects: select the same person, refuse account creation for a project manager, connect an unsent invitation, show the five statuses and a blank last sign-in, and switch accounts without showing the previous project cache or submitting the previous offline queue.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately
- **Foundational (Phase 2)**: Depends on T001 because T004 also edits `apps/api/core/config/settings.py`. Blocks every user story
- **User Stories (Phases 3–9)**: Depend on Phase 2
- **Polish (Phase 10)**: Depends on the stories being present

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2. No dependency on later stories. MVP
- **User Story 2 (P1)**: Starts after Phase 2. Uses the person selected by Story 1, but its API test does not need the team screen
- **User Story 3 (P1)**: Starts after Phase 2 and after T007, because create and invitation share `apps/api/core/projects/member_views.py`
- **User Story 4 (P1)**: Starts after T014, because the conflict handler wraps the same create path
- **User Story 5 (P2)**: Starts after T017, because status changes share `member_views.py`
- **User Story 6 (P2)**: Starts after Phase 2. Its authentication files do not wait for the team stories, except T026 waits for T020 because both edit `apps/api/core/authentication/admin.py`
- **User Story 7 (P3)**: Starts after T014 so the list includes invitation fields, and after T025 so last sign-in is actually recorded

### Within Each User Story

- The story test is written and fails before that story's implementation
- Schema from Phase 2 comes before services
- API behavior comes before the screen that calls it
- Shared files are sequenced, not marked parallel: `member_views.py` is T007 → T014 → T017 → T019; `add-member-drawer.tsx` is T008 → T011 → T015; `project-members.tsx` is T015 → T021 → T030; `test_team_lifecycle.py` is T006 → T013 → T016 → T018 → T028; `test_account_lifecycle.py` is T009 → T018 → T022; `authentication/admin.py` is T020 → T026

### Parallel Opportunities

- T002, T003, T004, and T005 touch different files and can run together after T001
- T008 can run with T007
- T009 can run with Story 1
- T012 can run with T010
- T020 can run with T019
- T023 can run with T022
- T031 can run beside the last story implementation

---

## Parallel Example: User Story 1

```bash
# After T006 has defined the failing API test:
Task: "T007 Keep same-user selection and 403 refusals in apps/api/core/projects/member_views.py"
Task: "T008 Keep search and select without account creation in apps/web/src/components/projects/add-member-drawer.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3
3. Stop and run the Story 1 tests in `apps/api/core/projects/tests/test_team_lifecycle.py`
4. Demonstrate that one person is added to two projects without a second account

### Incremental Delivery

1. Setup and foundation
2. Story 1: select an existing person
3. Story 2: create a person only with account authority
4. Story 3: invitation, connect, cancel, and honest delivery status
5. Story 4: one membership under repeated and concurrent adds
6. Story 5: two projects, suspension, exit, and delegated team management
7. Story 6: account status, recovery, logout, and account switch
8. Story 7: team list labels and real last sign-in
9. Polish: both languages, pytest, and the browser check

### Parallel Team Strategy

After Phase 2:

- One developer can take Stories 1, 3, and 4 in order, because they share the member view
- Another developer can take Story 2 and Story 6, because they share the authentication files
- Story 5 follows the member-view sequence
- Story 7 follows the recorded last sign-in and the invitation list fields

---

## Notes

- [P] means a different file and no unfinished dependency
- Story labels map tasks to spec stories
- Existing successful member and credential behavior is re-checked, not rebuilt
- Do not choose a messaging provider
- Do not reset the development database
- Commit after each task or logical group

## Phase 11: Convergence

- [X] T034 CRITICAL: Enforce open-invitation validation in `_connect_invitation` and `ProjectMemberViewSet.connect_invitation` (reject rows with an existing `user_id`, non-`invited` status, `invite_accepted_at`, `invite_cancelled_at`, or expired `invite_expires_at` with HTTP 400 `invitation_invalid`) in `apps/api/core/projects/services/__init__.py` and `apps/api/core/projects/member_views.py` per Constitution I, Constitution IV, FR-005, SC-004, US3/AC3 (contradicts)
- [X] T035 CRITICAL: Remove organizational `User.status` mutation from project-scoped `PersonDossierView.patch` and `update_dossier` in `apps/api/core/hr/capacity_views.py` and `apps/api/core/hr/services/dossier_service.py`, and enforce explicit organizational account-admin permission (`is_superuser` or `admin`/`hr` group, excluding bare `is_staff`) on `UserListView` and `AccountStatusView` in `apps/api/core/authentication/permissions.py` and `apps/api/core/authentication/views.py` per Constitution I, Constitution II, FR-010, FR-014, US5/AC1 (contradicts)
- [X] T036 CRITICAL: Wrap and translate `ProjectMemberCreateSerializer` validation messages in `apps/api/core/projects/member_serializers.py` and `apps/api/core/locale/fa/LC_MESSAGES/django.po` (compiling `django.mo`), override default `UniqueValidator` precedence on `UserSerializer` in `apps/api/core/authentication/serializers.py` so account edits return translated duplicate `username`/`mobile` errors, and normalize `DjangoValidationError` responses in `UserListView.post`, `ChangePasswordView`, and `ResetPasswordView` in `apps/api/core/authentication/views.py` to the standard `{error: {code, message, details}}` envelope per Constitution III, FR-004, FR-015, SC-003, T010, T031 (partial)
- [X] T037 CRITICAL: Align `HrUserRow` types (`id: string` and optional `status`) between `apps/web/src/app/hooks/queries.ts` and `apps/web/src/app/routes/hr/users.tsx` so `pnpm typecheck` passes with exit code 0 per Constitution VI, T027 (contradicts)
- [X] T038 CRITICAL: Update `apps/web/src/app/routes/forgot-password.tsx` and `apps/web/src/app/locales/fa.json` / `apps/web/src/app/locales/en.json` to inspect `delivery_status` and `message` from `POST /api/auth/forgot-password/` and never claim a reset code was sent when `delivery_status` is `not_configured` or `not_sent` per FR-006, SC-005, US3/AC4, T025 (contradicts)
- [X] T039 Extend the team create-person flow in `apps/web/src/components/projects/add-member-drawer.tsx`, `apps/web/src/app/lib/api/members.ts`, and `apps/api/core/authentication/serializers.py` to accept `username` and `status` (`active`, `inactive`, `suspended` synced with `is_active`), validate duplicate/password/confirmation rules consistently in form and API, and keep the create-person option available regardless of search substring matches and when connecting an unconnected invitation per FR-003, US2/AC1, US2/AC2, US2/AC3, US3/AC2, SC-002, SC-003, T010, T011 (partial)
- [X] T040 Expose `invite_cancelled_at` and fall back `full_name` to `invited_mobile` for mobile-only invitations in `apps/api/core/projects/member_serializers.py`, and update `apps/web/src/app/routes/project-members.tsx`, `apps/web/src/components/projects/add-member-drawer.tsx`, `apps/web/src/app/locales/fa.json`, and `apps/web/src/app/locales/en.json` to distinguish cancelled invitations (hiding connect/cancel actions), surface `delivery_status`, support searching mobile-only invitations, and persist edited role/position selections when connecting an invitation per FR-005, FR-013, US3/AC2, US7/AC1, T015 (partial)
- [X] T041 Expand `clearProjectSessionQueries` in `apps/web/src/app/lib/react-query.ts` and update `apps/web/src/app/lib/__tests__/offlineActorCache.test.ts` to cancel and remove `projects`, `portfolio-summary`, `members`, `roles`, `access-changes`, `member-permissions`, `selectable-positions`, and HR user queries on logout and account switch per FR-012, SC-010, US6/AC4, T027 (partial)
- [X] T042 Add missing backend tests in `apps/api/core/projects/tests/test_team_lifecycle.py` and `apps/api/core/authentication/tests/test_account_lifecycle.py` covering successful `connect_invitation`, expired and cancelled invitation connect/accept refusal, `TEAM_DELIVERY_TEST_RECIPIENT` operational `sent` vs `not_sent`/console SMS, absence of raw tokens or passwords in `RoleAccessChange`, distinct two-project roles with post-exit refusal and same-row `archived` to `active` restoration, and `UserAdmin` delete refusal on audit/`RoleAccessChange` history plus `save_model` status synchronization per SC-004, SC-007, SC-012, T013, T018, T020, T026 (partial)
- [X] T043 Record the open delivery-channel condition naming the customer channel owner and document final pytest, `pnpm typecheck`, and bilingual browser verification evidence (two-project selection, PM account-creation refusal, unsent invitation connect, five membership statuses, blank `last_login`, and account-switch cache/offline-queue isolation) in `specs/047-a6-p3-team-lifecycle/quickstart.md` and `specs/047-a6-p3-team-lifecycle/traceability.md` per FR-006, SC-005, US3/AC4, T032, T033 (missing)

## Phase 12: Convergence

- [X] T044 CRITICAL: Enforce `account_can_authenticate` and `CHECK_REVOKE_TOKEN` password-hash validation in `TokenRefreshView` / a custom refresh serializer, record rotated refresh tokens in `OutstandingToken`, verify refresh-token ownership in `LogoutView`, and blacklist outstanding refresh tokens when `AccountStatusView` or `UserAdmin` transitions an account to `inactive` or `suspended` in `apps/api/core/authentication/views.py`, `apps/api/core/authentication/serializers.py`, `apps/api/core/authentication/services.py`, and `apps/api/core/authentication/admin.py` per Constitution I, FR-010, FR-012, US6/AC2, US6/AC3, SC-009, SC-010, T004, T022, T023 (contradicts)
- [X] T045 CRITICAL: Expose `position_ids` on `ProjectMemberListSerializer` (with `positions` prefetched in `ProjectMemberViewSet`) in `apps/api/core/projects/member_serializers.py` and `apps/api/core/projects/member_views.py`, hydrate `selectedPositions` plus reset transient search/selection/create state whenever `editMember` or `isOpen` changes in `apps/web/src/components/projects/add-member-drawer.tsx` and `apps/web/src/app/lib/api/members.ts`, and add a regression test in `apps/api/core/projects/tests/test_team_lifecycle.py` so editing a member never wipes assigned job titles per Constitution II, FR-008, FR-016 (contradicts)
- [X] T046 CRITICAL: Route serializer and DRF `ValidationError` responses in `LoginView`, `ChangePasswordView`, `ForgotPasswordView`, and `ResetPasswordView` through the standard `{error: {code, message, details}}` envelope in `apps/api/core/authentication/views.py`, update `apps/web/src/app/routes/reset-password.tsx` and `apps/web/src/app/routes/forgot-password.tsx` to extract localized error messages via `apiJson` without crashing on object error envelopes, and surface localized error feedback on `updateAccountStatus` while allowing `is_superuser` access alongside `hr`/`admin` in `apps/web/src/app/routes/hr/users.tsx` and `apps/api/core/authentication/serializers.py` per Constitution III, Constitution IV, Constitution VII, FR-004, FR-015, SC-003 (contradicts)
- [X] T047 CRITICAL: Format `joined_at`, non-null `last_login` (keeping `null` strictly blank), and recent access-change timestamps with locale-aware `formatLocaleDateTime` in `apps/web/src/app/routes/project-members.tsx` so English renders Gregorian and Persian renders Jalali with `HH:MM` timestamps, and invalidate `["access-changes", projectId]` after member mutations in `apps/web/src/app/routes/project-members.tsx` and `apps/web/src/components/projects/add-member-drawer.tsx` per Constitution III, FR-013, SC-011, US7/AC1, US7/AC3 (contradicts)
- [X] T048 Allow up to 60-character usernames as well as mobile numbers in `LoginSerializer` and the login form in `apps/api/core/authentication/serializers.py`, `apps/web/src/app/routes/login.tsx`, `apps/web/src/app/locales/fa.json`, and `apps/web/src/app/locales/en.json`, require non-blank `mobile` on `UserRegistrationSerializer` while normalizing/rejecting blank `mobile` or `username` on `UserSerializer`, and add `T023` regression tests (distinct `username` and `mobile` login, refresh rejection after password change/reset and account suspension, old-password login rejection, and bilingual profile-edit duplicate/password errors) in `apps/api/core/authentication/tests/test_auth_api.py` and `apps/api/core/authentication/tests/test_credential_security.py` per FR-003, FR-004, FR-011, US2/AC3, US6/AC1, SC-003, SC-009, T023 (partial)
- [X] T049 Cancel all in-flight queries and clear the full React Query cache (`queryClient.cancelQueries()` and `queryClient.clear()`) in `clearProjectSessionQueries` in `apps/web/src/app/lib/react-query.ts` so all project module caches (WBS, activities, daily reports, contracts, progress, risks, roles) are evicted on logout and account switch, and expand `apps/web/src/app/lib/__tests__/offlineActorCache.test.ts` per FR-012, SC-010, US6/AC4, T027 (partial)
- [X] T050 Check per-channel operational status in `delivery_plan` in `apps/api/core/notifications/services/delivery.py`, validate roles/positions and retire expired uncancelled invitations for the same project and email/mobile before sending `deliver_account_message` in `create_project_member` in `apps/api/core/projects/services/__init__.py`, include `invited_email`/`invited_mobile`/`member_id` on `invitation_cancelled` history with fallback `subject_name` in `ProjectAccessChangeListView` in `apps/api/core/projects/local_role_views.py`, skip no-op `account_status_changed` records in `AccountStatusView`, and reject contradictory `(status, is_active)` form submissions while recording status changes in `UserAdmin` in `apps/api/core/authentication/admin.py` per FR-005, FR-006, FR-010, FR-014, SC-005, SC-012, T005, T014, T024, T026 (partial)
- [X] T051 Add the explicit Person fields (name, mobile, username, organization, unit, account status) versus Membership fields (project, roles, job titles, membership status, join time) separation table and the one-hour post-logout access-token lifetime rule to `specs/047-a6-p3-team-lifecycle/quickstart.md` per FR-001, FR-012 (missing)

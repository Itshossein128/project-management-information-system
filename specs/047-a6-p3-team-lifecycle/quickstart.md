# Quickstart: A6-P3

From `apps/api/core`, with the repository `.env` loaded and the test database, not the development database:

```bash
../.venv/bin/python -m pytest \
  projects/tests/test_members.py \
  projects/tests/test_team_lifecycle.py \
  authentication/tests/test_auth_api.py \
  authentication/tests/test_credential_security.py \
  authentication/tests/test_account_lifecycle.py
```

Do not drop or recreate the development database. Django stays on 4.2. Do not install the full development requirements file.

The account-switch check is in the browser, not a separate web test runner. Sign out, sign in as the other person, and confirm the previous project cache is gone and the previous offline queue is not submitted. The queue remains the existing actor-scoped queue in `apps/web/src/app/lib/offlineDB.ts`.

The browser check uses two projects, an account administrator, a project team manager, a viewer, and one agreed test recipient only when a real channel is configured. Otherwise the check records `not_configured` and finishes through account creation and connect.

Person fields are name, mobile, username, organization, unit, and account status. Membership fields are project, roles, job titles, membership status, and join time. The same person fields appear on every membership. After sign-out, a previously issued access credential remains usable only until its current one-hour lifetime ends and cannot be renewed.

## Verification recorded 2026-11-06

The open delivery condition stays with the customer channel owner. No provider was selected. `TEAM_DELIVERY_TEST_RECIPIENT` is empty unless that owner sets it. Console email and console SMS are not `sent`.

Pytest on the test database, without resetting the development database, covered `projects/tests/test_team_lifecycle.py`, `projects/tests/test_members.py`, `authentication/tests/test_account_lifecycle.py`, `authentication/tests/test_auth_api.py`, and `authentication/tests/test_credential_security.py`. `pnpm typecheck` is the frontend check. The browser check on the Persian member screen showed name search, the five membership statuses, a blank last sign-in, and the create-person form. The account screen showed active, inactive, and suspended. A live account was not changed and a new person was not saved.

## Scenarios

1. An account administrator creates one person. The team manager of project A selects that same person. The team manager of project B selects that same person. There is still one person. The project manager cannot create an organizational account.
2. A duplicate mobile, duplicate username, invalid password, and mismatched confirmation are refused on create and on edit.
3. An invitation without a person can be connected or cancelled from the team screen. Acceptance by the matching person creates one active membership. An expired, cancelled, used, or mismatched invitation grants nothing. When delivery is not operational, the response is not `sent`.
4. Two concurrent adds for one person and one project leave one membership and no partial roles. A second request returns `already_member`.
5. The person can edit in project A and only read in project B. Suspending A leaves B and the account unchanged. A document and its author remain after A is archived. A delegated team manager manages only A, and the next request fails after that authority is removed.
6. An active person signs in with username and with mobile. A wrong password fails. An inactive or suspended account cannot sign in or call the API afterward. Alignment does not re-enable a blocked account.
7. Logout refuses the old refresh token. After one hour the old access credential is refused. Password change refuses the old password and a used reset token. The next account on the same browser does not show the previous project cache or submit the previous offline queue.
8. The team list shows roles, all five membership statuses, join time, and last sign-in. A person who has not signed in has no last-sign-in value. A later project action does not change that value.
9. Each new invitation, status change, and account-status change has a base history record without a password or token.

Details of the requests are in [contracts/team-lifecycle.md](./contracts/team-lifecycle.md). Field ownership is in [data-model.md](./data-model.md).

# Contract: A6-P3 account and team lifecycle

Existing member and user routes stay. This phase adds the missing invitation actions, account status, and response fields.

## Select an existing person

`GET /api/v1/users/lookup/?q=`

Unchanged search. The team screen uses it to select a person. Creating the membership is still:

`POST /api/v1/projects/{project_id}/members/`

```json
{ "user_id": "<uuid>", "role_ids": ["<uuid>"], "position_ids": ["<uuid>"] }
```

The caller must be an active member with `manage_members`. A viewer, a non-member, an inactive member, and a caller with an explicit deny receive a refusal. The response uses the same user id. A second account is not created.

A repeated or concurrent add for that person and project returns HTTP 409, code `already_member`. No second membership and no partial role rows remain. The message tells the caller the membership already exists.

## Create a person

`POST /api/auth/users/`

This remains the account-administrator endpoint: `admin`, `hr`, staff, or superuser. A project manager with only `manage_members` receives HTTP 403. The team screen calls this endpoint and then adds the membership. The body stays the current registration body: name, mobile, username or email, password, and password confirmation.

Duplicate username or mobile, an invalid password, and a mismatched confirmation return HTTP 400 with the same field errors on create and on a later edit. Messages are translated.

The created person receives the `visitor` group only. The request does not assign `admin` or `hr`.

## Account status

`PATCH /api/auth/users/{user_id}/account-status/`

```json
{ "status": "active" }
```

`status` is `active`, `inactive`, or `suspended`. The caller must pass the account-administrator gate. The response includes `status` and `can_sign_in`. It does not accept a separate sign-in flag.

`inactive` and `suspended` fail login and fail a later request that still carries an access credential. Memberships are not deleted. Changing this status does not change another project's membership.

## Invitation

`POST /api/v1/projects/{project_id}/members/`

```json
{ "email": "person@example.com", "mobile": "+989120000000", "role_ids": ["<uuid>"] }
```

At least one of `email` or `mobile` is required when `user_id` is absent. The caller must have `manage_members`. The created row has no user, status `invited`, expiry seven days ahead, and `delivery_status` of `sent`, `not_sent`, or `not_configured`.

`sent` is returned only when an operational channel delivers to the configured test recipient. Console delivery is `not_configured` or `not_sent`, never `sent`.

The list row includes:

- `id`: membership id
- `user_id`: null until connected
- `delivery_status`
- `invite_expires_at`
- `last_login`: null when that person has never signed in

`POST /api/v1/projects/{project_id}/members/invitations/{member_id}/connect/`

```json
{ "user_id": "<uuid>" }
```

An account administrator or a team manager connects an existing person. If that person is already a member of the project, the response is `already_member` and neither row changes. On success the same membership gains the user and becomes `active` only when the account can sign in.

`POST /api/v1/projects/{project_id}/members/invitations/{member_id}/cancel/`

The team manager cancels it. A later accept grants nothing.

`POST /api/auth/invitations/accept/`

```json
{ "token": "<secret>" }
```

The caller is signed in. The token must be unexpired, unused, and uncanceled, and the caller's email or mobile must match the invitation. Otherwise nothing is granted. A matching active account becomes an active member on that same row.

The current `PATCH /api/v1/projects/{project_id}/members/{user_id}/` route remains for a membership that has a user.

## Membership status and roles

`PATCH /api/v1/projects/{project_id}/members/{user_id}/`

```json
{ "status": "suspended", "role_ids": ["<uuid>"] }
```

Status is one of `active`, `inactive`, `invited`, `suspended`, `archived`. Only `active` grants project authority. `joined_at` does not change. Project B and the account status do not change. Restoring `archived` updates this row.

## Team list

`GET /api/v1/projects/{project_id}/members/`

Returns name, roles, membership status, `joined_at`, and `last_login`. `last_login` is the last successful sign-in. The screen filters by name and shows the five statuses in Persian and English. An empty last sign-in is blank, not a date and not the join time.

## Sign-in, logout, and recovery

Login with username or mobile records last sign-in. Wrong password does not. A non-active account does not.

Logout blacklists the presented refresh token. Refresh after logout is refused. An access credential issued before logout works only until the current one-hour lifetime ends.

Password change and reset refuse the old password, refuse a used or expired reset token, retire unused reset tokens, and refuse refresh tokens issued before the change. The reset body includes `delivery_status`. Its message does not say a message was sent unless `delivery_status` is `sent`. Unknown and known mobiles get the same response.

Switching accounts clears the previous account's stored session and project queries. The previous account's offline queue is not submitted for the next account.

## History

Successful invitation, connect, cancel, accept, role replacement, membership status, and account status actions append a base history record. Account status has an empty project. The record has the actor, person, time, and difference. It has no password and no token.

`GET /api/v1/projects/{project_id}/access-changes/`

Still returns the recent project records from A6-P2. It is not the finished history screen.

## Errors

Refusals are translated in Persian and English. Codes used by this phase:

- `already_member`
- `invitation_invalid`
- `account_forbidden`
- `channel_not_configured`

A save that fails does not leave a membership without its roles, or roles without a membership.

## Screens

The team screen offers search and select, account creation, invitation, connect, cancel, role and status changes, and the labeled team list. Account creation that returns `account_forbidden` leaves search available. The account screen used by HR changes account status. Neither screen offers physical delete.

## Delivery guide fields

Person fields: name, mobile, username, email, organization, unit, account status, last sign-in.

Membership fields: project, roles, job titles, membership status, join time, invitation expiry, delivery status.

The same person field values appear in every project membership. Membership fields differ by project.

# Data model: A6-P3

No second person or membership table. Existing rows remain valid.

## Person

Existing user.

- Visible status: `active`, `inactive`, or `suspended`.
- Sign-in is allowed only when status is `active` and the existing sign-in flag is on.
- A status write sets the sign-in flag. `active` turns it on. `inactive` and `suspended` turn it off. The API does not accept a contradictory pair.
- Alignment of old rows never turns sign-in on. An active person who cannot sign in becomes `inactive`. A non-active person who can sign in keeps that non-active status and loses sign-in.
- Username and mobile stay unique.
- Password and confirmation use the existing password rules.
- A new person created by an account administrator receives the existing default `visitor` group only.
- The person is not deleted by leaving a project or by suspending the account.

## Membership

Existing project membership.

- One row for each project and person. The partial uniqueness on project plus user stays.
- Status stays `active`, `inactive`, `invited`, `suspended`, or `archived`.
- Only `active` grants project authority. Changing roles does not change this.
- `joined_at` is set when the row is created and is not changed by a later status update.
- `user` is protected. Deleting the person must not delete the membership.
- Pending invitations for the same project and the same email, or the same project and the same mobile, are unique.

Invitation fields added to this row:

- `invited_mobile`: optional, used when the invitation is addressed to a mobile.
- `invite_expires_at`: seven days after creation. Existing open invitations receive seven days from the migration.
- `invite_token_hash`: hash of the single-use token. Empty for an old invitation that was never given a token. The raw token is not stored.
- `invite_cancelled_at`: set by cancellation. Empty otherwise.
- `invite_accepted_at`: set when the matching person accepts or an authorized manager connects the person.
- `delivery_status`: `not_configured`, `not_sent`, or `sent`.

An invitation grants authority only after it has a user, `invite_accepted_at` is set, membership status is `active`, and the account can sign in.

## Account status transition

- `active` to `inactive` or `suspended`: sign-in stops. Memberships remain.
- `inactive` or `suspended` to `active`: sign-in returns. Project authority still depends on each membership.
- A membership status change does not move this status.

## Membership status transition

- `invited` to `active`: only by matching acceptance or by connecting an account that can sign in.
- `active` to `inactive`, `suspended`, or `archived`: project authority stops. The other project and the account stay unchanged.
- `inactive` or `suspended` to `active`: an authorized team manager restores the same row.
- `archived` to `active`: the same row is restored. A second row is not created.
- `invited` stays without authority when cancelled or expired.

## Delivery

No new provider.

- `sent` only after an operational email or SMS send to `TEAM_DELIVERY_TEST_RECIPIENT`.
- Console, locmem, dummy email, and console SMS are not operational.
- An unconfigured or unmatched recipient stays `not_configured` or `not_sent`.

## Base history

Existing `RoleAccessChange` row. New action names:

- `invitation_created`
- `invitation_cancelled`
- `invitation_accepted`
- `member_status_changed`
- `account_status_changed`

Role replacement already records `roles_replaced`. Account status has no project. The stored difference contains status and role identifiers, never a password or token.

## Migration and rollback

- Schema changes are a normal migration: invitation columns, pending-invitation uniqueness, and protected membership user.
- The account alignment is a data migration. Its reverse does not turn sign-in back on, because the old contradictory combination is not a safe state to restore.
- Existing memberships, roles, and history rows are not rewritten except for the expiry given to open invitations and the account alignment above.

## Deletion guard

Admin deletion of a person is refused when any membership, audit row, access-change row, or other related history row exists. Unused password-reset tokens may be removed with an unused account. The team and account screens have no delete action.

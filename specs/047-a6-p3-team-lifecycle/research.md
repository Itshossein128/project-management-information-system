# Research: A6-P3 team and account lifecycle

## Decision: Keep one person and one membership row

A person remains the existing user record. A project membership remains `ProjectMember`. The same user id is added to a second project. Account creation continues through the existing HR/admin user endpoint. The team screen calls that endpoint and then the existing member endpoint. It does not gain a second user table or a second membership table.

Rationale: The person, the membership, the role assignment, and the tests already exist. A parallel account would break the one-person rule.

Alternatives considered: A new invitation table and a team-only user record. Rejected because both would fork the current member and login behavior.

## Decision: Account administration stays on the current HR/admin gate

Creating a person and changing account status stay behind `IsHrOrAdmin`: the `admin` group, the `hr` group, staff, or a superuser. `manage_members` does not pass that gate. A project manager can search and select an existing person. The team screen shows account creation, and the existing endpoint refuses it when the caller lacks the account gate. The default new person still receives only the existing `visitor` group. This screen does not assign `admin` or `hr`.

Rationale: The acceptance test says HR creates the person, the project manager selects that person, and an ordinary user cannot administer organizational accounts. The `hr` group is the existing assigned account authority. Changing that set would be a different policy from the one this phase tests.

Alternatives considered: Letting every project manager create users. Rejected because it gives project authority an organizational power. Removing staff from the current gate. Rejected because this phase does not rewrite the account gate.

## Decision: Account status is the visible source, and sign-in follows it

The visible values remain `active`, `inactive`, and `suspended`. A saved `active` account can sign in. A saved `inactive` or `suspended` account cannot. The write path sets the existing sign-in flag from that status and does not accept the opposite combination. Login and later requests both use that rule.

Existing rows are aligned without enabling anyone who is blocked:

- `active` with sign-in off becomes `inactive` and stays unable to sign in.
- `inactive` or `suspended` with sign-in on keeps that status and loses sign-in.
- `active` with sign-in on stays unchanged.

Leaving one project does not change this status. Suspending the account does not delete memberships.

Rationale: The two fields can already disagree because admin edits them separately. The spec requires one visible authority and forbids re-enabling a blocked person during alignment.

Alternatives considered: Making the sign-in flag the authority and overwriting status. Rejected because a suspended person could be shown as active. Leaving the fields independent. Rejected because that is the current defect.

## Decision: An invitation is the same membership until it is connected

An invitation is a `ProjectMember` with no user, status `invited`, an email or mobile, an expiry, and a hashed single-use token. The list includes the membership id so the form can address that row. The current user-id route stays for members who have a user. Connect and cancel use the membership id. Accept requires a signed-in person whose email or mobile matches the invitation, an unexpired token, and no earlier acceptance or cancellation. Acceptance attaches that user and makes the membership active only when the account can sign in. A cancelled, expired, used, or mismatched invitation grants nothing.

An existing open invitation without a token stays connectable or cancellable. The migration gives it seven days from the migration time. It does not invent a token.

If the selected person already has a membership in that project, including an inactive, suspended, or archived one, connect and create both refuse and leave the rows unchanged. Restoring access is a status change on that same membership.

Rationale: The current edit route cannot see a membership that has no user. Extending the same row removes the dead end without a second invitation product.

Alternatives considered: Editing an invitation only by email. Rejected because two invitations could share an address and the form still could not target one row.

## Decision: Real delivery uses the existing settings and never pretends

No provider, price, or sending policy is added. Email is operational only when `EMAIL_BACKEND` is not the console, locmem, or dummy backend. SMS is not operational while `SMS_PROVIDER` is `console` or while the only backend is the current console logger. In-app notifications do not count as delivery to someone who cannot sign in. `TEAM_DELIVERY_TEST_RECIPIENT` must match the invitation address or reset mobile before a real send is attempted. It is empty unless the customer channel owner sets it.

The response says `sent` only after that operational send succeeds. Otherwise it says `not_configured` or `not_sent`. A console log and a token test are not `sent`. The reset response stays the same for an unknown mobile and a known mobile. The team can still finish by creating the account and connecting or cancelling the invitation.

Rationale: The current reset call logs that SMS is not configured and returns false, while the console SMS helper used by alerts returns true. Those are not proof of receipt.

Alternatives considered: Treating console email or console SMS as success. Rejected by the spec. Selecting a new SMS vendor. Rejected because this phase must not choose a provider.

## Decision: Duplicate and concurrent adds leave one membership

The existing partial unique constraint on project plus user stays. Create runs in one transaction, assigns roles only after the membership insert, and turns a constraint conflict into an actionable `already_member` response. The failed attempt leaves no membership and no role rows. The same transaction handles a repeated open invitation for the same project and email or mobile. Role replacement already deletes and recreates role rows inside the caller's transaction, so a failed create rolls those rows back too.

Rationale: The current code checks for an existing row and then inserts. Two overlapping requests can pass the check, and an uncaught constraint error is not an actionable result.

Alternatives considered: Catching the error after roles were committed. Rejected because the spec forbids a partial role assignment.

## Decision: Membership status keeps its current values

`active`, `inactive`, `invited`, `suspended`, and `archived` stay. Only `active` grants project authority. `inactive` and `suspended` can be returned to `active` by a team manager. `archived` is the left-project state; returning uses the same row. `joined_at` is not updated by a status change. Giving a role to a non-active member does not grant access. Project A does not change project B or the account status.

The team screen shows all five states in Persian and English. The current screen collapses every non-active value into inactive.

Rationale: The values and the active-member permission check already exist. The missing part is the visible distinction and the separate tests.

Alternatives considered: Adding a new left-project status. Rejected because `archived` already means that and a second value would split the history.

## Decision: Removal is a status change

The team and account screens do not offer physical deletion. `ProjectMember.user` changes from cascade delete to protect, so deleting a person cannot erase memberships. Django admin delete is refused when the person has a membership, an audit row, an access-change row, or any related row other than an unused password-reset token. The author name on existing records stays because the person row stays.

Rationale: Membership currently cascades from the user. Admin can still delete a user, which would remove the membership and damage history. This phase does not retarget every author field in the product.

Alternatives considered: A hard delete that copies the name into every document. Rejected as a broad rewrite. Leaving cascade in place. Rejected because it fails the history requirement.

## Decision: Sign-in, remaining access, and account switch stay on the current session mechanism

Successful username or mobile login records `last_login`. Refresh and ordinary project work do not. The member column labeled last sign-in shows that value, or nothing when it is null. It is not labeled as last work activity.

Logout continues to blacklist the presented refresh token. Password change and password reset continue to blacklist outstanding refresh tokens and retire unused reset tokens. An access credential already issued remains usable only until its current one-hour lifetime and cannot be renewed after logout or password change. Login and later API use both refuse an inactive or suspended account.

Logout already clears the stored session and the project query cache when the actor changes. The offline queue remains filtered by actor. This phase tests that boundary. It does not redesign the offline engine.

Rationale: The spec keeps the current one-hour access lifetime and forbids rewriting the sign-in core. `UPDATE_LAST_LOGIN` is currently false, so the team field can stay empty forever even after a real login.

Alternatives considered: Revoking every already issued access credential immediately. Rejected because that is a new session design. Turning on `UPDATE_LAST_LOGIN` for refresh. Rejected because refresh is not a sign-in.

## Decision: New actions append to the existing base history

Invitation created, cancelled, and accepted; role changes; membership status changes; and account status changes call the existing `record_access_change`. Account status stores no project. The record holds the actor, person, time, and before/after difference. Passwords, reset tokens, and invitation tokens are not written there. The recent project read from A6-P2 stays. The finished history screen stays a later phase.

Rationale: A6-P2 already created the base record and told this phase to consume it.

Alternatives considered: A new audit table for invitations. Rejected because the later history phase would then have two sources.

## Decision: The team list is the current list plus search and labels

The member list stays one response for the project. The screen filters that response by name. Search does not create a person. The response adds the membership id and invitation delivery state. It does not replace a missing last sign-in with the join time or with the current time.

Rationale: Projects already load the whole team for this screen. A separate search service is unnecessary.

Alternatives considered: A new directory service. Rejected because user lookup already supports selection, and directory confidentiality across every module is a later phase.

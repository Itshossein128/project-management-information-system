# Research: A6-P1 access policy

## Decision: Organizational observation is read-only and named

Only a member of the Django group `admin` (system administrator) or a
`is_superuser` account may read general operational project information without
an active project membership. The staff flag and the `hr` group do not receive
that exception. The same accounts still need an active membership and the
matching project permission to create, edit, delete, or approve project
operations.

Rationale: This is the customer decision recorded on 2026-11-05 and copied into
constitution 1.1.0 and spec FR-007.

Alternatives considered: Keeping today's `_is_global_admin` write bypass would
let these accounts change every project. Treating staff or HR as the same
exception would contradict the decision. Removing the read exception would
contradict option A.

## Decision: Do not change `_is_global_admin` for every module in this phase

`permissions.project._is_global_admin` currently treats superuser and group
`admin` as holding every project permission, including writes. Callers include
project lifecycle, portfolio cash-flow, and `HasProjectPermission`. Rewriting
that helper now would enforce the new write rule across the product. That
widespread enforcement belongs to P4.

This phase adds a strict check that does not consult `_is_global_admin`, and
uses it only on the selected paths: project positions, direct callers of
`CanViewProjectMembers`, project member role changes, the legacy item catalog
write gate, and one activity edit/delete/approve example.

Rationale: The spec requires the full policy to be recorded and the selected
paths to be tested, while module-wide coverage stays in P4.

Alternatives considered: Changing `_is_global_admin` immediately is smaller in
code and larger in behavior. Leaving the selected position writes on
`HasProjectPermission` would still allow the write bypass.

## Decision: One installed authorization realm, no new organization tenant

Projects have no organization foreign key. `User.organization` and
`Stakeholder.organization_name` are free-text labels, not an authorization
boundary. This phase does not add a tenant table and does not compare those
strings.

The observation exception therefore applies inside the single authorization
realm of this installation. It must not be implemented as a cross-tenant grant,
because no second tenant exists to grant. A later phase that introduces an
organization owner for projects must narrow this exception to that owner before
more than one organization shares a database. Until then, tests use two
projects in the current realm and do not pretend a second organization was
isolated.

Rationale: Inventing a tenant would be a new data model outside A6-P1.
Matching on free text would both leak and hide projects through spelling.

Alternatives considered: Filtering projects by `User.organization` text.
Rejected as a false boundary.

## Decision: Position reads and the direct membership helper

`CanViewProjectMembers` currently allows any membership row, and also allows
staff, `hr`, and `business-setup`, without checking `status='active'`.
`ProjectPositionViewSet` safe methods use it. The alias
`CanViewBusinessAssignments` is also used by project-scoped inventory reads
(`SpaceMaterialRequestViewSet` and department-activity views). Those are direct
consumers and must pick up the same active-membership rule.

Safe access becomes: active project member, or organizational observation
(superuser or group `admin`). Staff, `hr`, and `business-setup` lose this
shortcut. Inactive, invited, suspended, and archived memberships do not count.
An observer who also has an inactive membership keeps the read, and still
cannot write.

Rationale: The reproduced defect is an inactive member reading positions. The
spec requires the same check on direct consumers of that helper.

Alternatives considered: Patching only the position view and leaving the helper
to its other callers. That would leave the defect one call away.

## Decision: Position and team writes use active membership only

Position writes today use `IsHrOrAdmin`, which accepts staff, superuser, group
`admin`, and group `hr`. Member create and update use `HasProjectPermission`
for `manage_members`, which still honors `_is_global_admin`.

Selected-path writes call a strict helper: active membership plus
`manage_members`. Group `admin` and superuser without that membership are
rejected. HR and staff without that membership are rejected. This does not
remove their existing ability to administer organization accounts and reference
data through `IsHrOrAdmin` on those other screens.

Rationale: Organization administration does not automatically include project
member, role, or permission management. Position maintenance on a project is
part of that selected team path.

Alternatives considered: Adding a new position permission code. `manage_members`
already exists and is the project-manager capability for team structure.
A second code would widen the catalog without a customer name for it.

## Decision: Unknown roles fail before any membership write

`assign_roles_to_member` filters missing role ids and, on update, deletes
current `ProjectMemberRole` rows first. Create saves the member before role
assignment, outside one transaction.

Replace that with one service that, inside `transaction.atomic`, rejects the
whole request when any id is missing. Create must not insert `ProjectMember`
when validation fails. Update must not delete existing roles when validation
fails. Empty role lists stay on the current create rule: at least one role is
required. Update may still omit `role_ids`.

The error uses the existing envelope
`{"error": {"code": "unknown_role", "message": "...", "details": {"role_ids": [...]}}}`.
The message is wrapped in `gettext` so Persian and English catalogs can render
it. The add-member drawer already shows the thrown error message.

Rationale: FR-001 and FR-002 require all-or-nothing behavior and a bilingual
message. A new membership table is unnecessary.

Alternatives considered: Accepting partial roles, or deleting roles and then
rolling back in the view without a transaction. Both can leave a gap if a later
line fails.

## Decision: Visitor write block stays on the existing read-only gate

`ItemViewSet` allows every authenticated user to write. Other inventory
viewsets already include `IsVisitorReadOnly`. Add that same class to
`ItemViewSet`, including import. Export remains a safe method. A project
viewer role is not an organization visitor; the global catalog must not treat
"viewer in some project" as the visitor group. Project-viewer write denial on
project resources is covered where those paths require `manage_members` or the
activity permissions below. Full writer coverage remains P4.

Rationale: The reproduced defect is the visitor group creating an item. The
catalog is organization reference data, not a project record.

Alternatives considered: A new item permission code. The customer asked to
close the existing read-only gap, not to redesign the catalog.

## Decision: One activity proves edit, delete, and approve are separate

`ActivityViewSet` uses `edit_activities` for create, update, and destroy.
Measurement approval already requires `approve_reports`.

Add the codename `delete_activities`. A data migration grants it to every role
that already has `edit_activities`, so current editors keep delete. Destroy
then requires `delete_activities` through the strict membership helper.
Approval stays on `approve_reports` at
`activities/<activity_id>/measurement/approve/`. The representative role has
`edit_activities` and lacks the other two. Default roles do not lose delete.

No schema migration is required: `RolePermission.permission_codename` is
already a string. Rollback of the data migration deletes only the rows this
migration inserted. Reverting the view code returns destroy to
`edit_activities`.

Rationale: The catalog has no general delete code. Granting delete to current
editors preserves behavior while letting one role refuse it. Applying this
split to every module is P4.

Alternatives considered: Overloading `edit_activities` with a request flag.
That would not be an independent permission.

## Decision: Sensitive fields are not part of position observation

Position payloads do not include wages, pay rates, or stakeholder contacts.
This phase does not retune wage or contact redaction. The policy row says
observation does not imply those permissions. Existing `view_wage` and
`view_sensitive_contacts` checks remain the independent gates, and P4 must
prove them for observers who are not members. This phase records that limit
instead of claiming those screens were retested.

Rationale: PM-09 says to test sensitive disclosure only when the selected path
contains that data.

Alternatives considered: Expanding this phase into HR wage and stakeholder
contact retests. That is the confidentiality work reserved for later.

## Decision: Tests assert the desired result on a disposable test database

Use pytest against the project's test database. Do not drop or recreate the
development database named in `.env`. Cover the negative and positive cases in
the same test module. Do not leave the new tests as expected failures.

Historical probe counts from 14 Aban 1405 are not evidence for the current
tree. Implementation must show the failing assertion on the current code before
the fix, then the passing assertion after it.

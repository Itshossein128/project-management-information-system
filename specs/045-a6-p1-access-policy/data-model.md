# Data model: A6-P1 access policy

No new table and no new column. The phase uses the existing membership, role,
and permission rows.

## Person account

Existing user account.

- `is_superuser`: when true, the account may read general operational project
  information without an active membership. It does not by itself grant
  selected-path writes.
- `is_staff`: staff marker. Alone, it grants neither the observation exception
  nor project access.
- Group `admin`: system-administrator group. Same observation exception as
  superuser. It is not implied by staff.
- Group `hr`: human resources. No project observation exception. Existing
  organization-account and reference-data screens keep their current explicit
  checks.
- Group `visitor`: organization visitor. Read-only on the legacy item catalog.
- Group `business-setup`: not an observation exception. It loses the shortcut
  inside `CanViewProjectMembers` only.

Validation: these flags are not synonyms. Tests create one account per flag.

## Project membership

Existing link between a person and one project.

- Status values remain the current set: `active`, `inactive`, `invited`,
  `suspended`, `archived`.
- Only `active` satisfies project access for a person who is not an observer.
- An inactive membership does not delete historical documents or the recorded
  author.
- Transition used by this phase: active to inactive removes position reads for
  an ordinary member and does not remove them for an observer.

## Access role

Existing global role catalog. Project-local roles are not added.

- A role id in a member create or role update must refer to an existing role.
- Unknown or mixed id lists are rejected before any membership or role row
  changes.
- Create still requires at least one role id. That current rule is unchanged.
- Update may omit role ids. When role ids are present, the full list must
  exist or the previous assignments stay.

## Job title (project position)

Existing `ProjectPosition`. `project` may be null for a shared title. This
phase does not add multiple titles per membership.

- Reading titles of a project requires an active membership or organizational
  observation.
- Creating, updating, or deleting a title on the project path requires an
  active membership and `manage_members`.

## Permission codename

Existing `RolePermission.permission_codename` string, maximum length 60.

- New allowed value: `delete_activities`.
- Roles that already have `edit_activities` also receive `delete_activities`
  through a data migration, so current editors can still delete.
- A role may have `edit_activities` without `delete_activities` and without
  `approve_reports`.
- `manage_members` remains the permission for the selected team and position
  writes.

## Activity

Existing project activity. No field changes.

- Update requires active membership and `edit_activities`.
- Delete requires active membership and `delete_activities`.
- Approving that activity's measurement basis requires active membership and
  `approve_reports`.

## Legacy item

Existing organization-wide item. It is not a project-private record.

- Visitors may read and may not create, update, delete, or import.
- An account that is allowed to write today, and is not only a visitor, still
  may write.

## State transitions

Membership status is not given a new state. The only transition this phase
relies on is active to inactive, which drops ordinary access and keeps history.

Role assignment is not a partial transition. The stored role set either stays
as it was or becomes exactly the validated submitted set.

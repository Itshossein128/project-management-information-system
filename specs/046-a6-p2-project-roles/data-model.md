# Data model: A6-P2

No second role catalog. Existing rows remain valid.

## Role

- `project`: empty for a global role, set for a local role. Existing rows stay empty.
- `role_name`: maximum length 60. Unique among global roles. Unique per project for local roles.
- A global built-in name cannot be used for a new local role.
- Deleting a role is refused while any assignment row exists.

## Role assignment

Existing link from a membership to a role.

- The role must be global or belong to the membership's project.
- Membership status may be `active`, `inactive`, `invited`, `suspended`, or `archived`. None of these statuses removes the assignment from the delete check.
- Deleting the role must not delete the assignment. The database protects the role while assignments remain.

## Job title

Existing title. `project` empty means usable by every project. `is_active` false hides it from new selection.

- A membership may select several titles.
- The previous single title is kept and filled from the first selected title so older readers still see one title.
- Existing single titles are copied into the selected set.
- A title may have zero or more default permission codes. Each code maximum length is 60 and must be a known permission.

## Permission result

For one membership and one permission code:

- Origin `grant` when an explicit allow exists.
- Origin `deny` when an explicit deny exists.
- Origin `inherit` otherwise.
- Effective allow is the explicit allow, or otherwise the union of role permissions and title defaults, unless an explicit deny exists.

## Base history

One record per change:

- Actor, project, subject person, time.
- Action name.
- Before and after values for the roles or permissions that changed.
- Deleting the role afterward does not delete the record.

## State transitions

- Custom role with assignments: delete is refused and assignments stay.
- Custom role with no assignments: the authorized actor may delete it.
- Built-in global role: delete and permission edits stay refused.
- Removing one assigned role leaves every other assigned role in place.

# Contract: A6-P2 roles, titles, and permission origin

Global custom roles stay on the existing organization role screen and are not project-local roles.

## Local roles

`GET /api/v1/projects/{project_id}/roles/`

Returns assignable roles: global roles plus local roles of that project. A local role of another project is absent.

`POST` creates a local role. The caller must be an active project member allowed to manage members. A global role is not created here.

`PATCH` and `DELETE` apply only to a local role of that same project.

`GET .../roles/{role_id}/impact/`

Returns `assignment_count` and per-project counts inside the caller's scope. Inactive and suspended memberships are included.

`DELETE` of a custom role with any assignment returns HTTP 409, code `role_in_use`, and the same count. No assignment row is removed.

`DELETE` after the last assignment was removed or replaced returns success for a custom role. A built-in role still returns a refusal.

A project member-management permission does not allow `DELETE /api/v1/roles/{id}/` for a global role.

## Members

Role ids on create and update must be global or local to that project.

`position_ids` selects several job titles. Unknown titles, inactive titles, and titles of another project are rejected. Omitted `position_ids` does not clear titles.

The permission list includes, for every code:

- `granted`: effective allow or deny
- `origin`: `inherit`, `grant`, or `deny`

Clearing an override removes the override. The following read shows `inherit`.

## Recent changes

`GET /api/v1/projects/{project_id}/access-changes/`

Returns the latest base records for that project: subject person, actor, time, action, and before/after difference. It is not the finished history screen.

## Errors

Messages are translated. A refused delete says the role is still assigned and was not deleted. A cross-project role says the role does not belong to this project.

## Forms

The organization role screen shows the assignment count before a permission replacement or delete. If the count is not zero, delete stays closed and explains that assignments must be removed first.

The project member screen can create a local role, choose several roles and several usable titles, and show inherit, grant, and deny from `origin`. After a refused delete or a saved change, the list matches the saved result.

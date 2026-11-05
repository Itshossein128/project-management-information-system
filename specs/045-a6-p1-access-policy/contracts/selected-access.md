# Contract: selected access paths for A6-P1

Paths below are the ones this phase changes. Other endpoints that still treat
a system administrator as a full project writer are unchanged until P4.
Authenticated callers send the existing session or token. Error bodies use the
current envelope.

```json
{
  "error": {
    "code": "unknown_role",
    "message": "One or more selected roles do not exist.",
    "details": {"role_ids": ["<missing-uuid>"]}
  }
}
```

The message is translated. Persian and English both state that the role does
not exist and that nothing was saved.

## Member roles

`POST /api/v1/projects/{project_id}/members/`

`PATCH /api/v1/projects/{project_id}/members/{user_id}/`

Caller must be an active member with `manage_members`. A system administrator
or superuser without that membership is refused. Staff and human resources
without that membership are refused.

Request field `role_ids` is a list of role ids. On create it is required and
non-empty. On update it is optional.

Success on create returns the member and the saved roles. Success on update
replaces the role set with the submitted ids.

Failure with an unknown id returns HTTP 400 and `unknown_role`. No membership
is created. On update, previous roles and individual permission overrides stay
unchanged. A list that mixes a real role and an unknown role has the same
failure.

## Project positions

`GET /api/v1/projects/{project_id}/positions/`

`GET /api/v1/projects/{project_id}/positions/{position_id}/`

Allowed for an active member, a system administrator, or a superuser. Refused
for an ordinary inactive member, a non-member, staff alone, and human resources
alone. An observer with an inactive membership may still read.

`POST`, `PATCH`, and `DELETE` on those paths require an active membership and
`manage_members`. Observation does not allow them. The response does not add
wage, rate, or confidential contact fields.

Direct read callers of the same membership helper, including project-scoped
space-material and department-activity lists, use the same active-membership
rule. Their write rules outside the position path are not redesigned here.

## Legacy items

`GET /api/items/` remains allowed for an organization visitor.

`POST`, `PATCH`, and `DELETE` on `/api/items/` and `POST /api/items/import/`
are refused for a visitor. An account that is not a visitor and can write items
today still receives success. This catalog is not project-private data.

## Activity separation

`PATCH /api/v1/projects/{project_id}/activities/{activity_id}/` requires
`edit_activities`.

`DELETE /api/v1/projects/{project_id}/activities/{activity_id}/` requires
`delete_activities`.

`POST /api/v1/projects/{project_id}/activities/{activity_id}/measurement/approve/`
requires `approve_reports`.

A member whose role has only `edit_activities` can update and cannot delete or
approve. Roles that already had `edit_activities` before this phase also have
`delete_activities` after the data migration.

## Form

The project member form submits the same member payload. A refused role shows
the server message and leaves the member list unchanged. Item and position
screens that already call these paths show the refusal and do not save a
partial record.

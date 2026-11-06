# Contract: A6-P4 uniform module access and confidentiality

Authenticated callers use the existing session or token. Error bodies keep the standard envelope `{error: {code, message, details}}`. Messages are translated (Persian and English).

## Project scope

Project list/detail and project-scoped resources refuse non-members and inactive members without the observation exception.

Organizational observation (superuser or group `admin`) may read general operational project information inside the allowed organization. It does not authorize create, update, delete, approve, wages, person contacts, stakeholder contacts, or confidential files.

Create/update/actions that accept related object ids reject ids belonging to another project. No inconsistent relation is stored. Code example: `project_scope_mismatch` or the existing validation code used by the path.

## User lookup for member assignment

`GET /api/v1/users/lookup/?q=`

Caller must be an active member with `manage_members` for the project context used by the team flow. Unauthenticated and non-managing callers are refused.

Minimum success fields:

```json
[
  {
    "user_id": "<uuid>",
    "full_name": "<display name>"
  }
]
```

Without person-contact permission, `email` and `mobile` are absent or null and must not appear populated. With person-contact permission, those fields may be included. An optional single non-sensitive organizational disambiguator may appear when needed for duplicate names.

Lookup may return assignable accounts in the allowed organization that are not yet project members. It is not the full organization directory.

## Project member roster

Member list/detail for an active project member may include name, roles, and positions. Mobile and email require person-contact permission. Server omits unauthorized fields.

## Organization directory

Full organization account directory remains on the account-administration paths only. Project manager, bare `hr` group, and `is_staff` alone are insufficient.

## Stakeholder vs person contacts

Stakeholder sensitive contacts stay behind `view_sensitive_contacts`.

Person/employee/user contacts stay behind the separate person-contact permission. Holding only `view_sensitive_contacts` does not reveal person contacts, and the reverse is also true.

## Wage and nested exports

Paths that expose wage or rate fields require `view_wage` to read and `edit_wage` to change. Nested report, dashboard, drill, and export payloads apply the same rule to nested keys. Observation does not reveal these fields.

## Files and signed links

Upload finalize, signed link issue, and download re-check source resource permission and current project authority. Generic project membership is not enough for a confidential source. After membership revocation, a previous link is refused or expired per current policy. Mocked signing alone is not delivery evidence for real file coverage.

## Final approval and SoD

Material final-approve paths, including commitment approval, call the shared SoD guard.

`assert_not_self_final_approve(created_by_id, actor, *, break_glass_reason=None)` returns
`SodDecision(allowed, used_break_glass, reason)` or raises `CodedValidationError`.
Codes: `sod_self_approve`, `sod_missing_creator`, `sod_actor_required`.

Self-approve without break-glass returns HTTP 400 with code `sod_self_approve`.

Break-glass is allowed only when all of the following hold:

- actor `is_superuser`
- actor is an active member of the project
- actor has the normal approve permission for that action
- record status is valid for approval
- request includes an explicit non-empty reason
- a durable access-history row is written with actor, project, record, timestamp, reason, exception flag, and before/after

Group `admin`, staff, and HR do not receive break-glass. Superuser alone is not enough.

Request shape for break-glass (field name may be adapted consistently):

```json
{
  "break_glass_reason": "non-empty reason text"
}
```

For unknown legacy creator:

```json
{
  "break_glass_reason": "unknown_creator"
}
```

Null creator on the normal path is refused. Approvers must not rewrite `created_by` to themselves to bypass the guard.

## UI contract

Hidden forbidden actions remain forbidden on direct API calls. Observation-capable accounts are not falsely blocked from allowed reads in the UI, and are not shown effective write controls the server will refuse.

## Package matrix

Each internal package delivers a filled operation matrix for its module areas with positive and negative results on two projects, or N/A with reason. Alternate/legacy paths appear as their own rows when they exist.

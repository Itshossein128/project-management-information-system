# Contract: Project Capability Settings

**Feature**: `002-core-domain-principles`  
**Base path**: `/api/v1/projects/{project_id}/capabilities/`

## Endpoints

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `.../capabilities/` | `view_project` | List settings for project (seed missing keys as enabled/optional defaults) |
| PUT/PATCH | `.../capabilities/{capability_key}/` | `edit_project` (or admin-equivalent) | Update `enabled` / `mode` |

## Resource schema

```json
{
  "capability_key": "risk",
  "enabled": false,
  "mode": "disabled",
  "updated_at": "2026-10-07T12:00:00Z",
  "updated_by": "uuid"
}
```

## Behavior when disabled

- Navigation/UI hides create entry points for the capability.
- `POST`/`PATCH`/`DELETE` on that capability’s domain APIs → `403` or `409` with `code: capability_disabled`.
- `GET` list/detail of existing records → still allowed if user has read permission.

## Errors

| Code | HTTP | When |
|------|------|------|
| `capability_disabled` | 403/409 | Mutate while disabled |
| `unknown_capability_key` | 400 | Key not in catalog |

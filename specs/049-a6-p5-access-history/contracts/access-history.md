# Contract: access history

Extends the existing project list. Does not replace `AuditLog`.

## Project history

`GET /api/v1/projects/{project_id}/access-changes/`

Query parameters, all optional:

| Name | Meaning |
| --- | --- |
| subject | Subject user id |
| actor | Actor user id |
| since | Inclusive start, ISO date or datetime |
| until | Inclusive end, ISO date or datetime |
| page | Page number, default 1 |
| page_size | Default 50, maximum 100 |

The caller must be an active project member with `manage_members`, or an organizational administrator / superuser allowed to observe that organization. Otherwise the response is 403. A project the caller cannot see is 404. Rows from another project are not included.

Response:

```json
{
  "count": 1,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "id": "uuid",
      "action": "override_set",
      "origin": "exception",
      "role_name": "",
      "actor_name": "Admin",
      "subject_name": "سارا آزمون",
      "project_id": "uuid",
      "before": {},
      "after": {"permission": "edit_costs", "effect": "deny"},
      "unknown": [],
      "created_at": "2026-11-06T12:24:00+00:00"
    }
  ]
}
```

`origin` is `role`, `exception`, `membership`, `account`, or `event`, derived from `action`. `unknown` lists required fields that have no stored value. Secret values are the redacted marker, never the original.

The current unpaginated array is replaced by this object. The project members screen reads `results`.

## Organization history

`GET /api/v1/access-changes/`

Same filters, plus optional `project`. Restricted to the `admin` group and superuser, inside their organization. Global role changes and successful logins appear here with a null project. A project manager without that organizational right receives 403.

## Errors

Persian and English messages follow the active language. Codes:

| Situation | Status | Code |
| --- | --- | --- |
| No history permission | 403 | forbidden |
| Project not visible | 404 | not_found |
| Sensitive access change whose trail could not be stored | 503 | audit_unavailable |

No create, update, or delete endpoint exists for these rows.

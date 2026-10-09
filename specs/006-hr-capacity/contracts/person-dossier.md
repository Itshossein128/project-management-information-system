# Contract: Person dossier

**Base (preferred)**: `/api/v1/users/{user_id}/dossier/`  
**Alt (project people context)**: `/api/v1/projects/{project_id}/people/{user_id}/dossier/`

Project-scoped alt MUST verify the target user is a project member (or allocated) before read; write still requires HR edit permission.

## Permissions

- Read: authenticated + (`view_hr` **or** self-read of non-sensitive fields)
- Write: `edit_hr` (not self-escalation of skills-only unless product later allows)
- Sensitive wage/rates: never on this contract; see [wage-acl-and-cost-estimate.md](./wage-acl-and-cost-estimate.md)

## GET dossier

Returns:

```json
{
  "id": "uuid",
  "full_name": "string",
  "email": "string",
  "mobile": "string",
  "status": "active",
  "is_active": true,
  "organization": "string",
  "skills": ["welding"],
  "qualifications": ["ISO 9606"],
  "org_unit_id": "uuid|null",
  "org_unit_name": "string|null",
  "supervisor_id": "uuid|null",
  "supervisor_name": "string|null",
  "default_capacity_percent": "100.00"
}
```

## PATCH dossier

```json
{
  "skills": ["welding", "fit-up"],
  "qualifications": ["ISO 9606"],
  "org_unit_id": "uuid",
  "supervisor_id": "uuid",
  "status": "active",
  "default_capacity_percent": "100.00"
}
```

**200** updated. Reject inactive/suspended transition only via authorized HR edit.

## Errors

| Code | When |
|------|------|
| `permission_denied` | Missing `edit_hr` / `view_hr` |
| `validation_error` | Invalid supervisor (self-loop optional reject) or unknown org unit |
| `not_found` | User not visible in scope |

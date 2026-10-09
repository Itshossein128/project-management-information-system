# Contract: Organization, Stakeholder, References

**Feature**: `003-central-data-model`

## Organization units (org-wide)

Base: `/api/v1/organization-units/`

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/` | authenticated staff **or** users with global manage-refs; read open to authenticated project creators |
| PATCH | `/{id}/` | same as write |

```json
{
  "code": "OPS",
  "name": "Operations",
  "parent": null,
  "status": "active"
}
```

## Project owning unit

`PATCH /api/v1/projects/{id}/` accepts `owning_unit` UUID.

## Stakeholders (project-scoped)

Base: `/api/v1/projects/{project_id}/stakeholders/`

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/` | `view_project` / `edit_project` |
| PATCH/DELETE | `/{id}/` | `edit_project` (soft-delete) |

```json
{
  "name": "Client Rep",
  "organization_name": "Employer Co",
  "role": "کارفرما",
  "email": "a@b.c",
  "phone": "",
  "influence": 5,
  "interest": 4,
  "communication_need": "Weekly status",
  "status": "active"
}
```

## Contract types (org-wide)

Base: `/api/v1/contract-types/`

CRUD for `{ code, name_fa, name_en, is_active }`. Contract create accepts `contract_type_ref` UUID (preferred) while legacy string `contract_type` remains readable.

## Units

Existing `/api/...` unit endpoints remain; no free-text-only mandatory unit on new surfaces in this feature.

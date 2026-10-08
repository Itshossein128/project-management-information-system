# Contract: Project lifecycle

**Base**: `/api/v1/projects/`

## Permissions

| Action | Permission |
|--------|------------|
| Create | Authenticated (existing) |
| List / retrieve | Project member (existing) |
| Patch non-status / non-protected (or draft protected) | `edit_project` |
| Submit / reject-to-draft / suspend / resume / complete / archive | `edit_project` (archive also allows system admin) |
| Approve → active | `approve_project` |

## Create

`POST /api/v1/projects/`

Body (extends existing):

```json
{
  "project_code": "PRJ-001",
  "project_name": "Tower A",
  "purpose": "…",
  "scope_description": "…",
  "main_deliverables": "…",
  "employer": "…",
  "project_manager": "<uuid|null>",
  "start_date": "2026-01-01",
  "planned_finish_date": "2027-01-01",
  "contract_type": "lump_sum",
  "contract_number": "C-12",
  "contract_amount": "1000000.00",
  "currency": "IRR",
  "location": "…",
  "owning_unit": "<uuid|null>"
}
```

**Effects**: `status=draft`; `budget_approved_at=null`  
**201** with detail payload including new fields  
**400** duplicate `project_code`

## Detail / list

`GET /api/v1/projects/` — support `?status=` filter  
`GET /api/v1/projects/{project_id}/` — include lifecycle fields + `budget_approved_at` / `_by`

## Status actions

All `POST /api/v1/projects/{project_id}/…/`

| Path | From | To | Notes |
|------|------|-----|-------|
| `submit/` | draft | pending_approval | `edit_project` |
| `approve/` | pending_approval | active | `approve_project`; runs activation gates; sets `budget_approved_at` if amount set and stamp null |
| `reject/` | pending_approval | draft | body optional `{ "reason": "…" }` |
| `suspend/` | active | suspended | |
| `resume/` | suspended | active | gates still must hold |
| `complete/` | active\|suspended | completed | |
| `archive/` | completed\|active\|suspended | archived | non-admin cannot later mutate |

**400** `activation_gates_failed` with `{ "missing": ["project_manager", "scope_description", "budget_approved"] }`  
**400** `invalid_status_transition`  
**403** missing permission

## Patch rules

`PATCH /api/v1/projects/{project_id}/`

- Must **not** accept arbitrary `status` bypassing actions (reject or ignore with error).
- If `status` in `active|suspended|completed|archived` and body contains protected keys → **400** `protected_field_requires_change_request`.
- If `status == archived` and actor not system admin → **403** `project_archived`.

## Errors

| Code | When |
|------|------|
| `duplicate_project_code` | Unique violation |
| `activation_gates_failed` | Approve/resume without PM/scope/budget |
| `invalid_status_transition` | Illegal edge |
| `protected_field_requires_change_request` | Direct protected PATCH |
| `project_archived` | Mutate archived without admin |

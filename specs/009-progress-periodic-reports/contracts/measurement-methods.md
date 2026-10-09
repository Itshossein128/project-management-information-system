# Contract: Activity measurement methods

**Base**: `/api/v1/projects/{project_id}/activities/{activity_id}/measurement/`

## Permissions

- Read: `view_activities` or `view_dashboard`
- Draft / submit change: `edit_activities`
- Approve: `approve_reports` (fallback `edit_activities` if project lacks approve_reports — document in ENDPOINTS)

## GET current definition

Returns current method, status, basis fields, `current_version_id`, version list summary.

## PUT / PATCH draft basis

```json
{
  "method": "quantity",
  "total_quantity": 1000,
  "unit_id": "<uuid>",
  "milestones": [],
  "evidence_rules": ""
}
```

Weighted example:

```json
{
  "method": "weighted_milestones",
  "milestones": [
    { "name": "Formwork", "weight": 0.3 },
    { "name": "Pour", "weight": 0.5 },
    { "name": "Cure", "weight": 0.2 }
  ]
}
```

## POST `…/measurement/approve/`

Approves current draft basis → creates `ActivityMeasurementVersion`. Body optional `{ "reason": "…" }` (required if not first version).

## POST `…/measurement/change/`

Starts a new draft change from approved state without rewriting history. Body includes new method/basis + `reason` (required).

## Errors

| Code | HTTP | When |
|------|------|------|
| `incomplete_measurement_basis` | 400 | Approve with missing total/unit or bad milestone weights |
| `method_change_reason_required` | 400 | Non-first approve/change without reason |
| `measurement_already_approved` | 409 | Approve when nothing pending |

## Quantity change (exception for >100%)

`/api/v1/projects/{project_id}/activities/{activity_id}/quantity-changes/`

- Create draft `{ previous_total, new_total, reason }`
- `POST …/{id}/approve/`
- Progress APIs accept linkage to approved change when validating >100% of prior total

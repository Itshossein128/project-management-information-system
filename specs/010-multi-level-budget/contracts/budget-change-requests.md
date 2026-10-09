# Contract: Budget change requests

**Base**: `/api/v1/projects/{project_id}/budget-change-requests/`

## Permissions

| Action | Permission |
|--------|------------|
| List / retrieve | `view_costs` |
| Create / update draft / submit / cancel | `edit_costs` |
| Approve / reject | `approve_costs` |

## Create

`POST …/budget-change-requests/`

```json
{
  "reason": "Scope change for foundation package (min 10 chars)",
  "amount_delta": "50000000.00",
  "project_impact": "Extends foundation scope; schedule impact tracked separately",
  "affected_lines": [
    {
      "op": "update",
      "line_id": "<uuid>",
      "budget_amount": "150000000.00"
    },
    {
      "op": "create",
      "level": "wbs",
      "wbs": "<uuid>",
      "cost_category": "material",
      "budget_amount": "50000000.00"
    }
  ]
}
```

Preconditions: project has a control approved version; no other open CR (`draft`/`submitted`).

**201** `status=draft`  
**409** `change_request_already_open`  
**400** `reason_required` / `project_impact_required` / `no_control_budget`

## Lifecycle

| Method | Path | Effect |
|--------|------|--------|
| PATCH | `…/{id}/` | Update fields while draft |
| POST | `…/{id}/submit/` | draft → submitted |
| POST | `…/{id}/approve/` | Clone control → new `revised` version with affected_lines applied; set control; CR approved |
| POST | `…/{id}/reject/` | → rejected; budget unchanged |
| POST | `…/{id}/cancel/` | draft/submitted → cancelled |

## Interaction with direct edits

Direct PATCH/bulk on control version lines → **400** `budget_version_locked` (must use CR when net change or structural change; transfers use transfer endpoint).

# Contract: Budget lines (version-scoped)

**Base**: `/api/v1/projects/{project_id}/budget-versions/{version_id}/lines/`  
Also: existing `/budgets/` and `/budgets/bulk/` become version-aware.

## Permissions

| Action | Permission |
|--------|------------|
| List | `view_costs` |
| Create / update / delete / bulk | `edit_costs` and version `status=draft` only |

## Line payload

```json
{
  "level": "wbs",
  "wbs": "<uuid>",
  "activity": null,
  "cbs": "<uuid|null>",
  "contract": null,
  "cost_category": "labor",
  "budget_amount": "1000000.00",
  "period_start": null,
  "period_end": null,
  "notes": ""
}
```

### Level rules

| level | Required |
|-------|----------|
| project | none of wbs/activity/contract (optional cbs) |
| phase | wbs |
| contract | contract |
| wbs | wbs |
| cbs | cbs |
| activity | activity (wbs inferred) |

## Bulk upsert

`POST …/budgets/bulk/` with optional `version_id` (default: current draft working version, else create draft initial).  
If target version is not draft → **400** `budget_version_locked`.

## Errors

| Code | When |
|------|------|
| `budget_version_locked` | Mutate non-draft |
| `invalid_budget_level` | FK/level mismatch |
| `project_ceiling_exceeded` | Would exceed control ceiling (on allocate/transfer paths) |

# Contract: Remaining allocatable & transfers

## Remaining

`GET /api/v1/projects/{project_id}/budgets/remaining/?version_id=`

Default version = current control. Permission: `view_costs`.

Response:

```json
{
  "version_id": "<uuid>",
  "project_ceiling": 1000000000.0,
  "headings": [
    {
      "key": "cbs:<uuid>|labor",
      "level": "cbs",
      "wbs": null,
      "cbs": "<uuid>",
      "cost_category": "labor",
      "approved": 100000.0,
      "committed": 40000.0,
      "consumed": 25000.0,
      "remaining": 35000.0,
      "overrun": false,
      "cbs_missing_warning": false
    }
  ]
}
```

`cbs_missing_warning`: true when heading is used for commitment/cost without CBS (informational).

## Transfer

`POST /api/v1/projects/{project_id}/budgets/transfers/`

Permission: `edit_costs`.

```json
{
  "from_line_id": "<uuid>",
  "to_line_id": "<uuid>",
  "amount": "10000.00",
  "note": "Rebalance materials"
}
```

Rules:
- Both lines on same control approved version
- `amount` &gt; 0 and ≤ from_line.budget_amount
- After transfer, project total unchanged; neither line negative
- Target/source levels must be in allowed set: `project|phase|contract|wbs|cbs|activity` (all v1 levels allowed if same project)
- If transfer would somehow raise project total above ceiling → **400** `project_ceiling_exceeded`

**201** returns transfer record + updated lines.

## Errors

| Code | When |
|------|------|
| `project_ceiling_exceeded` | Would exceed control total |
| `transfer_insufficient_source` | amount &gt; source |
| `transfer_version_mismatch` | Lines not on same control version |
| `budget_version_locked` | Version not approved control |

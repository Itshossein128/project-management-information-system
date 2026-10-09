# Contract: Portfolio Cash / Need / Allocation Report

## API

`GET /api/v1/cash-flow/portfolio/report/`

Query: `from`, `to`, optional `cycle_id`.

### Response

```json
{
  "projects": [
    {
      "project_id": "<uuid>",
      "project_name": "Acme",
      "projected_inflow": 1200000,
      "projected_outflow": 800000,
      "net_need": 400000,
      "suggested_net_need": 400000,
      "composite": 67.5,
      "inflow_status": "registered"
    }
  ],
  "allocations": [
    {
      "cycle_id": "<uuid>",
      "decision_id": "<uuid>",
      "project_id": "<uuid>",
      "amount": 2000000,
      "owner_id": "<uuid>",
      "rationale": "..."
    }
  ],
  "totals": {
    "projected_inflow": 0,
    "projected_outflow": 0,
    "net_need": 0,
    "allocated": 0
  }
}
```

Only projects where the caller is an active member with `view_cashflow`.

## UI

Portfolio liquidity report table + link into project cash-flow projection.

## Test anchor

Two member projects with projection data + one decision → both appear in `projects`; decision in `allocations`.

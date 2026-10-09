# Contract: Net Cash Need

## Monthly net (from projection)

Included in projection response as `net_need` per month (= projected_inflow − projected_outflow).

## Suggested net need (FR-CASH-004)

`GET /api/v1/projects/{project_id}/cash-flow/suggested-need/`

Query: `from`, `to` (dates or YYYY-MM).

```json
{
  "period_start": "2026-10-01",
  "period_end": "2026-10-31",
  "due_commitments": 800000,
  "essential_costs": 0,
  "certain_planned_receipts": 1200000,
  "suggested_net_need": -400000,
  "meta": {
    "essential_costs_rule": "approved_actuals_in_categories_or_zero",
    "certain_planned_receipts_rule": "approved_ipc_remaining_due_in_period"
  }
}
```

Formula: `suggested_net_need = due_commitments + essential_costs − certain_planned_receipts`.

## UI

Net-need summary card on project cash-flow (monthly chart + suggested need for selected period).

## Test anchor

due_commitments=800k, receipts=1.2M, essential=0 → suggested_net_need=−400k.

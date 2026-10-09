# Contract: Projected Cash Series

## API

`GET /api/v1/projects/{project_id}/cash-flow/projection/`

Query: `from=YYYY-MM`, `to=YYYY-MM` (inclusive months).

### Response

```json
{
  "series": "projected",
  "months": [
    {
      "month": "2026-10-01",
      "projected_inflow": 1200000,
      "projected_outflow": 800000,
      "net_need": 400000,
      "inflow_status": "registered",
      "outflow_status": "registered"
    }
  ],
  "actual_months": [
    {
      "month": "2026-09-01",
      "actual_inflow": 500000,
      "actual_outflow": 450000,
      "net": 50000
    }
  ],
  "manual_forecast_months": [],
  "meta": {
    "inflow_sources": "approved_ipc_remaining_by_planned_payment_date",
    "outflow_sources": "approved_commitment_open_by_due_date"
  }
}
```

- `inflow_status`: `registered` \| `unregistered` (no IPC dues in range).
- Actual and projected arrays MUST remain separate keys (never merged).

Optional: `GET .../cash-flow/projection/details/?month=2026-10` for source lines.

## UI

Project cash-flow page: **Projection** panel showing monthly projected in/out/net beside existing actual/forecast tabs; empty inflow shows “no scheduled receipts” not `0` as success.

## Test anchor

IPC due month M with remaining R + commitment due M open O → month M projected_inflow=R, projected_outflow=O, net_need=R−O.

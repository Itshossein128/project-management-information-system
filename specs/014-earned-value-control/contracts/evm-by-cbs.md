# Contract: EVM by CBS

## API

`GET /api/v1/projects/{project_id}/progress/evm/by-cbs/`

Query: `as_of`, `force_refresh` (optional), `root_id` (optional CBS node to limit subtree).

Permission: `view_dashboard`.

### Response

```json
{
  "as_of_date": "2026-10-09",
  "validity": "valid",
  "warnings": [],
  "nodes": [
    {
      "cbs_id": "<uuid>",
      "cbs_code": "C-100",
      "cbs_name": "Concrete",
      "depth": 1,
      "bac": 300000,
      "pv": {"amount": 100000, "status": "registered"},
      "ev": {"amount": 90000, "status": "registered"},
      "ac": {"amount": 95000, "status": "registered"},
      "spi": {"value": 0.9, "status": "computable"},
      "cpi": {"value": 0.947, "status": "computable"},
      "eac": {"value": 316790, "status": "computable"},
      "etc": {"value": 221790, "status": "computable"},
      "vac": {"value": -16790, "status": "computable"},
      "children_roll_up": true
    }
  ],
  "project_totals": {
    "bac": 1000000,
    "note": "Same shape as project EVM measures; see evm-report.md"
  },
  "meta": {
    "ev_mapping": "activities_via_cbs_budget_lines",
    "ac_mapping": "actual_cost.cbs"
  }
}
```

### Rules

- Parent node amounts are either stored-at-node or sum of children—API `meta` MUST state which; v1 prefers **sum of direct budget/cost on node + optional explicit children_roll_up flag**.
- Node with BAC but no approved progress → `ev.status=unregistered`.
- Node with AC but no EV → CPI `not_computable`.
- Multi-currency under one node → block aggregate amounts for that node.

## UI

Progress page: **By cost center** table (CBS code/name + measures); bilingual headers.

## Test anchor

CBS node with budget line + ActualCost.cbs + activity budget on same CBS with approved progress → EV and AC both registered; CPI computable.

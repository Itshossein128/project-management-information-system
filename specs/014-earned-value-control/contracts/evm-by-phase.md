# Contract: EVM by Phase

## API

`GET /api/v1/projects/{project_id}/progress/evm/by-phase/`

Query: `as_of`, `force_refresh` (optional).

Permission: `view_dashboard`.

### Response

```json
{
  "as_of_date": "2026-10-09",
  "validity": "valid",
  "warnings": [],
  "phases": [
    {
      "wbs_id": "<uuid>",
      "wbs_code": "1.0",
      "wbs_name": "Phase A",
      "bac": 500000,
      "pv": {"amount": 200000, "status": "registered"},
      "ev": {"amount": 180000, "status": "registered"},
      "ac": {"amount": 210000, "status": "registered"},
      "spi": {"value": 0.9, "status": "computable"},
      "cpi": {"value": 0.857, "status": "computable"},
      "eac": {"value": 583430, "status": "computable"},
      "etc": {"value": 373430, "status": "computable"},
      "vac": {"value": -83430, "status": "computable"},
      "roll_up": "included"
    }
  ],
  "project_totals": {
    "bac": 1000000,
    "note": "Same shape as project EVM measures; see evm-report.md"
  },
  "meta": {
    "phase_basis": "wbs_phase_budget_or_subtree",
    "ac_allocation": "direct_only"
  }
}
```

### Rules

- Empty phase (no budget/progress/cost) → measures `unregistered` / indices `not_computable`, not SPI/CPI = 1.0.
- `roll_up=partial` on a phase when its BAC is outside the control version partition.
- Mixed currency within a phase → that phase `aggregation=blocked` (or omit amounts) with warning; see FR-010.

## UI

Progress page: **By phase** table under KPI grid; click-through optional to WBS filter.

## Test anchor

Two phase WBS nodes with partitioned BAC and approved progress → each phase has EV; project totals match global compute when partition complete.

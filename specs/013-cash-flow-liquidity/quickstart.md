# Quickstart: Cash Flow & Liquidity Allocation Gap Closure

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB; seed or fixtures with ≥2 projects, approved IPC with `planned_payment_date`, approved commitment with `due_date`
- Features 011 / 012 behaviors available for feeds

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  cash_flow/tests/test_projection_series.py \
  cash_flow/tests/test_net_need.py \
  cash_flow/tests/test_allocation_proposal_decision.py \
  cash_flow/tests/test_double_allocation_warn.py \
  cash_flow/tests/test_portfolio_cash_report.py \
  cash_flow/tests/test_cashflow_api.py \
  -q
```

## Manual API smoke

1. `GET .../projects/{id}/cash-flow/projection/?from=YYYY-MM&to=YYYY-MM` — projected in/out/net; actual separate.
2. `GET .../cash-flow/suggested-need/` — FR-004 formula fields.
3. `PUT .../priority-score/` on two projects → `POST .../portfolio/cycles/` → `propose/` → ordered lines.
4. `POST .../decisions/` without rationale → 400; with owner+rationale → 201.
5. Second overlapping decision without ack → `overlapping_allocation`; with ack → 201.
6. `GET .../portfolio/report/` — projects + allocations.

## UI

- Project → Cash flow: Projection + net-need panels (fa/en).
- Portfolio liquidity: cycle, proposal, decision, simulation compare.

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 | Projection shows due IPC + commitment month in &lt; 2 min |
| SC-002 | Portfolio report returns without spreadsheet export |
| SC-003 | Decision missing owner/rationale rejected |
| SC-004 | Overlap warned/blocked without ack |
| SC-005 | Zero pool → empty proposal + clear message |

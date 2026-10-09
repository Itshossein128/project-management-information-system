# Cash Flow Endpoints

Project-scoped routes live under `/api/v1/projects/{project_id}/` via `cash_flow/urls.py`.
Portfolio routes are registered globally under `/api/v1/cash-flow/portfolio/`.

## Cash Flow Transactions

| Endpoint | Method | Action | Description |
| :--- | :--- | :--- | :--- |
| `cash-flow/` | GET | list | Lists cash transactions with summary. |
| `cash-flow/transactions/` | POST | create | Creates a cash transaction. |
| `cash-flow/transactions/<uuid:pk>/` | PATCH | partial_update | Updates a transaction. |
| `cash-flow/transactions/<uuid:pk>/` | DELETE | destroy | Soft-deletes a transaction. |

## Reports & Forecasts

| Endpoint | Method | Permission | Description |
| :--- | :--- | :--- | :--- |
| `cash-flow/monthly/` | GET | `view_cashflow` | Monthly actual summary. |
| `cash-flow/forecast/` | GET | `view_cashflow` | Manual forecast vs actuals. |
| `cash-flow/forecast/<str:month>/` | PUT | `edit_cashflow` | Upsert manual forecast (`YYYY-MM`). |
| `cash-flow/gap-analysis/` | GET | `view_cashflow` | Gap analysis from manual forecasts. |
| `cash-flow/receivables/` | GET | `view_cashflow` | Receivables/payables summary. |

## Projection & Net Need (FR-CASH-001–004)

| Endpoint | Method | Permission | Description |
| :--- | :--- | :--- | :--- |
| `cash-flow/projection/` | GET | `view_cashflow` | Domain-fed projected series (`from`/`to` = `YYYY-MM`). Keys: `months`, `actual_months`, `manual_forecast_months` (never merged). |
| `cash-flow/suggested-need/` | GET | `view_cashflow` | FR-004 formula: due commitments + essential costs − certain planned receipts. |
| `cash-flow/priority-score/` | GET | `view_cashflow` | Current priority score + composite. |
| `cash-flow/priority-score/` | PUT | `edit_cashflow` | Upsert urgency/return_score/recovery_speed/risk (0–100). |

## Portfolio Liquidity (FR-CASH-005–009)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/cash-flow/portfolio/cycles/` | GET/POST | List/create allocation cycles (`available_liquidity`, period, currency). |
| `/api/v1/cash-flow/portfolio/cycles/{id}/propose/` | POST | Greedy proposal by composite; empty + `no_available_liquidity` when pool is 0; incomplete scores in `warnings`. |
| `/api/v1/cash-flow/portfolio/cycles/{id}/decisions/` | POST | Record decision (`owner_id` + `rationale` required). Overlap without `acknowledge_overlap` → `overlapping_allocation`. |
| `/api/v1/cash-flow/portfolio/cycles/{id}/simulations/` | POST | Save simulation payload `{name, lines}`. |
| `/api/v1/cash-flow/portfolio/cycles/{id}/simulations/{sim_id}/compare/` | GET | Diff simulation vs latest proposal. |
| `/api/v1/cash-flow/portfolio/report/` | GET | Membership-filtered projects + allocations (`from`, `to`, optional `cycle_id`). |

Visibility for portfolio APIs uses active membership + `view_cashflow` (`projects_visible_for_cashflow`).

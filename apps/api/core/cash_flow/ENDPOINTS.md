# Cash Flow Endpoints

This document outlines the API endpoints defined in the Cash Flow application (`apps/api/core/cash_flow/urls.py`). These endpoints manage cash transactions, monthly summaries, forecasting, gap analysis, and receivables/payables.

## Cash Flow Transactions

| Endpoint | Method | Action | Description |
| :--- | :--- | :--- | :--- |
| `cash-flow/` | GET | list | Lists cash transactions (inflows/outflows) with filtering options (by date, type, category, forecast flag, counterparty). Includes a summarized block of totals (total inflow/outflow, net balance, category breakdown). |
| `cash-flow/transactions/` | POST | create | Creates a new cash transaction. Validates and assigns project and user references. Automatically invalidates project cashflow caches upon creation. |
| `cash-flow/transactions/<uuid:pk>/` | PATCH | partial_update | Partially updates a cash transaction. Invalidates caches upon update. |
| `cash-flow/transactions/<uuid:pk>/` | DELETE | destroy | Deletes a cash transaction. Invalidates caches upon deletion. |

## Cash Flow Reports & Forecasts

| Endpoint | Method | Action | Description |
| :--- | :--- | :--- | :--- |
| `cash-flow/monthly/` | GET | monthly | Returns an aggregated monthly cash flow summary with cumulative balances. Results are cached and invalidated when transactions are modified. |
| `cash-flow/forecast/` | GET | list | Provides a list of monthly cash flow forecasts enriched with actual figures from the past for variance comparison. |
| `cash-flow/forecast/<str:month>/` | PUT | upsert | Inserts or updates the expected monthly forecast (expected inflows/outflows, confidence percentage) for a given month (`YYYY-MM`). |
| `cash-flow/gap-analysis/` | GET | gap_analysis | Identifies months with projected cash deficits and cumulative negative balances based on the current forecasts. |
| `cash-flow/receivables/` | GET | receivables | Returns an aggregated summary of expected receivables and payables derived from approved, unpaid IPCs (Interim Payment Certificates) in the contracts module. |

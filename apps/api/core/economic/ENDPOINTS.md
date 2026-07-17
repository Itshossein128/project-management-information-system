# Economic Engine Endpoints

Inflation-adjusted P&L snapshots, financing-cost analysis, and Monte Carlo scenario simulation. Snapshots aggregate paid main-contract IPC revenue, actual costs, inflation-adjusted costs, and financing delay costs.

Project routes: `/api/v1/projects/{project_pk}/economic/...`  
Global admin route: `/api/v1/inflation-indices/{name}/{index_date}/`

## Permissions

All project endpoints require `view_dashboard` + `IsProjectMember`. Inflation index upsert requires staff/superuser.

## Endpoints

### 1. P&L Snapshot

*   **URL:** `/economic/snapshot/`
*   **Method:** `GET`
*   **Description:** Returns the economic snapshot for `snapshot_date`. If none exists, generates one on demand via `generate_snapshot()`.
*   **Query:** `as_of` — optional Jalali (`1403/04/15`) or Gregorian (`2024-07-05`) date; defaults to today.
*   **Response:** Snapshot fields plus `inflation_detail` (per-category inflation breakdown).

**Profit layers:**

| Field | Formula |
|-------|---------|
| `accounting_profit` | `revenue_to_date - actual_cost` |
| `real_profit` | `revenue_to_date - inflation_adj_cost` |
| `economic_profit` | `revenue_to_date - actual_cost - financing_cost` |

### 2. Snapshot History

*   **URL:** `/economic/history/`
*   **Method:** `GET`
*   **Description:** All snapshots for the project ordered by `snapshot_date`.

### 3. Financing Cost

*   **URL:** `/economic/financing-cost/`
*   **Method:** `GET`
*   **Description:** Payment-delay analysis and total financing cost (from approved/paid IPC timing vs planned dates).

### 4. Inflation Indices (read)

*   **URL:** `/economic/inflation-indices/`
*   **Method:** `GET`
*   **Description:** Latest value per registered `index_name`.

### 5. Monte Carlo Simulation

*   **URL:** `/economic/simulate/`
*   **Method:** `POST`
*   **Body:** `{ "iterations": 5000, "scenario_params": { ... } }` (both optional)
*   **Response:** `202 Accepted` with `{ "task_id": "..." }`. Runs `run_monte_carlo_task` via Celery.

*   **URL:** `/economic/simulate/status/{task_id}/`
*   **Method:** `GET`
*   **Description:** Poll task status; returns `{ "status": "done", "result": ... }` when complete.

*   **URL:** `/economic/simulate/latest/`
*   **Method:** `GET`
*   **Description:** Most recent `SimulationResult` (P10/P50/P90 profit, prob of loss, sensitivity JSON).

### 6. Inflation Index Upsert (admin)

*   **URL:** `/api/v1/inflation-indices/{name}/{index_date}/`
*   **Method:** `PUT`
*   **Body:** `{ "index_value": 100, "source": "..." }`
*   **Permissions:** Staff or superuser only.
*   **Note:** `index_date` accepts Jalali or Gregorian strings.

## Background tasks

```bash
economic.tasks.generate_daily_snapshots   # nightly P&L for all active projects
economic.tasks.run_monte_carlo_task       # on-demand simulation
```

## Local dev without Celery worker

Set `CELERY_TASK_ALWAYS_EAGER=true` in `.env` so Monte Carlo runs inline. Snapshots still generate synchronously on first `GET /economic/snapshot/`.

## Data dependencies

- **Revenue:** paid IPCs on main contracts (`ContractType.MAIN`)
- **Costs:** `cost_control.ActualCost` ledger
- **Inflation:** `InflationIndex` + optional `CostCategoryInflationMapping` per project
- **Financing:** IPC planned vs actual payment dates

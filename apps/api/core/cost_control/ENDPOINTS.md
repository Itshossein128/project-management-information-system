# Cost Control Endpoints

Budget ingestion, actual cost ledger, variance engine, cost pools, and supplier registry. Routes are nested under:

`/api/v1/projects/{project_pk}/`

Global (non-project) route: `GET /api/v1/suppliers/` — shared supplier lookup.

## Permissions

| Resource | View | Edit |
|----------|------|------|
| Budgets, actual costs, variance, summary, pools | `view_costs` + `IsProjectMember` (reads) | — |
| Budget/cost/pool/supplier writes | `edit_costs` | Required |
| Project suppliers | `view_suppliers` / `edit_suppliers` | Separate from cost permissions |

All CRUD viewsets extend `ProjectScopedViewSet` (`common/viewsets.py`) for tenancy, soft-delete, and audit fields.

## Budgets

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `budgets/` | GET | List budgets. Filters: `wbs_id`, `activity_id`, `cost_category`. Response includes `summary` rollup and optional `warning` when WBS totals exceed limits. |
| `budgets/` | POST | Create single budget line. |
| `budgets/bulk/` | POST | Bulk upsert array of `{wbs, activity, cost_category, budget_amount, notes}`. Returns `{saved, summary, warning?}`. |
| `budgets/{pk}/` | GET | Budget detail. |
| `budgets/{pk}/` | PATCH | Partial update. |
| `budgets/{pk}/` | DELETE | Soft-delete. |

## Actual costs

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `costs/` | GET | Paginated ledger. Filters: `activity_id`, `wbs_id`, `cost_category`, `cost_type`, `supplier_id`, `date_from`, `date_to`. Response includes `meta.total_actual` and `meta.by_category`. |
| `costs/` | POST | Create manual actual cost. |
| `costs/{pk}/` | GET | Cost detail. |
| `costs/{pk}/` | PATCH | Update. **Blocked** when `daily_report_id` is set (auto-generated from daily report labor). |
| `costs/{pk}/` | DELETE | Soft-delete. **Blocked** for auto-generated costs. |
| `costs/variance/` | GET | Budget vs actual variance. Query: `group_by` (`wbs` default), `as_of`, `force_refresh`. Cached 30 min. |
| `costs/summary/` | GET | Cost summary for EVM integration. Query: `as_of`. |

Auto costs are created when daily reports with labor `daily_rate` are approved (see `field_reports/ENDPOINTS.md`).

## Cost pools

Shared overhead pools allocated across activities.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `cost-pools/` | GET, POST | List/create pools (`total_amount`, `cost_category`, `period`, etc.). |
| `cost-pools/{pk}/` | GET, PATCH, DELETE | CRUD (soft-delete). |
| `cost-pools/{pk}/allocate/` | POST | Manual allocation. Body: array of `{activity_id, amount}`. Raises `AllocationExceededError` if total exceeds remaining pool. |
| `cost-pools/{pk}/auto-allocate/` | POST | Auto-allocate remaining balance. Body: `method` (`by_budget_weight`, `by_quantity`, `by_hours`), optional `activity_ids`. Returns `{pool, allocations}`. |

All pool mutations invalidate project cost caches.

## Suppliers

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `suppliers/` | GET, POST | Project-scoped supplier registry. |
| `suppliers/{pk}/` | GET, PATCH, DELETE | CRUD. |
| `/api/v1/suppliers/` | GET | Global supplier search (`q` param, max 50 results). Auth only. |

## Frontend route

- `/projects/{id}/costs` — budget grid, actual ledger, variance tab, cost pool allocation wizard

## Operational notes

- **Dates:** `date_from`, `date_to`, and `as_of` accept Jalali or Gregorian strings.
- **Cache invalidation:** Budget/cost/pool writes call `invalidate_project_caches(project_id)` (best-effort).
- **Variance grouping:** `group_by=wbs` rolls up by WBS node; other values pass through to `variance_service.get_budget_vs_actual`.

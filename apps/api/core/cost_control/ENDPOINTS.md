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
| `budgets/` | GET | List budgets. Filters: `wbs_id`, `activity_id`, `cost_category`, `version_id`. Defaults to control version when present. Response includes `summary` rollup and optional `warning` when WBS totals exceed limits. |
| `budgets/` | POST | Create single budget line on a draft version (`version` / working draft). Non-draft → `budget_version_locked`. |
| `budgets/bulk/` | POST | Bulk upsert array **or** `{version_id, items:[…]}`. Returns `{saved, version_id, summary, warning?}`. |
| `budgets/{pk}/` | GET | Budget detail. |
| `budgets/{pk}/` | PATCH | Partial update (draft version only). |
| `budgets/{pk}/` | DELETE | Soft-delete (draft version only). |
| `budgets/remaining/` | GET | Remaining allocatable by heading (`approved − committed − consumed`). Query: `version_id` (default control). |
| `budgets/transfers/` | POST | Net-zero transfer on control version: `{from_line_id, to_line_id, amount, note?}`. |

Permissions: reads `view_costs`; writes `edit_costs`; version/CR approve/reject `approve_costs`.

## Budget versions

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `budget-versions/` | GET | List versions (kind, status, `is_control`, totals). |
| `budget-versions/` | POST | Create draft: `{kind: initial\|revised\|final_forecast, name?, currency?, notes?}`. |
| `budget-versions/compare/` | GET | Compare two versions: `left`, `right`, optional `fx_rate` (required if currencies differ → `fx_rate_required`). |
| `budget-versions/{id}/` | GET, PATCH | Detail; patch name/notes while draft. |
| `budget-versions/{id}/lines/` | GET, POST | List/create lines for a version (levels: project/phase/contract/wbs/cbs/activity + optional period). |
| `budget-versions/{id}/submit/` | POST | draft → submitted (≥1 line). |
| `budget-versions/{id}/approve/` | POST | submitted → approved. Body optional `{promote_to_control}` for `final_forecast`. Replacing an existing control without a change request → `budget_change_request_required`. |
| `budget-versions/{id}/reject/` | POST | submitted → rejected (`reason?`). |

## Budget change requests

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `budget-change-requests/` | GET, POST | List / create (`reason`, `project_impact`, `amount_delta`, `affected_lines`). |
| `budget-change-requests/{id}/` | GET, PATCH | Detail / update while draft. |
| `budget-change-requests/{id}/submit/` | POST | draft → submitted. |
| `budget-change-requests/{id}/approve/` | POST | Clone control → new revised control with ops applied. |
| `budget-change-requests/{id}/reject/` | POST | Reject; baseline unchanged. |
| `budget-change-requests/{id}/cancel/` | POST | Cancel open CR. |

Errors of note: `budget_version_locked`, `budget_change_request_required`, `project_ceiling_exceeded`, `no_control_budget`, `change_request_already_open`.

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

## Commitments & payments

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `commitments/` | GET, POST | List/create. Fields include `payment_terms`, optional `contract`, optional `requisition`. |
| `commitments/{id}/` | GET, PATCH, DELETE | Detail/update/soft-delete. Response includes `remaining` (amount − posted payments). |
| `commitments/{id}/approve/` | POST | Approve; requires WBS or CBS (`wbs_or_cbs_required`). |
| `payments/` | GET, POST | List/create payments. Duplicate non-empty `document_ref` in project → `duplicate_payment_document` unless `acknowledge_duplicate_exception` + `exception_reason`. |
| `costs/{id}/approve/` | POST | Approve draft actual (`wbs_or_cbs_required`; `cost_document_required` when project capability `require_cost_document` enabled). |
| `costs/{id}/void/` | POST | Void an approved actual. |
| `costs/ledger-report/` | GET | Rows typed `commitment` \| `actual` \| `payment` with document refs. Filters: `date_from`, `date_to`, `commitment_id`, `document_ref`. |
| `costs/contract-remaining/` | GET | Query `contract_id`. Returns `approved_amount`, `paid_total`, `remaining` from cost payments on linked commitments. |

Procurement handoff: `POST .../requisitions/{id}/create-commitment/` (requires requisition `approved`; permission `edit_costs`).

**Remaining allocatable** (`budgets/remaining/`): `committed` is **open** commitment = max(0, approved commitment − linked approved actuals); `consumed` is approved non-void actuals only.

## Frontend route

- `/projects/{id}/costs` — budget grid, actual ledger, variance tab, cost pool allocation wizard, CBS/commitment, payments/ledger tab
- Approved requisition detail: create-commitment action

## Operational notes

- **Dates:** `date_from`, `date_to`, and `as_of` accept Jalali or Gregorian strings.
- **Cache invalidation:** Budget/cost/pool writes call `invalidate_project_caches(project_id)` (best-effort).
- **Variance grouping:** `group_by=wbs` rolls up by WBS node; other values pass through to `variance_service.get_budget_vs_actual`.
- **Actual cost lifecycle:** new rows default `status=draft`; existing rows backfilled to `approved`.

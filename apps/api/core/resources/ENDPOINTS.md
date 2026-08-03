# Resources App Endpoints

Materials ledger, material requests (procurement workflow), inventory transactions, and balance analytics. All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Area | Permission | Notes |
|------|------------|-------|
| Materials, inventory reads, balance | `view_reports` or `view_procurement` | See per-view `view_permission` |
| Material / transaction writes | `edit_reports` | |
| Material request CRUD | `view_procurement` / `edit_reports` | Create/update uses `edit_reports` on `MaterialRequestViewSet` |
| Approve material request | `approve_procurement` | `MaterialRequestApproveView` |
| Place order, deliver, cancel | `edit_procurement` | Dedicated APIViews |

## Materials

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `materials/` | GET | List materials for the project |
| `materials/` | POST | Create material |
| `materials/{pk}/` | GET | Material detail |
| `materials/{pk}/` | PATCH | Partial update |
| `materials/{pk}/` | DELETE | Soft-delete |

## Material requests

CRUD is handled by `MaterialRequestViewSet`. Workflow transitions (`approve`, `place-order`, `deliver`, `cancel`) are **separate APIViews** in `resources/views.py` (SRP refactor — business logic lives in `procurement_service.py`).

| Endpoint | Method | View | Description |
| :--- | :--- | :--- | :--- |
| `material-requests/` | GET | `MaterialRequestViewSet` | List requests. Filter: `status`. Ordered by `-request_date`, `-request_number`. |
| `material-requests/` | POST | `MaterialRequestViewSet` | Create request; assigns sequential `request_number` per project. |
| `material-requests/{pk}/` | GET | `MaterialRequestViewSet` | Detail with material, activity, and purchase order prefetch. |
| `material-requests/{pk}/` | PATCH | `MaterialRequestViewSet` | Update. **Only `pending` requests are editable.** |
| `material-requests/{pk}/` | DELETE | `MaterialRequestViewSet` | Soft-delete |
| `material-requests/{pk}/approve/` | POST | `MaterialRequestApproveView` | Approve pending request |
| `material-requests/{pk}/place-order/` | POST | `MaterialRequestPlaceOrderView` | Create PO for approved request. Body: `supplier` (required), optional `order_date`, `expected_delivery_date`, `unit_price`, `notes`. |
| `material-requests/{pk}/deliver/` | POST | `MaterialRequestDeliverView` | Mark PO delivered; creates IN inventory transaction. Body: optional `actual_delivery_date`, `document_ref`. |
| `material-requests/{pk}/cancel/` | POST | `MaterialRequestCancelView` | Cancel pending or approved request |

### Procurement workflow

```
pending ──approve──► approved ──place-order──► ordered ──deliver──► delivered
   │                     │
   └────cancel───────────┘──► cancelled
```

| Transition | Required status | Side effects |
|------------|-----------------|--------------|
| Approve | `pending` | Sets `approved_by`, `approved_at` |
| Place order | `approved` | Creates `PurchaseOrder`, status → `ordered` |
| Deliver | `ordered` | Creates `InventoryTransaction` (type `in`), sets PO `actual_delivery_date`, status → `delivered` |
| Cancel | `pending` or `approved` | Status → `cancelled` |

Invalid transitions return `400` with `Cannot {action} while status is {status}` from `ProcurementWorkflowError`.

Dates on place-order/deliver accept Jalali or Gregorian via `parse_jalali_or_gregorian`.

## Inventory transactions

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `inventory-transactions/` | GET, POST | List / create transactions |
| `inventory-transactions/balance/` | GET | Running balance for a material. **Required query:** `material_id`. |
| `inventory-transactions/{pk}/` | GET, PATCH, DELETE | Detail / update / delete. Transactions sourced from daily reports cannot be edited or deleted directly. |

## Material balance & analytics

| Endpoint | Method | Query params | Description |
| :--- | :--- | :--- | :--- |
| `material-balance/` | GET | `discipline`, `location`, `block_type`, `low_stock` | Summarized balances |
| `material-balance/consumption/` | GET | `material_id`, `activity_id`, `date_from`, `date_to` | Consumption vs plan + waste |
| `material-balance/{mid}/` | GET | — | Detail with recent transactions and requests |

## Operational notes

- **Legacy deprecation:** global `/api/items/` (`inventory.Item`) is deprecated; use project-scoped `materials/` (see `docs/ipcas-scope-map.md`).
- **Service layer:** all procurement transitions delegate to `resources/services/procurement_service.py` — views are thin HTTP adapters.

# Resources App Endpoints

Materials ledger, procurement workflow, and inventory transactions. All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Area | Permission | Notes |
|------|------------|-------|
| Materials CRUD | `view_reports` / `edit_reports` | Standard `ProjectScopedViewSet` |
| Material requests (list/detail/create/edit) | `view_procurement` / `edit_reports` | Only `pending` requests are editable |
| Approve request | `approve_procurement` | `MaterialRequestApproveView` |
| Place order, deliver, cancel | `edit_procurement` | Dedicated APIViews (see below) |
| Inventory transactions, balance | `view_reports` / `edit_reports` | Rows linked to a daily report are read-only |

## Endpoints

### Materials
*   **`GET /materials/`**: (`material-list`)
    *   **Purpose**: Lists materials scoped to the current project.
    *   **View**: `MaterialViewSet.list`
*   **`POST /materials/`**: (`material-list`)
    *   **Purpose**: Creates a new material scoped to the current project.
    *   **View**: `MaterialViewSet.create`
*   **`GET /materials/<uuid:pk>/`**: (`material-detail`)
    *   **Purpose**: Retrieves details for a specific material.
    *   **View**: `MaterialViewSet.retrieve`
*   **`PATCH /materials/<uuid:pk>/`**: (`material-detail`)
    *   **Purpose**: Updates a specific material partially.
    *   **View**: `MaterialViewSet.partial_update`
*   **`DELETE /materials/<uuid:pk>/`**: (`material-detail`)
    *   **Purpose**: Deletes a specific material.
    *   **View**: `MaterialViewSet.destroy`

### Material Requests
*   **`GET /material-requests/`**: (`material-request-list`)
    *   **Purpose**: Lists material requests scoped to the current project. Can be filtered by `status`.
    *   **View**: `MaterialRequestViewSet.list`
*   **`POST /material-requests/`**: (`material-request-list`)
    *   **Purpose**: Creates a new material request scoped to the current project. Automatically assigns a sequential request number.
    *   **View**: `MaterialRequestViewSet.create`
*   **`GET /material-requests/<uuid:pk>/`**: (`material-request-detail`)
    *   **Purpose**: Retrieves details for a specific material request.
    *   **View**: `MaterialRequestViewSet.retrieve`
*   **`PATCH /material-requests/<uuid:pk>/`**: (`material-request-detail`)
    *   **Purpose**: Updates a specific material request partially. Note: Only pending requests can be edited.
    *   **View**: `MaterialRequestViewSet.partial_update`
*   **`DELETE /material-requests/<uuid:pk>/`**: (`material-request-detail`)
    *   **Purpose**: Deletes a specific material request.
    *   **View**: `MaterialRequestViewSet.destroy`
*   **`POST /material-requests/<uuid:pk>/approve/`**: (`material-request-approve`)
    *   **Purpose**: Approves a pending material request.
    *   **View**: `MaterialRequestApproveView` → `procurement_service.approve_material_request`
    *   **Permission**: `approve_procurement`
*   **`POST /material-requests/<uuid:pk>/place-order/`**: (`material-request-place-order`)
    *   **Purpose**: Places a purchase order for an approved material request, transitioning it to the ordered status.
    *   **View**: `MaterialRequestPlaceOrderView` → `procurement_service.place_purchase_order`
    *   **Body**: `supplier` (required), optional `order_date`, `expected_delivery_date`, `unit_price`, `notes`
    *   **Permission**: `edit_procurement`
*   **`POST /material-requests/<uuid:pk>/deliver/`**: (`material-request-deliver`)
    *   **Purpose**: Marks a purchase order as delivered, creating an IN inventory transaction and transitioning the request to the delivered status.
    *   **View**: `MaterialRequestDeliverView` → `procurement_service.deliver_purchase_order`
    *   **Body**: optional `actual_delivery_date`, `document_ref`
    *   **Permission**: `edit_procurement`
*   **`POST /material-requests/<uuid:pk>/cancel/`**: (`material-request-cancel`)
    *   **Purpose**: Cancels a pending or approved material request.
    *   **View**: `MaterialRequestCancelView` → `procurement_service.cancel_material_request`
    *   **Permission**: `edit_procurement`

Workflow actions are **standalone APIViews** (not ViewSet `@action`s). Routes are wired in `resources/urls.py`; business logic lives in `resources/services/procurement_service.py`.

### Inventory Transactions
*   **`GET /inventory-transactions/`**: (`inventory-tx-list`)
    *   **Purpose**: Lists inventory transactions scoped to the current project.
    *   **View**: `InventoryTransactionViewSet.list`
*   **`POST /inventory-transactions/`**: (`inventory-tx-list`)
    *   **Purpose**: Creates a new inventory transaction scoped to the current project.
    *   **View**: `InventoryTransactionViewSet.create`
*   **`GET /inventory-transactions/balance/`**: (`inventory-tx-balance`)
    *   **Purpose**: Retrieves a running balance report for a specific material over time. Requires `material_id` query parameter.
    *   **View**: `InventoryRunningBalanceView.get`
*   **`GET /inventory-transactions/<uuid:pk>/`**: (`inventory-tx-detail`)
    *   **Purpose**: Retrieves details for a specific inventory transaction.
    *   **View**: `InventoryTransactionViewSet.retrieve`
*   **`PATCH /inventory-transactions/<uuid:pk>/`**: (`inventory-tx-detail`)
    *   **Purpose**: Updates a specific inventory transaction partially. Note: Transactions created from daily reports cannot be edited directly.
    *   **View**: `InventoryTransactionViewSet.partial_update`
*   **`DELETE /inventory-transactions/<uuid:pk>/`**: (`inventory-tx-detail`)
    *   **Purpose**: Deletes a specific inventory transaction. Note: Transactions created from daily reports cannot be deleted directly.
    *   **View**: `InventoryTransactionViewSet.destroy`

### Material Balance and Analytics
*   **`GET /material-balance/`**: (`material-balance-list`)
    *   **Purpose**: Retrieves a summarized list of material balances for the current project. Can be filtered by `discipline`, `location`, `block_type`, and `low_stock`.
    *   **View**: `MaterialBalanceListView.get`
*   **`GET /material-balance/consumption/`**: (`material-balance-consumption`)
    *   **Purpose**: Retrieves a report comparing material consumption against planned estimates, including waste analytics. Can be filtered by `material_id`, `activity_id`, `date_from`, and `date_to`.
    *   **View**: `MaterialConsumptionView.get`
*   **`GET /material-balance/<uuid:mid>/`**: (`material-balance-detail`)
    *   **Purpose**: Retrieves detailed balance information for a specific material, including its recent transactions and material requests.
    *   **View**: `MaterialBalanceDetailView.get`

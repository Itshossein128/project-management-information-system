# Contracts Endpoints Documentation

This document describes the API endpoints provided by the `contracts` app within the IPCAS project. These endpoints manage contracts, change orders, and Interim Payment Certificates (IPCs). All URLs are nested under a specific project context (i.e., prefixed with `/api/v1/projects/<uuid:project_pk>/`).

## Contracts

### `GET /contracts/`
*   **Purpose**: Retrieves a list of all contracts associated with the project.
*   **Behavior**: Supports filtering via query params: `contract_type`, `status`, `counterparty`. Returns `{ results: [...] }` with per-contract IPC stats.

### `POST /contracts/`
*   **Purpose**: Creates a new contract within the project.
*   **Behavior**: Accepts contract details (e.g., contract number, counterparty, contract type, amounts, deduction percentages).

### `GET /contracts/<uuid:pk>/`
*   **Purpose**: Retrieves detailed information about a specific contract.
*   **Behavior**: Includes contract details along with related change orders and contract items (BoQ).

### `PATCH /contracts/<uuid:pk>/`
*   **Purpose**: Partially updates an existing contract.
*   **Behavior**: Allows modifying fields like counterparty, dates, amounts, or deduction percentages.

### `DELETE /contracts/<uuid:pk>/`
*   **Purpose**: Soft-deletes a specific contract.
*   **Behavior**: Sets `is_deleted=True` on the contract record.

### `POST /contracts/<uuid:pk>/items/`
*   **Purpose**: Bulk upserts the BoQ items associated with a contract.
*   **Behavior**: Accepts a JSON array of item rows (or `{ items: [...] }`). Creates new items or updates existing ones by `id`. Requires `edit_contracts`.

## Change Orders

### `POST /contracts/<uuid:pk>/change-orders/`
*   **Purpose**: Creates a new change order for a given contract.
*   **Behavior**: Accepts `description` and `amount_change`. Auto-assigns the next `change_number`.

### `PATCH /contracts/<uuid:pk>/change-orders/<uuid:chid>/`
*   **Purpose**: Partially updates a change order.
*   **Behavior**: Allows modifying fields such as `description` or `amount_change` while the change order is editable.

### `POST /contracts/<uuid:pk>/change-orders/<uuid:chid>/approve/`
*   **Purpose**: Approves a change order.
*   **Behavior**: Updates status to `approved` and adjusts the contract's `adjusted_amount`. Returns 400 if the resulting adjusted amount would be negative.

### `POST /contracts/<uuid:pk>/change-orders/<uuid:chid>/reject/`
*   **Purpose**: Rejects an approved change order.
*   **Behavior**: Reverses the approved amount adjustment on the contract and sets status to `rejected`.

## Interim Payment Certificates (IPCs)

### `GET /ipcs/`
*   **Purpose**: Retrieves a list of all IPCs within the project.
*   **Behavior**: Supports filtering via query params: `contract_id`, `status`, `overdue=true`. Returns `{ results: [...] }`.

### `POST /ipcs/`
*   **Purpose**: Creates a new draft IPC.
*   **Behavior**: Initializes a payment request for a contract (`contract_id`, optional `period_start`, `period_end`, `notes`). Triggers async populate + deduction calculation (falls back to sync when Celery is unavailable).

### `GET /ipcs/<uuid:pk>/`
*   **Purpose**: Retrieves details of a specific IPC.
*   **Behavior**: Includes line items, deductions (automatic and manual), calculated amounts (`gross_amount`, `net_amount`, `deductions_total`, `net_amount_computed`), and current status.

### `PATCH /ipcs/<uuid:pk>/`
*   **Purpose**: Partially updates a draft IPC.
*   **Behavior**: Modifies `period_start`, `period_end`, `prepared_date`, or `notes`. Only allowed while status is `draft`.

### `POST /ipcs/<uuid:pk>/populate/`
*   **Purpose**: Populates IPC line items from contract BoQ and activity progress for the IPC period.
*   **Behavior**: Runs `auto_populate_ipc` then `apply_deductions`. Returns the updated IPC detail.

### `PATCH /ipcs/<uuid:pk>/items/<uuid:itemid>/`
*   **Purpose**: Updates a specific line item within a draft IPC.
*   **Behavior**: Accepts `qty_current`. Recalculates cumulative quantities, gross amount, and deductions.

### `POST /ipcs/<uuid:pk>/deductions/`
*   **Purpose**: Adds a manual deduction to a draft IPC.
*   **Behavior**: Accepts `deduction_type` (`material_price_diff` or `other`), `amount`, and optional `description`. Recalculates net amount. Deduction lists are returned on IPC detail (`GET /ipcs/<uuid:pk>/`); there is no standalone list endpoint.

### `PATCH /ipcs/<uuid:pk>/deductions/<uuid:did>/`
*   **Purpose**: Updates an existing manual deduction on a draft IPC.
*   **Behavior**: Allows modifying `amount` and/or `description`. Only manual types (`material_price_diff`, `other`) are editable.

### `DELETE /ipcs/<uuid:pk>/deductions/<uuid:did>/`
*   **Purpose**: Soft-removes a manual deduction from a draft IPC.
*   **Behavior**: Deletes the specified manual deduction and recalculates IPC totals.

### `POST /ipcs/<uuid:pk>/submit/`
*   **Purpose**: Submits a draft IPC for review.
*   **Behavior**: Changes status from `draft` to `submitted`. Publishes `ipc.submitted` to the event bus.

### `POST /ipcs/<uuid:pk>/approve/`
*   **Purpose**: Approves a submitted IPC.
*   **Behavior**: Changes status to `approved`, sets `approval_date`, and default `planned_payment_date` (+30 days) if not set. Requires `approve_ipcs`.

### `POST /ipcs/<uuid:pk>/pay/`
*   **Purpose**: Marks an approved IPC as paid.
*   **Behavior**: Changes status to `paid`, records `actual_payment_date` (Gregorian or Jalali), and creates/updates a `CashTransaction` in `cash_flow`. Requires `approve_ipcs`.

### `POST /ipcs/<uuid:pk>/reject/`
*   **Purpose**: Rejects a submitted IPC.
*   **Behavior**: Reverts status to `draft` with optional `reason`. Requires `approve_ipcs`.

### `GET /ipcs/<uuid:pk>/pdf/`
*   **Purpose**: Exports the IPC as a PDF document.
*   **Behavior**: Returns `application/pdf` with line items, totals, and deductions.

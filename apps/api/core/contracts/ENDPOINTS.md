# Contracts Endpoints Documentation

This document describes the API endpoints provided by the `contracts` app within the Velora project. These endpoints manage contracts, change orders, and Interim Payment Certificates (IPCs). All URLs are nested under a specific project context (i.e., prefixed with `/api/v1/projects/<uuid:project_pk>/`).

## Contracts

### `GET /contracts/`
*   **Purpose**: Retrieves a list of all contracts associated with the project.
*   **Behavior**: Supports filtering via query params: `contract_type`, `status`, `counterparty`. Returns `{ results: [...] }` with per-contract IPC stats.

### `POST /contracts/`
*   **Purpose**: Creates a new contract within the project.
*   **Behavior**: Accepts contract details (e.g., contract number, counterparty, contract type, amounts, deduction percentages, **`payment_terms`** free text).

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

### `GET /ipcs/receivables-report/`
*   **Purpose**: Overdue and near-due receivables for approved IPCs with remaining receivable &gt; 0.
*   **Query**: `near_due_days` (default 7), optional `contract_id`.
*   **Behavior**: Returns `summary` counts/amounts and `items` with `band` = `overdue` | `near_due`. Requires `view_contracts`.

### `GET /ipcs/<uuid:pk>/`
*   **Purpose**: Retrieves details of a specific IPC.
*   **Behavior**: Includes line items, deductions, amounts (`gross_amount`, **`submitted_amount`**, **`approved_amount`**, `approval_variance_note`, `net_amount`, collections), and current status.

### `PATCH /ipcs/<uuid:pk>/`
*   **Purpose**: Partially updates a draft IPC.
*   **Behavior**: Modifies `period_start`, `period_end`, `prepared_date`, or `notes`. Only allowed while status is `draft`.

### `POST /ipcs/<uuid:pk>/populate/`
*   **Purpose**: Populates IPC line items from contract BoQ and activity progress for the IPC period.
*   **Behavior**: Runs `auto_populate_ipc` then `apply_deductions`. **Draft only** — after submit, returns `ipc_locked_after_submit` so `gross_amount` cannot be rewritten.

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
*   **Behavior**: Requires `gross_amount` &gt; 0. Freezes **`submitted_amount`** from gross, status → `submitted`. Publishes `ipc.submitted`.

### `POST /ipcs/<uuid:pk>/approve/`
*   **Purpose**: Approves a submitted IPC.
*   **Body (optional)**: `approved_amount` (≤ submitted), `approval_variance_note` (required if reduced), `planned_payment_date`.
*   **Behavior**: Sets **`approved_amount`**, recalculates deductions/net against approved, status → `approved`, default due date +30 days if unset. Codes: `approved_exceeds_submitted`, `approval_variance_note_required`. Requires `approve_ipcs`.

### `POST /ipcs/<uuid:pk>/collections/`
*   **Purpose**: Record a partial cash collection.
*   **Behavior**: Only on **approved** IPCs. Never changes status, submitted/approved/gross/net amounts. Full collection does **not** auto-mark paid.

### `POST /ipcs/<uuid:pk>/pay/`
*   **Purpose**: Marks an approved IPC as paid.
*   **Behavior**: Changes status to `paid`, records `actual_payment_date` (Gregorian or Jalali), and creates/updates a `CashTransaction` in `cash_flow`. Requires `approve_ipcs`.

### `POST /ipcs/<uuid:pk>/reject/`
*   **Purpose**: Rejects a submitted IPC.
*   **Behavior**: Reverts status to `draft` with optional `reason`. Requires `approve_ipcs`.

### `GET /ipcs/<uuid:pk>/pdf/`
*   **Purpose**: Exports the IPC as a PDF document.
*   **Behavior**: Returns `application/pdf` with line items, totals, and deductions.

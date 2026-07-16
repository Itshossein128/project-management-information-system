# Contracts Endpoints Documentation

This document describes the API endpoints provided by the `contracts` app within the IPCAS project. These endpoints manage contracts, change orders, and Interim Payment Certificates (IPCs). All URLs are nested under a specific project context (i.e., prefixed with `/api/projects/<uuid:project_pk>/`).

## Contracts

### `GET /contracts/`
*   **Purpose**: Retrieves a list of all contracts associated with the project.
*   **Behavior**: Supports filtering, searching, and pagination.

### `POST /contracts/`
*   **Purpose**: Creates a new contract within the project.
*   **Behavior**: Accepts contract details (e.g., contract number, title, counterparty, contract type).

### `GET /contracts/<uuid:pk>/`
*   **Purpose**: Retrieves detailed information about a specific contract.
*   **Behavior**: Includes basic contract details along with related change orders, IPCs, and contract items.

### `PATCH /contracts/<uuid:pk>/`
*   **Purpose**: Partially updates an existing contract.
*   **Behavior**: Allows modifying fields like the contract title or counterparty.

### `DELETE /contracts/<uuid:pk>/`
*   **Purpose**: Deletes a specific contract.
*   **Behavior**: Performs a soft delete if implemented, otherwise removes the contract from the database.

### `PUT/PATCH /contracts/<uuid:pk>/items/`
*   **Purpose**: Bulk updates the items associated with a contract.
*   **Behavior**: Often used after creating a contract to add its initial Schedule of Values (SoV) or line items.

## Change Orders

### `POST /contracts/<uuid:pk>/change-orders/`
*   **Purpose**: Creates a new change order for a given contract.
*   **Behavior**: Accepts details for scope or cost changes to the original contract.

### `GET /contracts/<uuid:pk>/change-orders/<uuid:chid>/`
*   **Purpose**: Retrieves details for a specific change order.
*   **Behavior**: Shows the change order's status, financial impact, and related documentation.

### `POST /contracts/<uuid:pk>/change-orders/<uuid:chid>/approve/`
*   **Purpose**: Approves a change order.
*   **Behavior**: Updates the change order status to 'Approved' and typically adjusts the contract's total value accordingly.

### `POST /contracts/<uuid:pk>/change-orders/<uuid:chid>/reject/`
*   **Purpose**: Rejects a change order.
*   **Behavior**: Updates the change order status to 'Rejected' (often requiring a reason) without altering the contract's total value.

## Interim Payment Certificates (IPCs)

### `GET /ipcs/`
*   **Purpose**: Retrieves a list of all IPCs within the project.
*   **Behavior**: Supports filtering by status, contract, or other fields.

### `POST /ipcs/`
*   **Purpose**: Creates a new draft IPC.
*   **Behavior**: Initializes a new payment request for a specific contract.

### `GET /ipcs/<uuid:pk>/`
*   **Purpose**: Retrieves details of a specific IPC.
*   **Behavior**: Includes the IPC's line items, deductions, calculated amounts (gross, net), and its current status.

### `PATCH /ipcs/<uuid:pk>/`
*   **Purpose**: Partially updates a specific draft IPC.
*   **Behavior**: Used to modify general IPC information (e.g., IPC number, start/end dates).

### `POST /ipcs/<uuid:pk>/populate/`
*   **Purpose**: Populates the IPC's line items based on the contract's current items and previous IPCs.
*   **Behavior**: Copies the contract's SoV into the draft IPC, carrying over previously claimed quantities/amounts as the baseline for the current period.

### `PATCH /ipcs/<uuid:pk>/items/<uuid:itemid>/`
*   **Purpose**: Updates a specific line item within a draft IPC.
*   **Behavior**: Used to input the current period's claimed quantity or amount. It automatically recalculates the item's cumulative values and the IPC's total gross amount.

### `GET /ipcs/<uuid:pk>/deductions/`
*   **Purpose**: Retrieves a list of deductions applied to an IPC.
*   **Behavior**: Shows deductions like advance payment recovery, retention, or manual adjustments.

### `POST /ipcs/<uuid:pk>/deductions/`
*   **Purpose**: Adds a new manual deduction to a draft IPC.
*   **Behavior**: Accepts a deduction type (e.g., material price difference) and an amount. Automatically recalculates the IPC's net amount.

### `PATCH /ipcs/<uuid:pk>/deductions/<uuid:did>/`
*   **Purpose**: Updates an existing manual deduction on a draft IPC.
*   **Behavior**: Allows modifying the amount or description of a manual deduction. Recalculates the IPC totals upon save.

### `DELETE /ipcs/<uuid:pk>/deductions/<uuid:did>/`
*   **Purpose**: Removes a manual deduction from a draft IPC.
*   **Behavior**: Deletes the specified deduction and recalculates the IPC totals.

### `POST /ipcs/<uuid:pk>/submit/`
*   **Purpose**: Submits a draft IPC for review.
*   **Behavior**: Changes the IPC status from 'Draft' to 'Submitted'. Publishes an event (e.g., `ipc.submitted`) to the event bus.

### `POST /ipcs/<uuid:pk>/approve/`
*   **Purpose**: Approves a submitted IPC.
*   **Behavior**: Changes the IPC status to 'Approved' and sets an approval date. May also set a planned payment date if one isn't already provided.

### `POST /ipcs/<uuid:pk>/pay/`
*   **Purpose**: Marks an approved IPC as paid.
*   **Behavior**: Changes the IPC status to 'Paid', records the actual payment date, and integrates with the `cash_flow` module by creating or updating a corresponding `CashTransaction`.

### `POST /ipcs/<uuid:pk>/reject/`
*   **Purpose**: Rejects a submitted IPC.
*   **Behavior**: Reverts the IPC status back to 'Draft', allowing for corrections, and typically requires a rejection reason.

### `GET /ipcs/<uuid:pk>/pdf/`
*   **Purpose**: Exports the IPC as a PDF document.
*   **Behavior**: Generates and returns a downloadable PDF representation of the IPC, including its line items, totals, and deductions.

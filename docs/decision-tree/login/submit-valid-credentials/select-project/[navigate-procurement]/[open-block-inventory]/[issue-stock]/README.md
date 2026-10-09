# Decision: Issue block stock

## Context & Screen

- **Route**: `/projects/:projectId/procurement/inventory`
- **Component**: `ProcurementInventoryPage`
- **Initial State**: Continue from Block inventory. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Issue drawer for an allocation; enter quantity and confirm.
- **Inputs**: Block/allocation/requisition-item ID and quantity.

## Authorization & Permissions

- **Required Permissions**: edit_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: issueStock mutation.
- **State Change**: Stock issue and available balance refresh.
- **Navigation**: `/projects/:projectId/procurement/inventory`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Block inventory](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-inventory.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-inventory.tsx)
- [apps/api/core/procurement/views/po_views.py](../../../../../../../../apps/api/core/procurement/views/po_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)

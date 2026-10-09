# Decision: Create stock transfer

## Context & Screen

- **Route**: `/projects/:projectId/procurement/transfers`
- **Component**: `ProcurementTransfersPage`
- **Initial State**: Continue from Internal stock transfers. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Fill transfer form and create, or click create on a pending row.
- **Inputs**: Source/target block, material and quantity for creation; transfer ID for decision.

## Authorization & Permissions

- **Required Permissions**: edit_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createTransfer mutation.
- **State Change**: Transfer status and stock change according to accepted server action.
- **Navigation**: `/projects/:projectId/procurement/transfers`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The documentation records exposed actions; conservation/capacity behavior is not runtime verified here.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Internal stock transfers](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-transfers.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-transfers.tsx)
- [apps/api/core/procurement/views/po_views.py](../../../../../../../../apps/api/core/procurement/views/po_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../../apps/web/src/app/lib/api/materials.ts)

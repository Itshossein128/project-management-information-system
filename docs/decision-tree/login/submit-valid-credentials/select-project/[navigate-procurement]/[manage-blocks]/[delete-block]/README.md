# Decision: Delete block

## Context & Screen

- **Route**: `/projects/:projectId/procurement/blocks`
- **Component**: `ProcurementBlocksPage`
- **Initial State**: Continue from Procurement blocks. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open delete form/action and save or confirm; cancel returns to list.
- **Inputs**: Block code/name/type, related WBS when applicable.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: deleteBlock mutation.
- **State Change**: Block list reloads; system workshop blocks cannot be changed/deleted and requisition-linked deletion is rejected.
- **Navigation**: `/projects/:projectId/procurement/blocks`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Procurement blocks](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-blocks.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-blocks.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../../apps/web/src/app/lib/api/wbs.ts)

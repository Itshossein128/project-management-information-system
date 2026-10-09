# Decision: Save requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/new`
- **Component**: `ProcurementNewPage`
- **Initial State**: Continue from Create purchase requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit the form.
- **Inputs**: Scope, block as applicable, items, priority/date/notes.

## Authorization & Permissions

- **Required Permissions**: edit_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createRequisition.
- **State Change**: Draft requisition saves; navigate to procurement list.
- **Navigation**: `/projects/:projectId/procurement`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Procurement](../../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-new.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-new.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../../apps/web/src/app/lib/api/materials.ts)

# Decision: Hold requisition item

## Context & Screen

- **Route**: `/projects/:projectId/procurement/req/:reqId`
- **Component**: `ProcurementDetailPage`
- **Initial State**: Continue from Open requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Hold beside an eligible item.
- **Inputs**: Requisition/item IDs and quantity or assignee fields.

## Authorization & Permissions

- **Required Permissions**: edit_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: holdRequisitionItem mutation.
- **State Change**: Item hold state refreshes.
- **Navigation**: `/projects/:projectId/procurement/req/:reqId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open requisition](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-detail.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-detail.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/api/core/procurement/permissions.py](../../../../../../../../apps/api/core/procurement/permissions.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/api/core/procurement/views/po_views.py](../../../../../../../../apps/api/core/procurement/views/po_views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)

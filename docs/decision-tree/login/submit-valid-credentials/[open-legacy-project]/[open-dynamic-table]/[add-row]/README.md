# Decision: Add dynamic row

## Context & Screen

- **Route**: `/projects/:businessId/tables/:tableSlug`
- **Component**: `BusinessTablePage`
- **Initial State**: Continue from Open dynamic table. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Add Row, complete schema-driven fields and submit.
- **Inputs**: Table slug and dynamic row fields or file.

## Authorization & Permissions

- **Required Permissions**: Frontend manager/business-setup; backend PROJECT_MEMBER_PERMISSIONS
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST dynamic rows endpoint.
- **State Change**: New row appears.
- **Navigation**: `/projects/:businessId/tables/:tableSlug`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Frontend canEdit and server membership permission policy are separate; field validation depends on schema.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open dynamic table](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/business-table.tsx](../../../../../../../apps/web/src/app/routes/business-table.tsx)
- [apps/api/core/business_meta/data_views.py](../../../../../../../apps/api/core/business_meta/data_views.py)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)

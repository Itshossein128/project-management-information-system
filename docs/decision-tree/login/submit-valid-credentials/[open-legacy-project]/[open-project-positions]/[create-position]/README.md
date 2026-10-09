# Decision: Create project position

## Context & Screen

- **Route**: `/projects/:businessId/job-positions`
- **Component**: `BusinessJobPositionsPage`
- **Initial State**: Continue from Project job positions. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use create control; fill form and save/confirm.
- **Inputs**: slug/label/ordering or selected position ID.

## Authorization & Permissions

- **Required Permissions**: IsHrOrAdmin and IsVisitorReadOnly
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: useCreateJobPosition mutation.
- **State Change**: Positions query refreshes; invalid slug/ordering is rejected before write.
- **Navigation**: `/projects/:businessId/job-positions`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project job positions](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/business-job-positions.tsx](../../../../../../../apps/web/src/app/routes/business-job-positions.tsx)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)
- [apps/api/core/business_meta/permissions.py](../../../../../../../apps/api/core/business_meta/permissions.py)
- [apps/web/src/app/hooks/queries.ts](../../../../../../../apps/web/src/app/hooks/queries.ts)

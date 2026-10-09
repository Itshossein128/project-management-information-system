# Decision: Record ready-mix delivery

## Context & Screen

- **Route**: `/projects/:projectId/concrete-operations`
- **Component**: `ProjectConcreteOperationsPage`
- **Initial State**: Continue from Concrete operations. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit ready-mix delivery form.
- **Inputs**: Date, delivered m³, supplier and ticket number.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createReadyMixDelivery mutation.
- **State Change**: Relevant rows and produced/delivered totals refresh. Poured volume is sourced from daily-report concrete logs.
- **Navigation**: `/projects/:projectId/concrete-operations`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Concrete operations](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-concrete-operations.tsx](../../../../../../../apps/web/src/app/routes/project-concrete-operations.tsx)
- [apps/web/src/app/lib/api/concrete-operations.ts](../../../../../../../apps/web/src/app/lib/api/concrete-operations.ts)
- [apps/api/core/concrete_operations/views.py](../../../../../../../apps/api/core/concrete_operations/views.py)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)

# Decision: Create barriers record

## Context & Screen

- **Route**: `/projects/:projectId/barriers`
- **Component**: `ProjectBarriersPage`
- **Initial State**: Continue from Barriers. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use create in the grid/drawer and save or confirm.
- **Inputs**: Selected record and form values.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createBarrier mutation.
- **State Change**: Grid refreshes after success; close/cancel retains existing server data.
- **Navigation**: `/projects/:projectId/barriers`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Barriers](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-barriers.tsx](../../../../../../../apps/web/src/app/routes/project-barriers.tsx)
- [apps/api/core/risk/views.py](../../../../../../../apps/api/core/risk/views.py)
- [apps/web/src/components/barriers/BarriersGrid.tsx](../../../../../../../apps/web/src/components/barriers/BarriersGrid.tsx)

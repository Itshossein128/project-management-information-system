# Decision: Record risk/delay event

## Context & Screen

- **Route**: `/projects/:projectId/risk-register`
- **Component**: `ProjectRiskRegisterPage`
- **Initial State**: Continue from Risk and delay register. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Add Event, fill severity/probability/type/date fields and save.
- **Inputs**: Risk event form.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createRiskEvent.
- **State Change**: Risk event list and matrix refresh.
- **Navigation**: `/projects/:projectId/risk-register`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Risk and delay register](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-risk-register.tsx](../../../../../../../apps/web/src/app/routes/project-risk-register.tsx)
- [apps/api/core/risk/views.py](../../../../../../../apps/api/core/risk/views.py)
- [apps/web/src/app/lib/api/risk-events.ts](../../../../../../../apps/web/src/app/lib/api/risk-events.ts)

# Decision: Security approve leave

## Context & Screen

- **Route**: `/projects/:projectId/leave-requests`
- **Component**: `ProjectLeaveRequestsPage`
- **Initial State**: Continue from Leave requests. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the security approval/rejection control at its supported status.
- **Inputs**: Request ID; approved=true and optional hours/notes.

## Authorization & Permissions

- **Required Permissions**: approve_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST securityApproveLeave.
- **State Change**: Request becomes security_approved and the list refreshes.
- **Navigation**: `/projects/:projectId/leave-requests`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Security decision is available only for mission-type leave after manager_approved status.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Leave requests](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-leave-requests.tsx](../../../../../../../apps/web/src/app/routes/project-leave-requests.tsx)
- [apps/api/core/hr/views.py](../../../../../../../apps/api/core/hr/views.py)
- [apps/web/src/app/lib/api/hr-forms.ts](../../../../../../../apps/web/src/app/lib/api/hr-forms.ts)
- [apps/api/core/hr/services/leave_overtime.py](../../../../../../../apps/api/core/hr/services/leave_overtime.py)

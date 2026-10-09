# Decision: Manage schedule change requests

## Context & Screen

- **Route**: `/projects/:projectId/schedule/gantt`
- **Component**: `ProjectScheduleGanttPage`
- **Initial State**: Continue from Schedule Gantt. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click New or an existing request; add/remove activity changes and save.
- **Inputs**: Request title/reason and proposed activity date/duration changes.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createScheduleChangeRequest or PATCH updateScheduleChangeRequest.
- **State Change**: Draft request is saved; no approved schedule change yet.
- **Navigation**: `/projects/:projectId/schedule/gantt`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Submit schedule change request](%5Bsubmit-change-request%5D/README.md)
- [Approve schedule change request](%5Bapprove-change-request%5D/README.md)
- [Reject schedule change request](%5Breject-change-request%5D/README.md)

Continue / return links (the same state is documented once):

- [Schedule Gantt](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-schedule-gantt.tsx](../../../../../../../apps/web/src/app/routes/project-schedule-gantt.tsx)
- [apps/api/core/schedule/gantt_views.py](../../../../../../../apps/api/core/schedule/gantt_views.py)
- [apps/web/src/components/schedule/ChangeRequestPanel.tsx](../../../../../../../apps/web/src/components/schedule/ChangeRequestPanel.tsx)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../apps/web/src/app/lib/api/schedule.ts)
- [apps/api/core/schedule/change_request_views.py](../../../../../../../apps/api/core/schedule/change_request_views.py)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/gantt.ts](../../../../../../../apps/web/src/app/lib/api/gantt.ts)

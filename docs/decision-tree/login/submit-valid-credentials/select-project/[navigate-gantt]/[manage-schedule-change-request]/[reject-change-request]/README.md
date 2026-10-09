# Decision: Reject schedule change request

## Context & Screen

- **Route**: `/projects/:projectId/schedule/gantt`
- **Component**: `ProjectScheduleGanttPage`
- **Initial State**: Continue from Manage schedule change requests. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click reject for an eligible selected request.
- **Inputs**: Request ID; decision notes when applicable.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: rejectScheduleChangeRequest helper (POST).
- **State Change**: Workflow action is recorded; approval applies the validated schedule changes.
- **Navigation**: `/projects/:projectId/schedule/gantt`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Manage schedule change requests](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-schedule-gantt.tsx](../../../../../../../../apps/web/src/app/routes/project-schedule-gantt.tsx)
- [apps/api/core/schedule/gantt_views.py](../../../../../../../../apps/api/core/schedule/gantt_views.py)
- [apps/web/src/components/schedule/ChangeRequestPanel.tsx](../../../../../../../../apps/web/src/components/schedule/ChangeRequestPanel.tsx)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../../apps/web/src/app/lib/api/schedule.ts)
- [apps/api/core/schedule/change_request_views.py](../../../../../../../../apps/api/core/schedule/change_request_views.py)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/gantt.ts](../../../../../../../../apps/web/src/app/lib/api/gantt.ts)

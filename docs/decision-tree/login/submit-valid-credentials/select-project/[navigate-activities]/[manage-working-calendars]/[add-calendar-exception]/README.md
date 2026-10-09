# Decision: Add calendar exception

## Context & Screen

- **Route**: `/projects/:projectId/activities`
- **Component**: `ProjectActivitiesPage`
- **Initial State**: Continue from Manage working calendars. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter exception date/hours and click Add.
- **Inputs**: Calendar and exception fields.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createCalendarException mutation.
- **State Change**: Parent query reloads on success; validation failures keep the current state.
- **Navigation**: `/projects/:projectId/activities`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Manage working calendars](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-activities.tsx](../../../../../../../../apps/web/src/app/routes/project-activities.tsx)
- [apps/api/core/schedule/activity_views.py](../../../../../../../../apps/api/core/schedule/activity_views.py)
- [apps/web/src/components/schedule/WorkingCalendarPanel.tsx](../../../../../../../../apps/web/src/components/schedule/WorkingCalendarPanel.tsx)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../../apps/web/src/app/lib/api/schedule.ts)
- [apps/api/core/schedule/calendar_views.py](../../../../../../../../apps/api/core/schedule/calendar_views.py)

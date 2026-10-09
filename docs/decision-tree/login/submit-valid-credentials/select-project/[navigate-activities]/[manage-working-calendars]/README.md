# Decision: Manage working calendars

## Context & Screen

- **Route**: `/projects/:projectId/activities`
- **Component**: `ProjectActivitiesPage`
- **Initial State**: Continue from Activities. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select a calendar; create it, set default, delete it or add/remove an exception.
- **Inputs**: Calendar working days/hours; exception date and values.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createWorkingCalendar, updateWorkingCalendar, deleteWorkingCalendar, createCalendarException, deleteCalendarException.
- **State Change**: Calendar list and exception records refresh.
- **Navigation**: `/projects/:projectId/activities`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Create calendar](%5Bcreate-calendar%5D/README.md)
- [Set default calendar](%5Bset-default-calendar%5D/README.md)
- [Delete calendar](%5Bdelete-calendar%5D/README.md)
- [Add calendar exception](%5Badd-calendar-exception%5D/README.md)
- [Delete exception](%5Bdelete-calendar-exception%5D/README.md)

Continue / return links (the same state is documented once):

- [Activities](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-activities.tsx](../../../../../../../apps/web/src/app/routes/project-activities.tsx)
- [apps/api/core/schedule/activity_views.py](../../../../../../../apps/api/core/schedule/activity_views.py)
- [apps/web/src/components/schedule/WorkingCalendarPanel.tsx](../../../../../../../apps/web/src/components/schedule/WorkingCalendarPanel.tsx)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../apps/web/src/app/lib/api/schedule.ts)
- [apps/api/core/schedule/calendar_views.py](../../../../../../../apps/api/core/schedule/calendar_views.py)

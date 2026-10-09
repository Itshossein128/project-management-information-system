# Decision: Export Gantt PDF

## Context & Screen

- **Route**: `/projects/:projectId/schedule/gantt`
- **Component**: `ProjectScheduleGanttPage`
- **Initial State**: Continue from Schedule Gantt. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export PDF.
- **Inputs**: Current baseline/view.

## Authorization & Permissions

- **Required Permissions**: view_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET downloadGanttPdf.
- **State Change**: Browser downloads a PDF; schedule records are unchanged.
- **Navigation**: `/projects/:projectId/schedule/gantt`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Schedule Gantt](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-schedule-gantt.tsx](../../../../../../../apps/web/src/app/routes/project-schedule-gantt.tsx)
- [apps/api/core/schedule/gantt_views.py](../../../../../../../apps/api/core/schedule/gantt_views.py)
- [apps/web/src/app/lib/api/gantt.ts](../../../../../../../apps/web/src/app/lib/api/gantt.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../apps/web/src/app/lib/api/schedule.ts)

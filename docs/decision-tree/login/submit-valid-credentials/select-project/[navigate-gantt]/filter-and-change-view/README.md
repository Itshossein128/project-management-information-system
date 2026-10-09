# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/schedule/gantt`
- **Component**: `ProjectScheduleGanttPage`
- **Initial State**: Continue from Schedule Gantt. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select baseline, scale or task on Gantt; inspect schedule status and activity drilldown.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchGantt / fetchScheduleStatus; Gantt selected task uses fetchActivity.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
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
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/gantt.ts](../../../../../../../apps/web/src/app/lib/api/gantt.ts)
- [apps/web/src/app/lib/api/schedule.ts](../../../../../../../apps/web/src/app/lib/api/schedule.ts)

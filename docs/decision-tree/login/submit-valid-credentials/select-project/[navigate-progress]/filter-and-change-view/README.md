# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Progress dashboard. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Change date range, interval, WBS/activity filter or force-refresh chart.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchSCurve / fetchActivityProgress with selected parameters.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/progress`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Progress dashboard](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-progress.tsx](../../../../../../../apps/web/src/app/routes/project-progress.tsx)
- [apps/api/core/schedule/progress_views.py](../../../../../../../apps/api/core/schedule/progress_views.py)
- [apps/web/src/app/lib/api/progress.ts](../../../../../../../apps/web/src/app/lib/api/progress.ts)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../apps/web/src/app/lib/api/economic.ts)

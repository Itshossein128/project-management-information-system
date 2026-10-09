# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/activity-log`
- **Component**: `ProjectActivityLogPage`
- **Initial State**: Continue from Activity bank. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose date, department, location, contractor and activity filters; page results.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchActivityLog with parameters.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/activity-log`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Activity bank](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-activity-log.tsx](../../../../../../../apps/web/src/app/routes/project-activity-log.tsx)
- [apps/api/core/sub_reports/views.py](../../../../../../../apps/api/core/sub_reports/views.py)
- [apps/web/src/app/lib/api/reports.ts](../../../../../../../apps/web/src/app/lib/api/reports.ts)

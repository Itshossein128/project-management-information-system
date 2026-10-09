# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/barriers`
- **Component**: `ProjectBarriersPage`
- **Initial State**: Continue from Barriers. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use the displayed date/status/search filters, grouping or table/calendar selection.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET the screen’s query helper with selected filters.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/barriers`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Barriers](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-barriers.tsx](../../../../../../../apps/web/src/app/routes/project-barriers.tsx)
- [apps/api/core/risk/views.py](../../../../../../../apps/api/core/risk/views.py)

# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/labor-productivity`
- **Component**: `ProjectLaborProductivityPage`
- **Initial State**: Continue from Labor productivity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use this screen’s visible date, category, discipline, grouping, detail/summary or Mine/All controls.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET the route’s query helper with selected filters; local grouping uses in-memory state where implemented.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/labor-productivity`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Labor productivity](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-labor-productivity.tsx](../../../../../../../apps/web/src/app/routes/project-labor-productivity.tsx)
- [apps/web/src/app/lib/api/labor-productivity.ts](../../../../../../../apps/web/src/app/lib/api/labor-productivity.ts)

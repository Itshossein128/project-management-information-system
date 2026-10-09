# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/concrete-operations`
- **Component**: `ProjectConcreteOperationsPage`
- **Initial State**: Continue from Concrete operations. This node describes the state reached by the action below.

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
- **Navigation**: `/projects/:projectId/concrete-operations`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Concrete operations](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-concrete-operations.tsx](../../../../../../../apps/web/src/app/routes/project-concrete-operations.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/concrete-operations.ts](../../../../../../../apps/web/src/app/lib/api/concrete-operations.ts)

# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Open Actual costs tab. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Filter date/category/source and page actual cost results.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchActualCosts with filters.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open Actual costs tab](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/ActualCostsTab.tsx](../../../../../../../../apps/web/src/components/costs/ActualCostsTab.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)

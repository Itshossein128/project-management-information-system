# Decision: Open Actual costs tab

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Cost control. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Actual costs tab.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchActualCosts as required.
- **State Change**: The selected tab and data are displayed.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Record actual cost](%5Brecord-actual-cost%5D/README.md)

Continue / return links (the same state is documented once):

- [Cost control](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/ActualCostsTab.tsx](../../../../../../../apps/web/src/components/costs/ActualCostsTab.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)

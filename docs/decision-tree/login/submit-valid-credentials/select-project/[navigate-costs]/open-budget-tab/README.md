# Decision: Open Budget tab

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Cost control. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Budget tab.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchBudgetVersions / fetchBudgets / fetchBudgetRemaining as required.
- **State Change**: The selected tab and data are displayed.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create budget version](%5Bcreate-version%5D/README.md)
- [Save budget line](%5Bsave-budget-line%5D/README.md)
- [Save WBS budget grid](%5Bsave-grid-budget%5D/README.md)
- [Transfer remaining allocation](%5Btransfer-budget%5D/README.md)
- [Submit budget version](%5Bsubmit-version%5D/README.md)
- [Approve budget version](%5Bapprove-version%5D/README.md)
- [Reject budget version](%5Breject-version%5D/README.md)
- [Compare budget versions](%5Bcompare-versions%5D/README.md)
- [Create budget change request](%5Bcreate-budget-change-request%5D/README.md)

Continue / return links (the same state is documented once):

- [Cost control](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/BudgetVersionsPanel.tsx](../../../../../../../apps/web/src/components/costs/BudgetVersionsPanel.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)

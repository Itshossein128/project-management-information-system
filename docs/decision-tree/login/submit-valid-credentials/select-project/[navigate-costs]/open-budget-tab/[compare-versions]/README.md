# Decision: Compare budget versions

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Open Budget tab. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select two different versions, optionally supply FX rate and click Compare.
- **Inputs**: Left/right version IDs and FX rate.

## Authorization & Permissions

- **Required Permissions**: view_costs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET compareBudgetVersions.
- **State Change**: Comparison differences and exchange rate display; no budget mutation.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open Budget tab](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/BudgetVersionsPanel.tsx](../../../../../../../../apps/web/src/components/costs/BudgetVersionsPanel.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)

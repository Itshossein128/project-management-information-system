# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/material-balance`
- **Component**: `ProjectMaterialBalancePage`
- **Initial State**: Continue from Material balance. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Switch Balance, Requests and Transactions; select material/date filters.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchMaterialBalance / fetchMaterialConsumption; Requests uses fetchMaterialRequests (view_procurement).
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/material-balance`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Material balance](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-material-balance.tsx](../../../../../../../apps/web/src/app/routes/project-material-balance.tsx)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../apps/web/src/app/lib/api/materials.ts)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)

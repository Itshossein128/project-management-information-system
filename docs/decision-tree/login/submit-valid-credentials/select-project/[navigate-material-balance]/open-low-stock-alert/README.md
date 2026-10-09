# Decision: Open low-stock alerts

## Context & Screen

- **Route**: `/projects/:projectId/material-balance`
- **Component**: `ProjectMaterialBalancePage`
- **Initial State**: Continue from Material balance. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the low-stock link on a balance row.
- **Inputs**: Low-stock row.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Navigate to the alerts route; its own permissions and filtering behavior apply.
- **Navigation**: `/projects/:projectId/alerts?type=low_stock`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Alerts](../../%5Bnavigate-alerts%5D/README.md)

## Source Evidence

- [apps/web/src/app/routes/project-material-balance.tsx](../../../../../../../apps/web/src/app/routes/project-material-balance.tsx)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../apps/web/src/app/lib/api/materials.ts)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)

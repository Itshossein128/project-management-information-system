# Decision: View projected cash and suggested net need

## Context & Screen

- **Route**: `/projects/:projectId/cash-flow`
- **Component**: `ProjectCashFlowPage`
- **Initial State**: Continue from Cash flow. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Projection tab.
- **Inputs**: The panel uses fromMonth/toMonth supplied by its route.

## Authorization & Permissions

- **Required Permissions**: view_cashflow
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET fetchProjection / fetchSuggestedNeed.
- **State Change**: Monthly projected inflow/outflow/balance and suggested net need display.
- **Navigation**: `/projects/:projectId/cash-flow`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Cash flow](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-cash-flow.tsx](../../../../../../../apps/web/src/app/routes/project-cash-flow.tsx)
- [apps/api/core/cash_flow/views.py](../../../../../../../apps/api/core/cash_flow/views.py)
- [apps/web/src/components/cashflow/ProjectionPanel.tsx](../../../../../../../apps/web/src/components/cashflow/ProjectionPanel.tsx)
- [apps/web/src/app/lib/api/cashflow.ts](../../../../../../../apps/web/src/app/lib/api/cashflow.ts)

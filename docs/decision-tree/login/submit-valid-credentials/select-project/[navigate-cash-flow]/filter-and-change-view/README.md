# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/cash-flow`
- **Component**: `ProjectCashFlowPage`
- **Initial State**: Continue from Cash flow. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose Transactions, Forecast or Gap Analysis; filter/sort transactions.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchCashFlowList / fetchForecast / fetchGapAnalysis.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
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

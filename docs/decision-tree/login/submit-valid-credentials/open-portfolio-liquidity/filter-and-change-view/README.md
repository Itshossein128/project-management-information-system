# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/portfolio/liquidity`
- **Component**: `PortfolioLiquidityPage`
- **Initial State**: Continue from Portfolio liquidity allocation. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose an existing liquidity cycle.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchPortfolioCashReport with cycle_id.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/portfolio/liquidity`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Portfolio liquidity allocation](../README.md)

## Source Evidence

- [apps/web/src/app/routes/portfolio-liquidity.tsx](../../../../../../apps/web/src/app/routes/portfolio-liquidity.tsx)
- [apps/api/core/cash_flow/views.py](../../../../../../apps/api/core/cash_flow/views.py)
- [apps/api/core/cash_flow/services/portfolio_access.py](../../../../../../apps/api/core/cash_flow/services/portfolio_access.py)
- [apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx](../../../../../../apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx)

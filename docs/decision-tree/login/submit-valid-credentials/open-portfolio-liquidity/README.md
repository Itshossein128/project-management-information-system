# Decision: Portfolio liquidity allocation

## Context & Screen

- **Route**: `/portfolio/liquidity`
- **Component**: `PortfolioLiquidityPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Portfolio Liquidity on the project list.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET through listLiquidityCycles, fetchPortfolioCashReport.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/portfolio/liquidity`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Cycle/proposal/decision endpoints use IsAuthenticated. Portfolio project rows are filtered by active membership plus view_cashflow (global admins bypass this filter). The current workbench hard-codes cycle period 2026-10-01 to 2026-12-31, report months 2026-10 to 2026-12, and decision lines to October; these dates are not editable controls.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create liquidity cycle](create-cycle/README.md)
- [Generate allocation proposal](generate-proposal/README.md)
- [Record allocation decision](save-decision/README.md)
- [Compare allocation simulation](simulate-allocation/README.md)
- [Acknowledge overlapping allocation](acknowledge-overlap-and-retry/README.md)
- [Open project cash flow](open-project-cash-flow/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/portfolio-liquidity.tsx](../../../../../apps/web/src/app/routes/portfolio-liquidity.tsx)
- [apps/api/core/cash_flow/views.py](../../../../../apps/api/core/cash_flow/views.py)
- [apps/api/core/cash_flow/services/portfolio_access.py](../../../../../apps/api/core/cash_flow/services/portfolio_access.py)
- [apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx](../../../../../apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx)

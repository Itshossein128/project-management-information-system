# Decision: Generate allocation proposal

## Context & Screen

- **Route**: `/portfolio/liquidity`
- **Component**: `PortfolioLiquidityPage`
- **Initial State**: Continue from Portfolio liquidity allocation. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select cycle and click Generate Proposal.
- **Inputs**: Selected cycle and displayed operation-specific values.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: proposeAllocation request(s).
- **State Change**: Ranked suggested amounts display; no_available_liquidity can produce no proposal lines.
- **Navigation**: `/portfolio/liquidity`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The workbench does not display every mutation error: save-decision has explicit error UI; cycle/proposal/simulation handlers currently have no explicit error renderer.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Portfolio liquidity allocation](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/portfolio-liquidity.tsx](../../../../../../apps/web/src/app/routes/portfolio-liquidity.tsx)
- [apps/api/core/cash_flow/views.py](../../../../../../apps/api/core/cash_flow/views.py)
- [apps/api/core/cash_flow/services/portfolio_access.py](../../../../../../apps/api/core/cash_flow/services/portfolio_access.py)
- [apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx](../../../../../../apps/web/src/components/cashflow/allocation/AllocationWorkbench.tsx)
- [apps/web/src/app/lib/api/cashflow.ts](../../../../../../apps/web/src/app/lib/api/cashflow.ts)
- [apps/api/core/cash_flow/services/allocation_service.py](../../../../../../apps/api/core/cash_flow/services/allocation_service.py)

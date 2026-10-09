# Decision: Adjust monthly forecast

## Context & Screen

- **Route**: `/projects/:projectId/cash-flow`
- **Component**: `ProjectCashFlowPage`
- **Initial State**: Continue from Cash flow. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Change a forecast input and blur, or move a probability slider and release.
- **Inputs**: Transaction or month and operation-specific fields.

## Authorization & Permissions

- **Required Permissions**: edit_cashflow
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: upsertForecast mutation.
- **State Change**: Monthly forecast saves with PUT; gap query is refreshed.
- **Navigation**: `/projects/:projectId/cash-flow`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

System/source-derived rows and backend validation may restrict editing; UI save remains subject to server acceptance.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Cash flow](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-cash-flow.tsx](../../../../../../../apps/web/src/app/routes/project-cash-flow.tsx)
- [apps/api/core/cash_flow/views.py](../../../../../../../apps/api/core/cash_flow/views.py)
- [apps/web/src/components/cashflow/TransactionsTab.tsx](../../../../../../../apps/web/src/components/cashflow/TransactionsTab.tsx)
- [apps/web/src/components/cashflow/ForecastTab.tsx](../../../../../../../apps/web/src/components/cashflow/ForecastTab.tsx)
- [apps/web/src/app/lib/api/cashflow.ts](../../../../../../../apps/web/src/app/lib/api/cashflow.ts)

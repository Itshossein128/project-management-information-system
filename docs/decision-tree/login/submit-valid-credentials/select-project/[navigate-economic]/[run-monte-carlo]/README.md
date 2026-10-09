# Decision: Run Monte Carlo simulation

## Context & Screen

- **Route**: `/projects/:projectId/economic`
- **Component**: `ProjectEconomicPage`
- **Initial State**: Continue from Economic analysis. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Set iterations/scenario values and click Run.
- **Inputs**: iterations and scenario_params.

## Authorization & Permissions

- **Required Permissions**: view_dashboard
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST runSimulation; GET fetchSimulationStatus polling.
- **State Change**: Task ID is returned before completion; percentiles/results appear after the task completes.
- **Navigation**: `/projects/:projectId/economic`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Requires the configured task runtime; accepted task ID is not a completed simulation.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Economic analysis](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-economic.tsx](../../../../../../../apps/web/src/app/routes/project-economic.tsx)
- [apps/api/core/economic/views.py](../../../../../../../apps/api/core/economic/views.py)
- [apps/web/src/components/economic/MonteCarloPanel.tsx](../../../../../../../apps/web/src/components/economic/MonteCarloPanel.tsx)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../apps/web/src/app/lib/api/economic.ts)

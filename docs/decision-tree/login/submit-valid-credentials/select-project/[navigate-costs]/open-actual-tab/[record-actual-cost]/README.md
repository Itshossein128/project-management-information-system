# Decision: Record actual cost

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Open Actual costs tab. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Add Cost, fill the drawer and Save.
- **Inputs**: Cost date/category/amount, optional WBS/activity/supplier; corrective flag and reason where required.

## Authorization & Permissions

- **Required Permissions**: edit_costs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createActualCost.
- **State Change**: Manual actual-cost row and summaries refresh after acceptance.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Fiscal lock and corrective rules still apply; a locked date without permitted corrective reason disables or rejects the write. Source-generated costs are not this manual entry.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open Actual costs tab](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/ActualCostsTab.tsx](../../../../../../../../apps/web/src/components/costs/ActualCostsTab.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/api/core/cost_control/services/actual_cost_service.py](../../../../../../../../apps/api/core/cost_control/services/actual_cost_service.py)

# Decision: Save budget line

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Continue from Open Budget tab. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select draft version, CBS/WBS/activity/contract association and enter line fields, then Save.
- **Inputs**: Version/line IDs and displayed form values.

## Authorization & Permissions

- **Required Permissions**: edit_costs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createBudgetVersionLine mutation.
- **State Change**: Version line is validated and stored.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open Budget tab](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/api/core/cost_control/views.py](../../../../../../../../apps/api/core/cost_control/views.py)
- [apps/web/src/components/costs/BudgetVersionsPanel.tsx](../../../../../../../../apps/web/src/components/costs/BudgetVersionsPanel.tsx)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../../apps/web/src/app/lib/api/costs.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/components/costs/BudgetLineEditor.tsx](../../../../../../../../apps/web/src/components/costs/BudgetLineEditor.tsx)
- [apps/api/core/cost_control/budget_version_views.py](../../../../../../../../apps/api/core/cost_control/budget_version_views.py)

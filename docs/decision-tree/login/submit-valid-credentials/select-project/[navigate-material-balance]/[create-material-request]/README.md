# Decision: Create legacy material request

## Context & Screen

- **Route**: `/projects/:projectId/material-balance`
- **Component**: `ProjectMaterialBalancePage`
- **Initial State**: Continue from Material balance. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: On Requests, select material/quantity and save.
- **Inputs**: Material ID and requested quantity.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createMaterialRequest.
- **State Change**: Material-request table refreshes. This is distinct from the scope-based purchase requisition workflow.
- **Navigation**: `/projects/:projectId/material-balance`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Material balance](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-material-balance.tsx](../../../../../../../apps/web/src/app/routes/project-material-balance.tsx)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../apps/web/src/app/lib/api/materials.ts)
- [apps/api/core/resources/views.py](../../../../../../../apps/api/core/resources/views.py)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)

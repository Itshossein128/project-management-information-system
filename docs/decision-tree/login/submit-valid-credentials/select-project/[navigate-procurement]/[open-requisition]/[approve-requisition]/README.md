# Decision: Approve requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/req/:reqId`
- **Component**: `ProcurementDetailPage`
- **Initial State**: Continue from Open requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click approve; fill comments in the action drawer when offered.
- **Inputs**: Current requisition and comments.

## Authorization & Permissions

- **Required Permissions**: ProcurementStepPermission: required current-step role
- **Required Roles / Groups**: Current step: block_engineer or workshop_supervisor (draft scope); technical_office, workshop_supervisor, project_controller, project_manager, procurement_officer, hq_project_controller or ceo_or_pm_budget thereafter; staff/superuser/admin override.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST approveRequisition.
- **State Change**: The scope-specific approval engine advances, returns to a prior step, or rejects; approval log refreshes.
- **Navigation**: `/projects/:projectId/procurement/req/:reqId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Block draft role: block_engineer; workshop draft role: workshop_supervisor. Later roles: technical_office, workshop_supervisor (block scope), project_controller, project_manager, procurement_officer, hq_project_controller, ceo_or_pm_budget. Staff/superuser/admin can override this step gate. Action validity and budget/liquidity validators still apply; frontend status controls do not prove authorization.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open requisition](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-detail.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-detail.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/api/core/procurement/permissions.py](../../../../../../../../apps/api/core/procurement/permissions.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/api/core/procurement/services/approval_engine.py](../../../../../../../../apps/api/core/procurement/services/approval_engine.py)
- [apps/api/core/procurement/views/approval_views.py](../../../../../../../../apps/api/core/procurement/views/approval_views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)

# Decision: Create commitment from requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/req/:reqId`
- **Component**: `ProcurementDetailPage`
- **Initial State**: Continue from Open requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: On an approved requisition, enter commitment details and click Create Commitment.
- **Inputs**: Commitment number/date/amount and optional associations/payment terms.

## Authorization & Permissions

- **Required Permissions**: edit_costs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createCommitmentFromRequisition.
- **State Change**: Draft cost commitment is created from the approved requisition.
- **Navigation**: `/projects/:projectId/procurement/req/:reqId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open requisition](../README.md)
- [Open CBS and commitments tab](../../../%5Bnavigate-costs%5D/open-cbs-tab/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-detail.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-detail.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/api/core/procurement/permissions.py](../../../../../../../../apps/api/core/procurement/permissions.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/api/core/procurement/views/create_commitment_view.py](../../../../../../../../apps/api/core/procurement/views/create_commitment_view.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)

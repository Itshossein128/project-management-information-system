# Decision: Edit contract

## Context & Screen

- **Route**: `/projects/:projectId/contracts/:contractId`
- **Component**: `ProjectContractDetailPage`
- **Initial State**: Continue from Open contract. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Edit, change header/terms and Save.
- **Inputs**: Selected contract and displayed form fields.

## Authorization & Permissions

- **Required Permissions**: edit_contracts
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: updateContract mutation.
- **State Change**: Contract detail query refreshes.
- **Navigation**: `/projects/:projectId/contracts/:contractId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open contract](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-contract-detail.tsx](../../../../../../../../apps/web/src/app/routes/project-contract-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)

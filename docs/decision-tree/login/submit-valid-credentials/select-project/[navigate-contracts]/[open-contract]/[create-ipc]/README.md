# Decision: Create IPC

## Context & Screen

- **Route**: `/projects/:projectId/contracts/:contractId`
- **Component**: `ProjectContractDetailPage`
- **Initial State**: Continue from Open contract. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click New IPC, enter period and move to review, then Create.
- **Inputs**: Contract ID, IPC period and form values.

## Authorization & Permissions

- **Required Permissions**: edit_ipcs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createIPC; wizard calls populateIPC after creation.
- **State Change**: Draft IPC is created/populated and its detail page opens.
- **Navigation**: `/projects/:projectId/ipcs/:ipcId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Creating and populating are separate requests; a populate failure can follow a created draft.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open IPC](../../%5Bopen-ipc%5D/README.md)
- [Open contract](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-contract-detail.tsx](../../../../../../../../apps/web/src/app/routes/project-contract-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/components/contracts/IPCWizard.tsx](../../../../../../../../apps/web/src/components/contracts/IPCWizard.tsx)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)

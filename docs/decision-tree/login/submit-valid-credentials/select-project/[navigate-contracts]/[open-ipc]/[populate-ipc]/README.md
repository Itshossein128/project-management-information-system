# Decision: Populate draft IPC

## Context & Screen

- **Route**: `/projects/:projectId/ipcs/:ipcId`
- **Component**: `ProjectIPCDetailPage`
- **Initial State**: Continue from Open IPC. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Populate in draft.
- **Inputs**: Selected IPC and operation-specific fields.

## Authorization & Permissions

- **Required Permissions**: edit_ipcs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: populateIPC mutation.
- **State Change**: Draft quantities/line data recalculate.
- **Navigation**: `/projects/:projectId/ipcs/:ipcId`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Server status validation is authoritative; a visible control does not guarantee acceptance.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open IPC](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-ipc-detail.tsx](../../../../../../../../apps/web/src/app/routes/project-ipc-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/components/contracts/IPCWorkflowBar.tsx](../../../../../../../../apps/web/src/components/contracts/IPCWorkflowBar.tsx)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/api/core/contracts/collection_views.py](../../../../../../../../apps/api/core/contracts/collection_views.py)

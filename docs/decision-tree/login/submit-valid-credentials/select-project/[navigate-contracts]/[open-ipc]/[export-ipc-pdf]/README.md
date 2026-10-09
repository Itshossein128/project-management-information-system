# Decision: Export IPC PDF

## Context & Screen

- **Route**: `/projects/:projectId/ipcs/:ipcId`
- **Component**: `ProjectIPCDetailPage`
- **Initial State**: Continue from Open IPC. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click PDF.
- **Inputs**: IPC ID.

## Authorization & Permissions

- **Required Permissions**: view_ipcs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET downloadIPCPdf.
- **State Change**: Browser downloads the statement.
- **Navigation**: `/projects/:projectId/ipcs/:ipcId`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open IPC](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-ipc-detail.tsx](../../../../../../../../apps/web/src/app/routes/project-ipc-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/components/contracts/IPCWorkflowBar.tsx](../../../../../../../../apps/web/src/components/contracts/IPCWorkflowBar.tsx)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)

# Decision: Open IPC

## Context & Screen

- **Route**: `/projects/:projectId/ipcs/:ipcId`
- **Component**: `ProjectIPCDetailPage`
- **Initial State**: Continue from Contracts. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click an IPC row or finish the IPC wizard.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_ipcs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchIPC.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/ipcs/:ipcId`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Populate draft IPC](%5Bpopulate-ipc%5D/README.md)
- [Edit IPC quantities](%5Bedit-line-items%5D/README.md)
- [Manage IPC deductions](%5Bmanage-deductions%5D/README.md)
- [Submit draft IPC](%5Bsubmit-ipc%5D/README.md)
- [Approve submitted IPC](%5Bapprove-ipc%5D/README.md)
- [Reject submitted IPC](%5Breject-ipc%5D/README.md)
- [Mark approved IPC paid](%5Bmark-ipc-paid%5D/README.md)
- [Record IPC collection](%5Brecord-collection%5D/README.md)
- [Export IPC PDF](%5Bexport-ipc-pdf%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Contracts](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-ipc-detail.tsx](../../../../../../../apps/web/src/app/routes/project-ipc-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../apps/web/src/app/lib/api/contracts.ts)

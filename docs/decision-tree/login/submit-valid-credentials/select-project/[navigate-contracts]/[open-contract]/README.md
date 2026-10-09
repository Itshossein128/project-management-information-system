# Decision: Open contract

## Context & Screen

- **Route**: `/projects/:projectId/contracts/:contractId`
- **Component**: `ProjectContractDetailPage`
- **Initial State**: Continue from Contracts. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a contract row.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_contracts
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchContract.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/contracts/:contractId`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Edit contract](%5Bedit-contract%5D/README.md)
- [Edit BoQ items](%5Bsave-boq%5D/README.md)
- [Create contract change order](%5Bcreate-change-order%5D/README.md)
- [Approve contract change order](%5Bapprove-change-order%5D/README.md)
- [Create IPC](%5Bcreate-ipc%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Contracts](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-contract-detail.tsx](../../../../../../../apps/web/src/app/routes/project-contract-detail.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../apps/web/src/app/lib/api/contracts.ts)

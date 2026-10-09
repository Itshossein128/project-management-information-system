# Decision: Sync conflicts

## Context & Screen

- **Route**: `/projects/:projectId/sync-conflicts`
- **Component**: `SyncConflictsPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None on initial load: read getUnresolvedConflicts and getFailedQueue from IndexedDB.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/sync-conflicts`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration.

## Subsequent Decisions

- [Resolve a synchronization conflict](%5Bresolve-conflict%5D/README.md)
- [Retry a failed queued item](retry-failed-item/README.md)
- [Discard failed queued item](discard-failed-item/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/sync-conflicts.tsx](../../../../../../apps/web/src/app/routes/sync-conflicts.tsx)

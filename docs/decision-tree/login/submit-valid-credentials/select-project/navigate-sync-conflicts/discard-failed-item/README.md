# Decision: Discard failed queued item

## Context & Screen

- **Route**: `/projects/:projectId/sync-conflicts`
- **Component**: `SyncConflictsPage`
- **Initial State**: Continue from Sync conflicts. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Delete on a failed queue row.
- **Inputs**: Queue ID.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: discardFailedQueueItem; local queue update.
- **State Change**: Queued unsynchronized change is discarded and failed list reloads.
- **Navigation**: `/projects/:projectId/sync-conflicts`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Sync conflicts](../README.md)

## Source Evidence

- [apps/web/src/app/routes/sync-conflicts.tsx](../../../../../../../apps/web/src/app/routes/sync-conflicts.tsx)
- [apps/web/src/app/lib/syncService.ts](../../../../../../../apps/web/src/app/lib/syncService.ts)

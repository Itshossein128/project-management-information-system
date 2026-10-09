# Decision: Keep server version

## Context & Screen

- **Route**: `/projects/:projectId/sync-conflicts`
- **Component**: `SyncConflictsPage`
- **Initial State**: Continue from Resolve a synchronization conflict. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose Server and Apply.
- **Inputs**: Conflict and selected/merged payload.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; resolveConflict + removeQueueItem in IndexedDB.
- **State Change**: Local unsynchronized write is discarded; conflict marked resolved_server.
- **Navigation**: `/projects/:projectId/sync-conflicts`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Sync conflicts](../../README.md)
- [Daily reports](../../../%5Bnavigate-daily-reports%5D/README.md)

## Source Evidence

- [apps/web/src/app/routes/sync-conflicts.tsx](../../../../../../../../apps/web/src/app/routes/sync-conflicts.tsx)
- [apps/web/src/components/daily_reports/ConflictCard.tsx](../../../../../../../../apps/web/src/components/daily_reports/ConflictCard.tsx)

# Decision: Merge versions

## Context & Screen

- **Route**: `/projects/:projectId/sync-conflicts`
- **Component**: `SyncConflictsPage`
- **Initial State**: Continue from Resolve a synchronization conflict. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose Merge, set field values in the merge dialog and Save.
- **Inputs**: Conflict and selected/merged payload.

## Authorization & Permissions

- **Required Permissions**: Original endpoint write permission
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: PATCH/POST original queue endpoint.
- **State Change**: Accepted merged write marks resolved_merged and removes queued item.
- **Navigation**: `/projects/:projectId/sync-conflicts`
- **UI Feedback**: Success updates the visible state. An unsuccessful request shows the handler’s error feedback and does not take the success navigation.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Sync conflicts](../../README.md)
- [Daily reports](../../../%5Bnavigate-daily-reports%5D/README.md)

## Source Evidence

- [apps/web/src/app/routes/sync-conflicts.tsx](../../../../../../../../apps/web/src/app/routes/sync-conflicts.tsx)
- [apps/web/src/components/daily_reports/ConflictCard.tsx](../../../../../../../../apps/web/src/components/daily_reports/ConflictCard.tsx)

# Decision: Resolve a synchronization conflict

## Context & Screen

- **Route**: `/projects/:projectId/sync-conflicts`
- **Component**: `SyncConflictsPage`
- **Initial State**: Continue from Sync conflicts. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select local/server values in ConflictCard and apply.
- **Inputs**: Conflicting fields and chosen values.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; original mutation endpoint permissions apply.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Choosing server removes the queue item locally; local/merge calls the stored endpoint with PATCH when stored method is PATCH, otherwise POST.
- **State Change**: Accepted chosen resolution marks the conflict resolved and removes the queued write; server choice needs no API mutation. Last visible resolved conflict navigates to daily report list.
- **Navigation**: `/projects/:projectId/sync-conflicts`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Keep server version](keep-server/README.md)
- [Keep local version](%5Bkeep-local%5D/README.md)
- [Merge versions](%5Bmerge-fields%5D/README.md)

Continue / return links (the same state is documented once):

- [Sync conflicts](../README.md)
- [Daily reports](../../%5Bnavigate-daily-reports%5D/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/sync-conflicts.tsx](../../../../../../../apps/web/src/app/routes/sync-conflicts.tsx)
- [apps/web/src/components/daily_reports/ConflictCard.tsx](../../../../../../../apps/web/src/components/daily_reports/ConflictCard.tsx)

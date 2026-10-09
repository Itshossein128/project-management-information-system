# Decision: Delete a daily report

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports`
- **Component**: `DailyReportsListPage`
- **Initial State**: Continue from Daily reports. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Delete on an eligible report and confirm; cancel keeps it.
- **Inputs**: Report ID.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: DELETE deleteDailyReport; local-only deletion uses the offline database handler.
- **State Change**: Report list refreshes after the appropriate deletion.
- **Navigation**: `/projects/:projectId/daily-reports`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Daily reports](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-reports-list.tsx](../../../../../../../apps/web/src/app/routes/daily-reports-list.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

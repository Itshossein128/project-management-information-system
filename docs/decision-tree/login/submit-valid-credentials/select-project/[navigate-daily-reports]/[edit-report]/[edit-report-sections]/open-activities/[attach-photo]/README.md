# Decision: Attach activity photo

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/edit`
- **Component**: `DailyReportEditPage`
- **Initial State**: Continue from Activities section. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose a photo file in the activity row.
- **Inputs**: File and activity row.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; project membership for storage URL; edit_reports for saving row
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: uploadProjectFile requests upload URL, PUTs file, then confirms; offline savePendingPhoto stores bytes for later synchronization.
- **State Change**: Online file ID or pending local photo reference is attached to row; the row still needs saving.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/edit`
- **UI Feedback**: Success updates the visible state. An unsuccessful request shows the handler’s error feedback and does not take the success navigation.

## Outcomes & Guards

Storage must be available. files.ts uses literal /api/v1 paths with apiJson, while API_BASE defaults to an /api base; URL assembly can duplicate /api. This flow is source-mapped but not verified as a working upload.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Activities section](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form-edit.tsx](../../../../../../../../../../apps/web/src/app/routes/daily-report-form-edit.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/components/daily_reports/ActivityTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/ActivityTab.tsx)
- [apps/web/src/components/daily_reports/InlineGridTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/InlineGridTab.tsx)
- [apps/web/src/app/lib/api/files.ts](../../../../../../../../../../apps/web/src/app/lib/api/files.ts)
- [apps/api/core/storage/views.py](../../../../../../../../../../apps/api/core/storage/views.py)

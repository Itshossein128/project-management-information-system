# Decision: Save report header

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/edit`
- **Component**: `DailyReportEditPage`
- **Initial State**: Continue from Edit daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Fill header and click Save; changing a dated header also starts the 900 ms autosave.
- **Inputs**: Date, weather, temperatures, notes and header values.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Online: createDailyReport / updateDailyReport. Offline: useDailyReportForm.saveHeader writes IndexedDB and sync queue.
- **State Change**: New report gets server/local ID and opens its edit URL; existing report remains on edit. Offline toast means locally saved.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/edit`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Offline save is not server acceptance. Workflow submit/review/approve/reject uses network calls. Autosave errors are silent; manual Save surfaces its error.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Edit daily report](../README.md)
- [Daily reports](../../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form-edit.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-form-edit.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/hooks/useDailyReportForm.ts](../../../../../../../../apps/web/src/app/hooks/useDailyReportForm.ts)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

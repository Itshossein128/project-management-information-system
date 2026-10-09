# Decision: Submit daily report

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportViewPage`
- **Initial State**: Continue from View daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click submit on ApprovalStatusBar; confirm rejection reason when applicable.
- **Inputs**: Report in draft/rejected; rejection reason at least 10 characters when required.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST submitReport.
- **State Change**: Report becomes submitted; report query refreshes; submission warnings can be displayed.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/view`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The visible submit button follows report status; backend edit_reports still applies. No successful transition is promised while offline.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [View daily report](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-view.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-view.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/ApprovalStatusBar.tsx](../../../../../../../../apps/web/src/components/daily_reports/ApprovalStatusBar.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/api/core/field_reports/services/__init__.py](../../../../../../../../apps/api/core/field_reports/services/__init__.py)

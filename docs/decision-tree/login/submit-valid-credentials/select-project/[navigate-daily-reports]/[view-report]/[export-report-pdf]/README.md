# Decision: Export daily report PDF

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportViewPage`
- **Initial State**: Continue from View daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export PDF.
- **Inputs**: Report ID.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET fetchReportPdf.
- **State Change**: Browser downloads the report PDF.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/view`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [View daily report](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-view.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-view.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../../apps/web/src/app/lib/api/activities.ts)

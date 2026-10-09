# Decision: Inspect report versions

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportViewPage`
- **Initial State**: Continue from View daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Versions and choose a listed version.
- **Inputs**: Report ID/version.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchReportVersions.
- **State Change**: Version history appears; selecting a version opens the report view.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/view`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [View daily report](../README.md)
- [View daily report](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-view.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-view.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/ApprovalStatusBar.tsx](../../../../../../../../apps/web/src/components/daily_reports/ApprovalStatusBar.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../../apps/web/src/app/lib/api/activities.ts)

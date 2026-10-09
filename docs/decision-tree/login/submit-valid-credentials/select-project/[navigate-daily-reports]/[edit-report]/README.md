# Decision: Edit daily report

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/edit`
- **Component**: `DailyReportEditPage`
- **Initial State**: Continue from Daily reports. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Edit on a draft/rejected current report.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: edit_reports; editable status draft/rejected
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchDailyReport.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/edit`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Save report header](%5Bsave-report-header%5D/README.md)
- [Edit report sections](%5Bedit-report-sections%5D/README.md)
- [Submit daily report](%5Bsubmit-report%5D/README.md)
- [Review daily report](%5Breview-report%5D/README.md)
- [Approve daily report](%5Bapprove-report%5D/README.md)
- [Reject daily report](%5Breject-report%5D/README.md)
- [Request correction of locked report](%5Brequest-correction%5D/README.md)
- [Inspect report versions](inspect-report-versions/README.md)

Continue / return links (the same state is documented once):

- [Daily reports](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/daily-report-form-edit.tsx](../../../../../../../apps/web/src/app/routes/daily-report-form-edit.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../apps/api/core/field_reports/daily_report_views.py)

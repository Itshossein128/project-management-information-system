# Decision: Create daily report

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/new`
- **Component**: `DailyReportNewPage`
- **Initial State**: Continue from Daily reports. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click New Report.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/daily-reports/new`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Save report header](%5Bsave-report-header%5D/README.md)
- [Edit report sections](%5Bedit-report-sections%5D/README.md)

Continue / return links (the same state is documented once):

- [Daily reports](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/daily-report-form.tsx](../../../../../../../apps/web/src/app/routes/daily-report-form.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../apps/api/core/field_reports/daily_report_views.py)

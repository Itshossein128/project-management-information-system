# Decision: Concrete section

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/new`
- **Component**: `DailyReportNewPage`
- **Initial State**: Continue from Edit report sections. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the concrete tab.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None for tab selection; tab data comes from the saved report.
- **State Change**: Selected section is visible.
- **Navigation**: `/projects/:projectId/daily-reports/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Add concrete row](%5Badd-row%5D/README.md)
- [Edit concrete row](%5Bedit-row%5D/README.md)
- [Delete concrete row](%5Bdelete-row%5D/README.md)
- [Retry row synchronization](retry-row-sync/README.md)

Continue / return links (the same state is documented once):

- [Edit report sections](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form.tsx](../../../../../../../../../apps/web/src/app/routes/daily-report-form.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/components/daily_reports/ConcreteTab.tsx](../../../../../../../../../apps/web/src/components/daily_reports/ConcreteTab.tsx)
- [apps/web/src/components/daily_reports/InlineGridTab.tsx](../../../../../../../../../apps/web/src/components/daily_reports/InlineGridTab.tsx)

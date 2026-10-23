# Decision: Open daily report summary by date

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports` → ensure by date → `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportsListPage` (`daily-report-open-by-date`) → `DailyReportViewPage`
- **Initial State**: Continue from Daily reports.

## Action Taken

- **Trigger**: Pick a Jalali date and click «نمایش گزارش روز» (or equivalent open-by-date control).
- **Inputs**: `:projectId`, selected `report_date`

## Authorization & Permissions

- **Required Permissions**: `view_reports`
- **Required Roles / Groups**: Project roles and member overrides
- **Protection notation**: Parent `[navigate-daily-reports]` is permission-gated; this child is not separately bracketed.

## Desired Result

- **API Call**: `GET/POST /api/v1/projects/:projectId/daily-reports/by-date/?date=`
- **State Change**: Ensures auto-summary shell for that date, rebuilds from specialty contributions when needed.
- **Navigation**: Summary view for the ensured report id
- **UI Feedback**: Excel-like sectional summary; incompleteness banner when partial

## Outcomes & Guards

Ensuring the daily report by date validates project membership and date parameter. If a summary already exists, it is loaded; if not, an empty or rebuilt summary is created.

## Subsequent Decisions

- [View daily report](../%5Bview-report%5D/README.md)
- [Synchronize queued reports](../%5Bsync-now%5D/README.md)
- [Discipline subreports](../../%5Bnavigate-sub-reports%5D/README.md)

Continue / return:

- [Daily reports](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-reports-list.tsx](../../../../../../../apps/web/src/app/routes/daily-reports-list.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

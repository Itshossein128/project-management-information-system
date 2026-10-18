# Decision: Create daily report (superseded)

## Status

**Superseded** by auto daily-report summary (`028-auto-daily-report-summary`).

Project-level blank «گزارش جدید» / `/daily-reports/new` is retired. Authoring is specialty-unit (رشته) reports; the project daily report is an auto-rebuilt summary opened by date.

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/new` (redirects to list)
- **Component**: Redirect → `DailyReportsListPage`
- **Initial State**: Continue from Daily reports.

## Action Taken

- **Trigger**: Legacy New Report control or direct URL to `/daily-reports/new`.
- **Inputs**: `:projectId`

## Authorization & Permissions

- **Required Permissions**: `edit_reports` (historical; create control removed from list)
- **Protection notation**: Directory remains bracketed for historical inventory.

## Desired Result

- **API Call**: None for blank create. Use `GET/POST .../daily-reports/by-date/?date=` to ensure summary, or specialty `POST .../sub-reports/`.
- **State Change**: Redirect to daily reports list.
- **Navigation**: `/projects/:projectId/daily-reports`
- **UI Feedback**: No blank create form.

## Subsequent Decisions

Prefer:

- [Open summary by date](../open-by-date/README.md)
- [View daily report](../%5Bview-report%5D/README.md)
- [Discipline subreports](../../%5Bnavigate-sub-reports%5D/README.md)

Continue / return:

- [Daily reports](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-reports-list.tsx](../../../../../../../apps/web/src/app/routes/daily-reports-list.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../apps/api/core/field_reports/daily_report_views.py)

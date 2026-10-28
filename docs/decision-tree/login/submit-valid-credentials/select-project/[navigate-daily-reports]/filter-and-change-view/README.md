# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports` and `/projects/:projectId/activity-log`
- **Component**: `DailyReportsListPage` (`apps/web/src/app/routes/daily-reports-list.tsx`) and `ProjectActivityLogPage` (`apps/web/src/app/routes/project-activity-log.tsx`)
- **Initial State**: Continue from Daily reports. This node describes the state reached by changing active filters or view parameters.

## Action Taken

- **Trigger**: Change filter inputs (Jalali date range `date_from`/`date_to`, status, discipline, parcel, zone, block, subcontractor) or pagination (`page`).
- **Inputs**: Filter values or pagination index.

## Authorization & Permissions

- **Required Permissions**: `view_reports` (inherited from parent daily reports screen).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; parent screen gate applies.

## Desired Result

- **State Persistence**: All filter parameters and pagination are synchronized with browser URL query parameters via `useSearchParams`:
  - `?page=1&date_from=1403-11-01&date_to=1403-11-30&status=approved`
  - `?discipline=civil,electrical&parcel=p1&zone=z1&block=b1&subcontractor=XYZ&page=2`
  - Filter state is deep-linkable, refresh-safe, and bookmarks preserve the active search view.
- **API Call**: `GET fetchDailyReports` or `GET fetchActivityLog` with the active search parameters.
- **State Change**: Filtered table rows and aggregate summary metrics (total man-days and volumes grouped by measurement unit) update reactively.
- **Export Action**: Option to export flat historical cumulative database via "خروجی اکسل دیتابیس جامع فعالیت‌ها (FILE 1)" calling `GET /api/v1/projects/:projectId/activity-log/excel/`.
- **Navigation**: Query parameters update on `/projects/:projectId/daily-reports` or `/projects/:projectId/activity-log`.
- **UI Feedback**: Table and summary metrics re-render with the filtered slice.

## Outcomes & Guards

Loading, empty results, and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Daily reports](../README.md)
- [View daily report](../%5Bview-report%5D/README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-reports-list.tsx](../../../../../../../apps/web/src/app/routes/daily-reports-list.tsx)
- [apps/web/src/app/routes/project-activity-log.tsx](../../../../../../../apps/web/src/app/routes/project-activity-log.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/api/core/field_reports/report_views.py](../../../../../../../apps/api/core/field_reports/report_views.py)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

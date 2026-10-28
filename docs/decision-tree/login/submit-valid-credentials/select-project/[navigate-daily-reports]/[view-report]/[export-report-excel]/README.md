# Decision: Export daily report Excel (FILE 4)

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportViewPage` (`apps/web/src/app/routes/daily-report-view.tsx`)
- **Initial State**: Continue from View daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click "خروجی اکسل (FILE 4)" / Export Excel.
- **Inputs**: `:projectId`, `:reportId`.

## Authorization & Permissions

- **Required Permissions**: `view_reports`
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets `[export-report-excel]`.

## Desired Result

- **API Call**: `GET /api/v1/projects/:projectId/daily-reports/:reportId/excel/` via `fetchReportExcel`.
- **State Change**: Browser downloads the generated workbook attachment named `daily-report-{report_date}-{shift}.xlsx`.
- **Workbook Structure**:
  - Right-to-Left (RTL) worksheet layout (`ws.sheet_view.rightToLeft = True`).
  - Font: Tahoma.
  - Rows 1–8: Comprehensive Persian project header (project name, contract number, Jalali date, day of week, weather conditions, shift hours).
  - Indirect Labor Section: All 34 standard Shiraz FILE 4 roles with subtotal formula `=SUM(F11:F44)`.
  - Direct Labor Section: All 32 standard Shiraz FILE 4 worker types with subtotal formula `=SUM(F48:F79)`.
  - Grand Total Row: Formula summing indirect and direct subtotals.
  - Materials, concrete pouring logs, machinery/equipment table, and executed site activities table.
- **Navigation**: Remains on `/projects/:projectId/daily-reports/:reportId/view`.
- **UI Feedback**: Button shows downloading state, file is downloaded or error toast is shown.

## Outcomes & Guards

Guarded by `canView` (`has("view_reports")`) in frontend and `HasProjectPermission('view_reports')` on the backend viewset action.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [View daily report](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-view.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-view.tsx)
- [apps/api/core/field_reports/shiraz_file4_excel.py](../../../../../../../../apps/api/core/field_reports/shiraz_file4_excel.py)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

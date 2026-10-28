# Decision: Download weekly activity report

## Context & Screen

- **Route**: `/projects/:businessId/machinery`
- **Component**: `DepartmentPage`
- **Initial State**: The authenticated user is viewing the Machinery department activity screen.

## Action Taken

- **Trigger**: Choose a Saturday week start and click Download Weekly Report.
- **Inputs**: Department, current filters, and the selected workbook date/range where applicable.

## Authorization & Permissions

- **Required Permissions**: Standard authenticated project member with the normal read/assignment guards; no special write permission.
- **Required Roles / Groups**: Project membership and the standard project-assignment guards.
- **Protection notation**: Standard authenticated action; directory is unbracketed.

## Desired Result

- **API Call**: GET `/api/v1/projects/:businessId/department-activity-records/reports/weekly/?department=machinery&week_start=YYYY-MM-DD` downloads eight RTL worksheets with native `=SUM(...)` formulas and clean empty days.
- **State Change**: The workbook download completes; imports refresh the table only after an atomic success and display row-level failures otherwise.
- **Navigation**: `/projects/:businessId/machinery`
- **UI Feedback**: Download feedback or localized validation errors are shown by `DepartmentPage`.
- **Resulting Route / Screen**: Remain on `/projects/:businessId/machinery`; the workbook is downloaded.

## Resulting Route / Screen

- **Route**: `/projects/:businessId/machinery`

## Outcomes & Guards

Empty result sets are valid and produce clean workbook structures. Invalid dates, filters, permissions, or workbook rows return the endpoint’s documented error without an unintended state change.

## Subsequent Decisions

- [Return to Machinery department activity](../README.md)

## Source Evidence

- [../../../../../../../apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)
- [../../../../../../../apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)

# Decision: Download daily activity report

## Context & Screen

- **Route**: `/projects/:businessId/warehouse`
- **Component**: `DepartmentPage`
- **Initial State**: The authenticated user is viewing the Warehouse department activity screen.

## Action Taken

- **Trigger**: Choose a report date and click "دانلود گزارش روزانه انبار (شیراز)" (Download Daily Report).
- **Inputs**: Department (`warehouse`), current filters, and the selected report date (`YYYY-MM-DD`).

## Authorization & Permissions

- **Required Permissions**: `view_reports` alongside standard authenticated project membership (`IsProjectMember`, `HasProjectPermission`, `CanViewBusinessAssignments`).
- **Required Roles / Groups**: Project membership and standard project-assignment guards.
- **Protection notation**: Standard authenticated action; directory is unbracketed.

## Desired Result

- **API Call**: GET `/api/v1/projects/:businessId/department-activity-records/reports/daily/?department=warehouse&date=YYYY-MM-DD` downloads the Shiraz-standard RTL `.xlsx` workbook featuring:
  - Header Banner: `گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}`
  - Tier 1 Summary: Total Inbound (`=SUM(D5:D{n})`) and Total Outbound (`=SUM(F5:F{n})`)
  - Tier 2 Summary: Net Daily Balance («تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):») with native formula `=D{sum_row}-F{sum_row}`.
- **State Change**: The workbook download completes; imports refresh the table only after an atomic success and display row-level failures otherwise.
- **Navigation**: `/projects/:businessId/warehouse`
- **UI Feedback**: Download feedback or localized validation errors are shown by `DepartmentPage`.
- **Resulting Route / Screen**: Remain on `/projects/:businessId/warehouse`; the workbook is downloaded.

## Resulting Route / Screen

- **Route**: `/projects/:businessId/warehouse`

## Outcomes & Guards

Empty result sets are valid and produce clean workbook structures. Invalid dates, filters, permissions, or workbook rows return the endpoint’s documented error without an unintended state change.

## Subsequent Decisions

- [Return to Warehouse department activity](../README.md)

## Source Evidence

- [../../../../../../../apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)
- [../../../../../../../apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)

# Decision: Download weekly activity report

## Context & Screen

- **Route**: `/projects/:businessId/warehouse`
- **Component**: `DepartmentPage`
- **Initial State**: The authenticated user is viewing the Warehouse department activity screen.

## Action Taken

- **Trigger**: Choose a Saturday week start date and click "دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)" (Download Weekly Report).
- **Inputs**: Department (`warehouse`), current filters, and the selected Saturday `week_start` date.

## Authorization & Permissions

- **Required Permissions**: `view_reports` alongside standard authenticated project membership (`IsProjectMember`, `HasProjectPermission`, `CanViewBusinessAssignments`).
- **Required Roles / Groups**: Project membership and standard project-assignment guards.
- **Protection notation**: Standard authenticated action; directory is unbracketed.

## Desired Result

- **API Call**: GET `/api/v1/projects/:businessId/department-activity-records/reports/weekly/?department=warehouse&week_start=YYYY-MM-DD` downloads an 8-worksheet RTL Excel workbook (.xlsx):
  - Sheets 1 to 7: Daily activity sheets for Saturday through Friday.
  - Sheet 8: **Cumulative Material Balance Sheet** («بالانس تجمعی مصالح») aggregating movements by `(material_type, unit)`:
    - Column A: ردیف (Row index)
    - Column B: نوع مصالح (Material Type)
    - Column C: واحد (Unit)
    - Column D: موجودی اول دوره (Opening balance before `week_start`)
    - Column E: کل ورودی دوره (Total weekly inbound)
    - Column F: کل خروجی دوره (Total weekly outbound)
    - Column G: مانده پای کار / موجودی پایان دوره (Closing balance with native formula `=D{row}+E{row}-F{row}`)
    - Column H: توضیحات و وضعیت اقلام (Item notes/status)
    - Summary Row: Native `=SUM(...)` formulas for Opening Balance, Inbound, Outbound, and Closing Balance.
  - Materials with historical balances prior to the week appear even if zero transactions took place during the week.
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

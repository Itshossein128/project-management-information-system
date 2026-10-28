# Decision: Import department activities

## Context & Screen

- **Route**: `/projects/:businessId/electrical`
- **Component**: `DepartmentPage`
- **Initial State**: The authenticated user is viewing the Electrical department activity screen.

## Action Taken

- **Trigger**: Choose Import Excel and submit an `.xlsx` workbook.
- **Inputs**: Department, current filters, and the selected workbook date/range where applicable.

## Authorization & Permissions

- **Required Permissions**: edit_reports (plus authenticated project membership and standard project-assignment guards).
- **Required Roles / Groups**: Project membership and the standard project-assignment guards.
- **Protection notation**: Special permission gate; directory uses brackets.

## Desired Result

- **API Call**: Multipart POST `/api/v1/projects/:businessId/department-activity-records/import-excel/?department=electrical` validates every row atomically and returns Persian row errors with zero rows committed on failure.
- **State Change**: The workbook download completes; imports refresh the table only after an atomic success and display row-level failures otherwise.
- **Navigation**: `/projects/:businessId/electrical`
- **UI Feedback**: Download feedback or localized validation errors are shown by `DepartmentPage`.
- **Resulting Route / Screen**: Remain on `/projects/:businessId/electrical` with the grid refreshed after success or the row error displayed after failure.

## Resulting Route / Screen

- **Route**: `/projects/:businessId/electrical`

## Outcomes & Guards

Empty result sets are valid and produce clean workbook structures. Invalid dates, filters, permissions, or workbook rows return the endpoint’s documented error without an unintended state change.

## Subsequent Decisions

- [Return to Electrical department activity](../README.md)

## Source Evidence

- [../../../../../../../apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)
- [../../../../../../../apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)

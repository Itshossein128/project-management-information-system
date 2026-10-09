# Decision: Import department activity records

## Context & Screen

- **Route**: `/projects/:businessId/warehouse`
- **Component**: `BusinessWarehouseRoute`
- **Initial State**: Continue from Warehouse department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Import Excel and choose file.
- **Inputs**: Workbook and department.

## Authorization & Permissions

- **Required Permissions**: view_reports plus CanViewBusinessAssignments, IsHrOrAdminOrReadOnly, IsVisitorReadOnly
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Multipart POST department-activity-records/import/.
- **State Change**: Import result reports created rows and row errors; any created rows trigger refresh.
- **Navigation**: `/projects/:businessId/warehouse`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Warehouse department activity](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/business-warehouse.tsx](../../../../../../../apps/web/src/app/routes/business-warehouse.tsx)
- [apps/api/core/inventory/views.py](../../../../../../../apps/api/core/inventory/views.py)
- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)

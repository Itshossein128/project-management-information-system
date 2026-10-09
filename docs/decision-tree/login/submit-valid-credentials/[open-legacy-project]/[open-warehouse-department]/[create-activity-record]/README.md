# Decision: Create department activity record

## Context & Screen

- **Route**: `/projects/:businessId/warehouse`
- **Component**: `BusinessWarehouseRoute`
- **Initial State**: Continue from Warehouse department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Add and submit DepartmentActivityRecordModal.
- **Inputs**: Department-specific date/location/quantity/description fields.

## Authorization & Permissions

- **Required Permissions**: CanViewBusinessAssignments, IsHrOrAdminOrReadOnly, IsVisitorReadOnly
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST useCreateDepartmentActivityRecord.
- **State Change**: Record saves and query invalidates.
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
- [apps/web/src/components/department/department-activity-record-modal.tsx](../../../../../../../apps/web/src/components/department/department-activity-record-modal.tsx)
- [apps/web/src/app/hooks/queries.ts](../../../../../../../apps/web/src/app/hooks/queries.ts)

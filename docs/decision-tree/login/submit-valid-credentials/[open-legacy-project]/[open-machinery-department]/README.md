# Decision: Machinery department activity

## Context & Screen

- **Route**: `/projects/:businessId/machinery`
- **Component**: `BusinessMachineryRoute`
- **Initial State**: Continue from Open legacy project area. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose legacy department tile/link.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: CanViewBusinessAssignments for reads; mutation policy IsHrOrAdminOrReadOnly + IsVisitorReadOnly
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through useDepartmentActivityRecordsQuery.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId/machinery`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

DepartmentPage consumes :businessId. Warehouse uses material/consumption/supplier fields; other departments use activity/location/contractor fields. Export/report/import APIs additionally require view_reports; legacy CRUD does not use an edit_reports codename check.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create department activity record](%5Bcreate-activity-record%5D/README.md)
- [Import department activity records](%5Bimport-activity-excel%5D/README.md)
- [Download export workbook](%5Bexport-report%5D/README.md)
- [Download daily workbook](%5Bdaily-report%5D/README.md)
- [Download weekly workbook](%5Bweekly-report%5D/README.md)

Continue / return links (the same state is documented once):

- [Open legacy project area](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-machinery.tsx](../../../../../../apps/web/src/app/routes/business-machinery.tsx)
- [apps/api/core/inventory/views.py](../../../../../../apps/api/core/inventory/views.py)
- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/web/src/components/department/department-page.tsx](../../../../../../apps/web/src/components/department/department-page.tsx)

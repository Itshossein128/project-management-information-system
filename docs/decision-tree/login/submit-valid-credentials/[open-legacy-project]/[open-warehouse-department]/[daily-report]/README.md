# Decision: Download daily workbook

## Context & Screen

- **Route**: `/projects/:businessId/warehouse`
- **Component**: `BusinessWarehouseRoute`
- **Initial State**: Continue from Warehouse department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Daily Report.
- **Inputs**: Current filters.

## Authorization & Permissions

- **Required Permissions**: view_reports plus CanViewBusinessAssignments
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET department-activity-records/reports/daily/
- **State Change**: Workbook downloads; no source records change.
- **Navigation**: `/projects/:businessId/warehouse`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Warehouse department activity](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-warehouse.tsx](../../../../../../../apps/web/src/app/routes/business-warehouse.tsx)
- [apps/api/core/inventory/views.py](../../../../../../../apps/api/core/inventory/views.py)
- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)

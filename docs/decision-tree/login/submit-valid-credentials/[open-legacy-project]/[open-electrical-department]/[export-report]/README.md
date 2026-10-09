# Decision: Download export workbook

## Context & Screen

- **Route**: `/projects/:businessId/electrical`
- **Component**: `BusinessElectricalRoute`
- **Initial State**: Continue from Electrical department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export Excel.
- **Inputs**: Current filters.

## Authorization & Permissions

- **Required Permissions**: view_reports plus CanViewBusinessAssignments
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET department-activity-records/export/
- **State Change**: Workbook downloads; no source records change.
- **Navigation**: `/projects/:businessId/electrical`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Electrical department activity](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-electrical.tsx](../../../../../../../apps/web/src/app/routes/business-electrical.tsx)
- [apps/api/core/inventory/views.py](../../../../../../../apps/api/core/inventory/views.py)
- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)

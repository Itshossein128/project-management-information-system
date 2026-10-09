# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:businessId/mechanical`
- **Component**: `BusinessMechanicalRoute`
- **Initial State**: Continue from Mechanical department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Search, page/sort and select date/location/activity/contractor filters; warehouse substitutes material/supplier/consumption-location filters.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET useDepartmentActivityRecordsQuery.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:businessId/mechanical`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Mechanical department activity](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-mechanical.tsx](../../../../../../../apps/web/src/app/routes/business-mechanical.tsx)
- [apps/api/core/inventory/views.py](../../../../../../../apps/api/core/inventory/views.py)
- [apps/api/core/inventory/department_activity_data_views.py](../../../../../../../apps/api/core/inventory/department_activity_data_views.py)
- [apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)

# Decision: Preview personnel capacity

## Context & Screen

- **Route**: `/projects/:projectId/resource-allocations`
- **Component**: `ProjectResourceAllocationsPage`
- **Initial State**: Continue from Resource allocations. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Complete allocation dates/person/capacity in the form.
- **Inputs**: Person, date range, requested capacity.

## Authorization & Permissions

- **Required Permissions**: view_hr
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: fetchCapacityPreview.
- **State Change**: Committed/available/requested capacity is displayed before save.
- **Navigation**: `/projects/:projectId/resource-allocations`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Resource allocations](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-resource-allocations.tsx](../../../../../../../apps/web/src/app/routes/project-resource-allocations.tsx)
- [apps/api/core/hr/capacity_views.py](../../../../../../../apps/api/core/hr/capacity_views.py)
- [apps/web/src/components/hr/AllocationFormPanel.tsx](../../../../../../../apps/web/src/components/hr/AllocationFormPanel.tsx)
- [apps/web/src/app/lib/api/hr-capacity.ts](../../../../../../../apps/web/src/app/lib/api/hr-capacity.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../apps/web/src/app/lib/api/wbs.ts)

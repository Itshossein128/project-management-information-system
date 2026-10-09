# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/procurement`
- **Component**: `ProcurementListPage`
- **Initial State**: Continue from Procurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Change scope, block, status and date/search filters.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchRequisitions / fetchBlocks.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/procurement`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Procurement](../README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-list.tsx](../../../../../../../apps/web/src/app/routes/procurement/procurement-list.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../apps/web/src/app/lib/api/procurement.ts)

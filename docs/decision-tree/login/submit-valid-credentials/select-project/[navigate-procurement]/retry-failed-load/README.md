# Decision: Retry failed load

## Context & Screen

- **Route**: `/projects/:projectId/procurement`
- **Component**: `ProcurementListPage`
- **Initial State**: Continue from Procurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Retry on the displayed QueryErrorState.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: Refetch the query used by the screen’s onRetry handler.
- **State Change**: Loading state restarts; success or repeated failure determines the rendered content.
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
- [apps/web/src/components/layout/query-error-state.tsx](../../../../../../../apps/web/src/components/layout/query-error-state.tsx)

# Decision: Procurement

## Context & Screen

- **Route**: `/projects/:projectId/procurement`
- **Component**: `ProcurementListPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchRequisitions, fetchBlocks.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/procurement`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create purchase requisition](%5Bcreate-requisition%5D/README.md)
- [Open requisition](%5Bopen-requisition%5D/README.md)
- [Procurement officer dashboard](%5Bopen-officer-dashboard%5D/README.md)
- [Block inventory](%5Bopen-block-inventory%5D/README.md)
- [Procurement reports](%5Bopen-procurement-reports%5D/README.md)
- [Procurement blocks](%5Bmanage-blocks%5D/README.md)
- [Internal stock transfers](%5Bopen-stock-transfers%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)
- [Start screen walkthrough](start-product-tour/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-list.tsx](../../../../../../apps/web/src/app/routes/procurement/procurement-list.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../apps/web/src/app/lib/api/procurement.ts)

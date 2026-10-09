# Decision: Internal stock transfers

## Context & Screen

- **Route**: `/projects/:projectId/procurement/transfers`
- **Component**: `ProcurementTransfersPage`
- **Initial State**: Continue from Procurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Transfers.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_procurement
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchTransfers, fetchBlocks, fetchMaterials.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/procurement/transfers`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Create stock transfer](%5Bcreate-transfer%5D/README.md)
- [Approve stock transfer](%5Bapprove-transfer%5D/README.md)
- [Reject stock transfer](%5Breject-transfer%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)
- [Start screen walkthrough](start-product-tour/README.md)

Continue / return links (the same state is documented once):

- [Procurement](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-transfers.tsx](../../../../../../../apps/web/src/app/routes/procurement/procurement-transfers.tsx)
- [apps/api/core/procurement/views/po_views.py](../../../../../../../apps/api/core/procurement/views/po_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../apps/web/src/app/lib/api/materials.ts)

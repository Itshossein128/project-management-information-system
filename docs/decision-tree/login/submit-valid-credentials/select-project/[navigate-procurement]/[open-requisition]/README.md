# Decision: Open requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/req/:reqId`
- **Component**: `ProcurementDetailPage`
- **Initial State**: Continue from Procurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a requisition number/row.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_procurement; approval log endpoint also requires project membership
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchRequisition, fetchApprovalLogs, fetchMembers.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/procurement/req/:reqId`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Submit requisition](%5Bsubmit-requisition%5D/README.md)
- [Approve requisition](%5Bapprove-requisition%5D/README.md)
- [Return requisition](%5Breturn-requisition%5D/README.md)
- [Reject requisition](%5Breject-requisition%5D/README.md)
- [Partially approve items](%5Bpartially-approve-items%5D/README.md)
- [Assign procurement officers](%5Bassign-officers%5D/README.md)
- [Hold requisition item](%5Bhold-item%5D/README.md)
- [Create commitment from requisition](%5Bcreate-cost-commitment%5D/README.md)
- [Start screen walkthrough](start-product-tour/README.md)

Continue / return links (the same state is documented once):

- [Procurement](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-detail.tsx](../../../../../../../apps/web/src/app/routes/procurement/procurement-detail.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/api/core/procurement/permissions.py](../../../../../../../apps/api/core/procurement/permissions.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)

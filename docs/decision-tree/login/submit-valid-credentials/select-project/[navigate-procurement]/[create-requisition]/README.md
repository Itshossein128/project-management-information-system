# Decision: Create purchase requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/new`
- **Component**: `ProcurementNewPage`
- **Initial State**: Continue from Procurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Block Requisition or Workshop Requisition (?scope=workshop).
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: edit_procurement (backend); edit_reports controls list-page create links
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchBlocks, fetchMaterials.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/procurement/new`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Block scope requires a selected standard block. Workshop scope uses the system workshop block and skips workshop_approval. The frontend list create gate differs from the backend write gate.

## Subsequent Decisions

- [Prepare requisition lines](edit-line-items/README.md)
- [Save requisition](%5Bsave-requisition%5D/README.md)
- [Cancel requisition](cancel-requisition/README.md)
- [Start screen walkthrough](start-product-tour/README.md)

Continue / return links (the same state is documented once):

- [Procurement](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-new.tsx](../../../../../../../apps/web/src/app/routes/procurement/procurement-new.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../apps/web/src/app/lib/api/materials.ts)

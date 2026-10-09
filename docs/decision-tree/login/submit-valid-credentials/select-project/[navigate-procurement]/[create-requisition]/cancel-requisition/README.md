# Decision: Cancel requisition

## Context & Screen

- **Route**: `/projects/:projectId/procurement/new`
- **Component**: `ProcurementNewPage`
- **Initial State**: Continue from Create purchase requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Cancel.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Local selection changes; no server mutation.
- **Navigation**: `/projects/:projectId/procurement`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Procurement](../../README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-new.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-new.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../../apps/web/src/app/lib/api/materials.ts)

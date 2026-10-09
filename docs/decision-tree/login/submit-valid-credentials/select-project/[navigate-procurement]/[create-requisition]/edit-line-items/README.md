# Decision: Prepare requisition lines

## Context & Screen

- **Route**: `/projects/:projectId/procurement/new`
- **Component**: `ProcurementNewPage`
- **Initial State**: Continue from Create purchase requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Add/remove item rows; select material, quantity and displayed details.
- **Inputs**: Scope/header and line values.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; local form state.
- **State Change**: Form line array updates; no requisition saved yet.
- **Navigation**: `/projects/:projectId/procurement/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Create purchase requisition](../README.md)

## Source Evidence

- [apps/web/src/app/routes/procurement/procurement-new.tsx](../../../../../../../../apps/web/src/app/routes/procurement/procurement-new.tsx)
- [apps/api/core/procurement/views/requisition_views.py](../../../../../../../../apps/api/core/procurement/views/requisition_views.py)
- [apps/web/src/app/lib/api/procurement.ts](../../../../../../../../apps/web/src/app/lib/api/procurement.ts)
- [apps/web/src/app/lib/api/materials.ts](../../../../../../../../apps/web/src/app/lib/api/materials.ts)

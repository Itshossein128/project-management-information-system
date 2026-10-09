# Decision: Start screen walkthrough

## Context & Screen

- **Route**: `/projects/:projectId/procurement/new`
- **Component**: `ProcurementNewPage`
- **Initial State**: Continue from Create purchase requisition. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click ProductTourButton.
- **Inputs**: Current screen.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; useProductTour / Driver.js UI state.
- **State Change**: Walkthrough highlights the screen controls; use its Next/Previous/Close controls to continue/dismiss.
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
- [apps/web/src/components/tour/ProductTourButton.tsx](../../../../../../../../apps/web/src/components/tour/ProductTourButton.tsx)
- [apps/web/src/components/tour/useProductTour.ts](../../../../../../../../apps/web/src/components/tour/useProductTour.ts)

# Decision: Export dynamic rows

## Context & Screen

- **Route**: `/projects/:businessId/tables/:tableSlug`
- **Component**: `BusinessTablePage`
- **Initial State**: Continue from Open dynamic table. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export Excel.
- **Inputs**: Table and rows.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; project membership
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Dynamic rows export request.
- **State Change**: Browser downloads workbook; rows remain unchanged.
- **Navigation**: `/projects/:businessId/tables/:tableSlug`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open dynamic table](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-table.tsx](../../../../../../../apps/web/src/app/routes/business-table.tsx)
- [apps/api/core/business_meta/data_views.py](../../../../../../../apps/api/core/business_meta/data_views.py)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)

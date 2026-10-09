# Decision: Open dynamic table

## Context & Screen

- **Route**: `/projects/:businessId/tables/:tableSlug`
- **Component**: `BusinessTablePage`
- **Initial State**: Continue from Open legacy project area. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a table tile or open /projects/:businessId/tables/:tableSlug.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; project membership
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through apiJson schema by_slug and dynamic rows.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId/tables/:tableSlug`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Add dynamic row](%5Badd-row%5D/README.md)
- [Delete dynamic row](%5Bdelete-row%5D/README.md)
- [Import dynamic rows](%5Bimport-excel%5D/README.md)
- [Export dynamic rows](%5Bexport-excel%5D/README.md)

Continue / return links (the same state is documented once):

- [Open legacy project area](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-table.tsx](../../../../../../apps/web/src/app/routes/business-table.tsx)
- [apps/api/core/business_meta/data_views.py](../../../../../../apps/api/core/business_meta/data_views.py)
- [apps/api/core/business_meta/views.py](../../../../../../apps/api/core/business_meta/views.py)

# Decision: Legacy table/field schema setup

## Context & Screen

- **Route**: `/projects/:businessId/setup`
- **Component**: `BusinessSetupSchema`
- **Initial State**: Continue from Open legacy project area. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open legacy setup link or /projects/:businessId/setup.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Frontend IsBusinessSetup; schema mutations IsBusinessSetup
- **Required Roles / Groups**: business-setup for the frontend/schema gate; additional project write permission where stated.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through apiJson table/field definitions.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId/setup`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Create dynamic table](%5Bcreate-table%5D/README.md)
- [Edit dynamic table](%5Bedit-table%5D/README.md)
- [Delete dynamic table](%5Bdelete-table%5D/README.md)
- [Create dynamic field](%5Bcreate-field%5D/README.md)
- [Edit dynamic field](%5Bedit-field%5D/README.md)
- [Delete dynamic field](%5Bdelete-field%5D/README.md)

Continue / return links (the same state is documented once):

- [Open legacy project area](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-setup-schema.tsx](../../../../../../apps/web/src/app/routes/business-setup-schema.tsx)
- [apps/api/core/business_meta/views.py](../../../../../../apps/api/core/business_meta/views.py)

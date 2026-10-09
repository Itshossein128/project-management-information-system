# Decision: Open legacy project area

## Context & Screen

- **Route**: `/projects/:businessId`
- **Component**: `BusinessPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open /projects/:businessId directly or use a legacy project link.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; project membership for project/tables reads
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through apiJson project detail and table definitions.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

This is the legacy project overview, separate from /projects/:projectId/overview. Components still consume BusinessDetail fields; route registration does not prove their compatibility with blueprint ProjectDetail.

## Subsequent Decisions

- [Legacy table/field schema setup](%5Bnavigate-schema-setup%5D/README.md)
- [Open dynamic table](%5Bopen-dynamic-table%5D/README.md)
- [Legacy project members](%5Bopen-legacy-members%5D/README.md)
- [Project job positions](%5Bopen-project-positions%5D/README.md)
- [Buildings department activity](%5Bopen-buildings-department%5D/README.md)
- [Mechanical department activity](%5Bopen-mechanical-department%5D/README.md)
- [Security department activity](%5Bopen-security-department%5D/README.md)
- [Machinery department activity](%5Bopen-machinery-department%5D/README.md)
- [Warehouse department activity](%5Bopen-warehouse-department%5D/README.md)
- [Electrical department activity](%5Bopen-electrical-department%5D/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/business.tsx](../../../../../apps/web/src/app/routes/business.tsx)
- [apps/api/core/business_meta/views.py](../../../../../apps/api/core/business_meta/views.py)

# Decision: Legacy project members

## Context & Screen

- **Route**: `/projects/:businessId/users`
- **Component**: `BusinessUsersPage`
- **Initial State**: Continue from Open legacy project area. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open legacy Users / Team link.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; project membership for list
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through useAssignmentsForBusinessQuery.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId/users`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Inspect legacy assignment](inspect-assignment/README.md)

Continue / return links (the same state is documented once):

- [Open legacy project area](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-users.tsx](../../../../../../apps/web/src/app/routes/business-users.tsx)
- [apps/api/core/projects/member_views.py](../../../../../../apps/api/core/projects/member_views.py)

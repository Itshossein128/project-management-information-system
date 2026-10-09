# Decision: HR users

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from Open HR hub. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Users card.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Frontend admin/hr; backend IsHrOrAdmin
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through useHrUsersQuery / system role list.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/hr/users`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create HR user](%5Bcreate-user%5D/README.md)
- [Import HR users](%5Bimport-users%5D/README.md)
- [Inspect user assignments](%5Binspect-user-assignments%5D/README.md)

Continue / return links (the same state is documented once):

- [Open HR hub](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/hr/users.tsx](../../../../../../apps/web/src/app/routes/hr/users.tsx)
- [apps/api/core/authentication/views.py](../../../../../../apps/api/core/authentication/views.py)
- [apps/api/core/authentication/permissions.py](../../../../../../apps/api/core/authentication/permissions.py)

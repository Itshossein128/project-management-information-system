# Decision: Project-role settings

## Context & Screen

- **Route**: `/settings/roles`
- **Component**: `SettingsRolesPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Roles in global navigation.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Frontend admin/hr; writes IsHrOrAdmin; role list IsAuthenticated
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchProjectRoles, fetchPermissionCatalog.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/settings/roles`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create custom role](%5Bcreate-role%5D/README.md)
- [Save role permissions](%5Bsave-role-permissions%5D/README.md)
- [Delete custom role](%5Bdelete-role%5D/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/settings-roles.tsx](../../../../../apps/web/src/app/routes/settings-roles.tsx)
- [apps/api/core/projects/role_views.py](../../../../../apps/api/core/projects/role_views.py)
- [apps/web/src/app/lib/api/roles.ts](../../../../../apps/web/src/app/lib/api/roles.ts)

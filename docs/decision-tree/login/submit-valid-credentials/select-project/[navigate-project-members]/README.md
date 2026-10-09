# Decision: Project members

## Context & Screen

- **Route**: `/projects/:projectId/settings/members`
- **Component**: `ProjectMembersPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; active project membership for listing/permission reads; manage_members for changes.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchMembers.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/settings/members`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectMembersPage has no usePermission UI gate for Add/Edit/Deactivate. Backend remains authoritative and requires manage_members for writes.

## Subsequent Decisions

- [Add/invite project member](%5Badd-or-invite-member%5D/README.md)
- [Edit member roles](%5Bedit-member%5D/README.md)
- [Deactivate member](%5Bdeactivate-member%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-members.tsx](../../../../../../apps/web/src/app/routes/project-members.tsx)
- [apps/api/core/projects/member_views.py](../../../../../../apps/api/core/projects/member_views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../apps/web/src/app/lib/api/members.ts)

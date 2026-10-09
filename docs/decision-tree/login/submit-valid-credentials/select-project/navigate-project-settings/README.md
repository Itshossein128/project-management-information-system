# Decision: Project settings

## Context & Screen

- **Route**: `/projects/:projectId/settings`
- **Component**: `ProjectSettingsPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; active project membership (or global admin).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchProject, listCapabilities, listFiscalLocks and fetchProjectChangeRequests as mounted.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/settings`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Read-only project details can load with membership. Capability/fiscal-lock/change-request reads additionally require view_project; writes use edit_project. The form’s canEdit check controls editing rather than registering a separate route guard.

## Subsequent Decisions

- [Save project settings](%5Bsave-settings%5D/README.md)
- [Enable/disable capability](%5Btoggle-capability%5D/README.md)
- [Lock fiscal period](%5Bcreate-fiscal-lock%5D/README.md)
- [Delete project](%5Bdelete-project%5D/README.md)
- [Create project change request](%5Bcreate-project-change-request%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-settings.tsx](../../../../../../apps/web/src/app/routes/project-settings.tsx)
- [apps/api/core/projects/views.py](../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/project-core.ts](../../../../../../apps/web/src/app/lib/api/project-core.ts)

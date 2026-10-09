# Decision: WBS

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_wbs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchWBSTree.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration. WBS read API requires view_wbs although the route only computes canEditWBS for editing.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create the first WBS node](%5Bcreate-root-node%5D/README.md)
- [Add a child WBS node](%5Badd-child-node%5D/README.md)
- [Edit a WBS node](%5Bedit-node%5D/README.md)
- [Delete a WBS node](%5Bdelete-node%5D/README.md)
- [Save WBS as a template](%5Bsave-as-template%5D/README.md)
- [Import MSP or P6 schedule](%5Bimport-schedule-file%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../apps/web/src/app/lib/api/wbs.ts)

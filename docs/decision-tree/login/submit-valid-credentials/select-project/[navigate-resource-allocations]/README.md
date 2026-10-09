# Decision: Resource allocations

## Context & Screen

- **Route**: `/projects/:projectId/resource-allocations`
- **Component**: `ProjectResourceAllocationsPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_hr
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchResourceAllocations, fetchCapacityExceptions.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/resource-allocations`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration. Dossier self-read has a membership exception; wages require view_wage/edit_wage separately.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Preview personnel capacity](%5Bpreview-capacity%5D/README.md)
- [Create resource allocation](%5Bcreate-allocation%5D/README.md)
- [Delete resource allocation](%5Bdelete-allocation%5D/README.md)
- [Create capacity exception](%5Bcreate-capacity-exception%5D/README.md)
- [View personnel dossier](%5Bview-person-dossier%5D/README.md)
- [Edit personnel dossier](%5Bedit-person-dossier%5D/README.md)
- [Read labor rates and estimate cost](%5Bview-labor-rates-and-estimate%5D/README.md)
- [Create approved labor rate](%5Bcreate-labor-rate%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-resource-allocations.tsx](../../../../../../apps/web/src/app/routes/project-resource-allocations.tsx)
- [apps/api/core/hr/capacity_views.py](../../../../../../apps/api/core/hr/capacity_views.py)
- [apps/web/src/app/lib/api/hr-capacity.ts](../../../../../../apps/web/src/app/lib/api/hr-capacity.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../apps/web/src/app/lib/api/wbs.ts)

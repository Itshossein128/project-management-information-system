# Decision: Project job positions

## Context & Screen

- **Route**: `/projects/:businessId/job-positions`
- **Component**: `BusinessJobPositionsPage`
- **Initial State**: Continue from Open legacy project area. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open project Job Positions link.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: CanViewProjectMembers for reads; IsHrOrAdmin for writes
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through useJobPositionsForBusinessQuery.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:businessId/job-positions`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create project position](%5Bcreate-position%5D/README.md)
- [Edit project position](%5Bedit-position%5D/README.md)
- [Delete project position](%5Bdelete-position%5D/README.md)

Continue / return links (the same state is documented once):

- [Open legacy project area](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-job-positions.tsx](../../../../../../apps/web/src/app/routes/business-job-positions.tsx)
- [apps/api/core/business_meta/views.py](../../../../../../apps/api/core/business_meta/views.py)
- [apps/api/core/business_meta/permissions.py](../../../../../../apps/api/core/business_meta/permissions.py)

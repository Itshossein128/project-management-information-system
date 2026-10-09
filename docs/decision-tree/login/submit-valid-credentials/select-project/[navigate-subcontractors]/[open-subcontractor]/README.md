# Decision: Open subcontractor

## Context & Screen

- **Route**: `/projects/:projectId/subcontractors/:subId`
- **Component**: `ProjectSubcontractorDetailPage`
- **Initial State**: Continue from Subcontractors. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click subcontractor row/name.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_contracts
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchSubcontractor; fetchIPCs for a linked contract.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/subcontractors/:subId`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Record performance score](%5Brecord-score%5D/README.md)
- [Create warning](%5Bcreate-warning%5D/README.md)
- [Resolve warning](%5Bresolve-warning%5D/README.md)
- [Export subcontractor activities](export-activities/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Subcontractors](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-subcontractor-detail.tsx](../../../../../../../apps/web/src/app/routes/project-subcontractor-detail.tsx)
- [apps/api/core/subcontractors/views.py](../../../../../../../apps/api/core/subcontractors/views.py)
- [apps/web/src/app/lib/api/subcontractors.ts](../../../../../../../apps/web/src/app/lib/api/subcontractors.ts)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../apps/web/src/app/lib/api/contracts.ts)

# Decision: Export concrete operations

## Context & Screen

- **Route**: `/projects/:projectId/concrete-operations`
- **Component**: `ProjectConcreteOperationsPage`
- **Initial State**: Continue from Concrete operations. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose date range and click CSV.
- **Inputs**: Date filters.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET concrete operations CSV helper.
- **State Change**: Download contains separate production, delivery and poured totals.
- **Navigation**: `/projects/:projectId/concrete-operations`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Concrete operations](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-concrete-operations.tsx](../../../../../../../apps/web/src/app/routes/project-concrete-operations.tsx)
- [apps/web/src/app/lib/api/concrete-operations.ts](../../../../../../../apps/web/src/app/lib/api/concrete-operations.ts)
- [apps/web/src/app/lib/api/costs.ts](../../../../../../../apps/web/src/app/lib/api/costs.ts)

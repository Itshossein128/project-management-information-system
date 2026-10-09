# Decision: HR job positions

## Context & Screen

- **Route**: `/hr/job-positions`
- **Component**: `HrJobPositionsPage`
- **Initial State**: Continue from Open HR hub. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Job Positions card.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: HR card visible to admin/hr; direct route requires IsAuthenticated
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/hr/job-positions`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

This route is a placeholder: it displays explanatory text and Back only. Do not add imaginary job-position CRUD here; project-scoped positions live on a different route.

## Subsequent Decisions

- [Return to HR](return-to-hr/README.md)

Continue / return links (the same state is documented once):

- [Open HR hub](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/hr/job-positions.tsx](../../../../../../apps/web/src/app/routes/hr/job-positions.tsx)

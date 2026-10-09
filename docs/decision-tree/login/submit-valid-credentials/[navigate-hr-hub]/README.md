# Decision: Open HR hub

## Context & Screen

- **Route**: `/hr`
- **Component**: `HrHubPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click HR in global navigation.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Sidebar roles admin or hr; direct route only requires IsAuthenticated
- **Required Roles / Groups**: Sidebar: admin or hr; direct route does not have that same role guard.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/hr`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

HrProtectedLayout only renders Outlet. HR hub cards use frontend role checks; this is not a backend-protected hub endpoint.

## Subsequent Decisions

- [HR users](%5Bnavigate-hr-users%5D/README.md)
- [HR job positions](%5Bnavigate-hr-job-positions%5D/README.md)
- [Legacy project setup list](%5Bnavigate-business-setup%5D/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/hr/home.tsx](../../../../../apps/web/src/app/routes/hr/home.tsx)
- [apps/api/core/authentication/permissions.py](../../../../../apps/api/core/authentication/permissions.py)

# Decision: Executive portfolio dashboard

## Context & Screen

- **Route**: `/portfolio/dashboard`
- **Component**: `ExecutiveDashboardPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Portfolio dashboard in navigation sidebar or project list.
- **Inputs**: Optional query parameter `as_of`.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Active project membership determines which project cards appear.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET `/v1/portfolio/dashboard/` via `fetchPortfolioDashboard`.
- **State Change**: Dashboard strip displays figure summaries across accessible projects. Clicking a figure card opens the figure drill-down drawer.
- **Navigation**: `/portfolio/dashboard`
- **UI Feedback**: Skeleton loading rows while queries resolve; project cards with figure metrics on success; empty state message when no projects exist.

## Outcomes & Guards

Only active project members can see project cards in the dashboard strip; global admins bypass this filter. Data is aggregated read-only. Clicking "Open project dashboard" navigates to the specific project's dashboard.

## Subsequent Decisions

- [Select a project](../select-project/README.md)
- [Open role dashboard](../select-project/%5Bnavigate-dashboard%5D/README.md)
- [Submit valid credentials](../README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/executive-dashboard.tsx](../../../../../apps/web/src/app/routes/executive-dashboard.tsx)
- [apps/web/src/app/lib/api/dashboards.ts](../../../../../apps/web/src/app/lib/api/dashboards.ts)
- [apps/api/core/projects/dashboard_views.py](../../../../../apps/api/core/projects/dashboard_views.py)
- [apps/api/core/projects/services/dashboard_pack_service.py](../../../../../apps/api/core/projects/services/dashboard_pack_service.py)

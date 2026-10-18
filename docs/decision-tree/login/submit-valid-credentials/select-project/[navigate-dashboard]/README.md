# Decision: Role dashboard

## Context & Screen

- **Route**: `/projects/:projectId/dashboard`
- **Component**: `ProjectDashboardPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Role dashboard link in project overview or sidebar.
- **Inputs**: :projectId path parameter, optional query parameters `pack` and `as_of`.

## Authorization & Permissions

- **Required Permissions**: view_dashboard.
- **Required Roles / Groups**: Project member with view_dashboard permission.
- **Protection notation**: Protected action requiring specific permissions or roles.

## Desired Result

- **API Call**: GET `/v1/projects/:projectId/dashboard/pack/` via `fetchProjectDashboardPack`.
- **State Change**: Route loads and renders figure groups (EVM, Progress, Finance, etc.). Clicking a figure card opens the figure drill drawer.
- **Navigation**: `/projects/:projectId/dashboard`
- **UI Feedback**: Skeleton loading rows while queries resolve; DashboardFigureGrid with figure status indicators; AccessDenied if missing permission.

## Outcomes & Guards

Access requires active project membership and view_dashboard permission. When missing permission, AccessDenied component renders.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-dashboard.tsx](../../../../../../apps/web/src/app/routes/project-dashboard.tsx)
- [apps/web/src/app/lib/api/dashboards.ts](../../../../../../apps/web/src/app/lib/api/dashboards.ts)
- [apps/api/core/projects/dashboard_views.py](../../../../../../apps/api/core/projects/dashboard_views.py)
- [apps/api/core/projects/services/dashboard_pack_service.py](../../../../../../apps/api/core/projects/services/dashboard_pack_service.py)

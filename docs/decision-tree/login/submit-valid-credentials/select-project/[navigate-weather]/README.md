# Decision: Weather logs

## Context & Screen

- **Route**: `/projects/:projectId/weather`
- **Component**: `ProjectWeatherPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchWeatherLogs.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/weather`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Create weather record](%5Bcreate-record%5D/README.md)
- [Edit weather record](%5Bedit-record%5D/README.md)
- [Delete weather record](%5Bdelete-record%5D/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-weather.tsx](../../../../../../apps/web/src/app/routes/project-weather.tsx)
- [apps/api/core/field_reports/standalone_forms_views.py](../../../../../../apps/api/core/field_reports/standalone_forms_views.py)

# Decision: Personnel summary

## Context & Screen

- **Route**: `/projects/:projectId/personnel-summary`
- **Component**: `ProjectPersonnelSummaryPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchPersonnelSummary.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/personnel-summary`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Export personnel summary](%5Bexport-personnel-xlsx%5D/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-personnel-summary.tsx](../../../../../../apps/web/src/app/routes/project-personnel-summary.tsx)
- [apps/api/core/field_reports/report_views.py](../../../../../../apps/api/core/field_reports/report_views.py)
- [apps/web/src/app/lib/api/reports.ts](../../../../../../apps/web/src/app/lib/api/reports.ts)

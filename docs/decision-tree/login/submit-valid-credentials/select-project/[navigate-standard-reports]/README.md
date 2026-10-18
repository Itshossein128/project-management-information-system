# Decision: Standard reports

## Context & Screen

- **Route**: `/projects/:projectId/standard-reports`
- **Component**: `StandardReportsPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Standard reports link in project overview or sidebar.
- **Inputs**: :projectId path parameter, selected report type, date range (`date_from`, `date_to`), and `approved_only` toggle.

## Authorization & Permissions

- **Required Permissions**: view_dashboard OR view_reports.
- **Required Roles / Groups**: Project member with view_dashboard or view_reports permission.
- **Protection notation**: Protected action requiring specific permissions or roles.

## Desired Result

- **API Call**: GET `/v1/projects/:projectId/reports/catalog/` via `fetchProjectReportCatalog`, GET `/v1/projects/:projectId/reports/:reportType/run/` via `runProjectReport`, POST `/v1/projects/:projectId/reports/:reportType/export/` via `exportProjectReport`.
- **State Change**: Catalog lists available standard reports; running a report renders structured preview data; exporting generates and downloads file.
- **Navigation**: `/projects/:projectId/standard-reports`
- **UI Feedback**: Report catalog buttons, date range picker, run/export buttons, formatted JSON preview, success toast on export.

## Outcomes & Guards

Access requires active project membership and either view_dashboard or view_reports. Filters adapt based on the selected report's supported_filters list.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Role dashboard](../%5Bnavigate-dashboard%5D/README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-standard-reports.tsx](../../../../../../apps/web/src/app/routes/project-standard-reports.tsx)
- [apps/web/src/app/lib/api/standard-reports.ts](../../../../../../apps/web/src/app/lib/api/standard-reports.ts)
- [apps/api/core/projects/report_views.py](../../../../../../apps/api/core/projects/report_views.py)
- [apps/api/core/projects/services/report_export_service.py](../../../../../../apps/api/core/projects/services/report_export_service.py)

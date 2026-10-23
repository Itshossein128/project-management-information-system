# Decision: Discipline subreports (retired)

## Context & Screen

- **Route**: `/projects/:projectId/sub-reports`
- **Component**: `ErrorBoundary` (`apps/web/src/app/root.tsx`)
- **Initial State**: Continue from Select a project or direct URL entry. This node describes the retired legacy route.

## Action Taken

- **Trigger**: Direct navigation to `/projects/:projectId/sub-reports` or legacy bookmark.
- **Inputs**: `:projectId`

## Authorization & Permissions

- **Required Permissions**: None (unregistered route hits standard 404 boundary)
- **Required Roles / Groups**: None
- **Protection notation**: Directory retains brackets for inventory continuity; route itself is unregistered.

## Desired Result

- **API Call**: None. No report-data requests (`/sub-reports`, `/daily-reports`, `/units/`) are issued.
- **State Change**: Standard localized 404 Not Found boundary is displayed. No forms or editing controls are rendered.
- **Navigation**: `/projects/:projectId/sub-reports`
- **UI Feedback**: Displays "صفحه مورد نظر یافت نشد" / "The requested page could not be found" with navigation back to project.

## Outcomes & Guards

Direct navigation to this retired route never loads the old authoring surface. Specialty unit reporting is authored exclusively from the respective Specialty Unit pages under `/projects/:businessId/{buildings,electrical,mechanical,machinery,warehouse,security}`.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Project daily reports](../%5Bnavigate-daily-reports%5D/README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/root.tsx](../../../../../../apps/web/src/app/root.tsx)
- [apps/web/src/app/routes/business-setup.routes.ts](../../../../../../apps/web/src/app/routes/business-setup.routes.ts)
- [apps/web/e2e/tests/unit-report-source-truth.spec.ts](../../../../../../apps/web/e2e/tests/unit-report-source-truth.spec.ts)

# Decision: Export personnel summary

## Context & Screen

- **Route**: `/projects/:projectId/personnel-summary`
- **Component**: `ProjectPersonnelSummaryPage`
- **Initial State**: Continue from Personnel summary. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export Excel.
- **Inputs**: Current date/category/grouping filters.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Personnel summary export helper.
- **State Change**: Browser downloads XLSX.
- **Navigation**: `/projects/:projectId/personnel-summary`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Personnel summary](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-personnel-summary.tsx](../../../../../../../apps/web/src/app/routes/project-personnel-summary.tsx)
- [apps/web/src/app/lib/api/reports.ts](../../../../../../../apps/web/src/app/lib/api/reports.ts)

# Decision: Refresh material reconciliation

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/edit`
- **Component**: `DailyReportEditPage`
- **Initial State**: Continue from Materials section. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Refresh on material reconciliation.
- **Inputs**: Report ID.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET fetchMaterialReconciliation.
- **State Change**: Consumption/reconciliation comparison refreshes.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/edit`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Materials section](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form-edit.tsx](../../../../../../../../../../apps/web/src/app/routes/daily-report-form-edit.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/components/daily_reports/MaterialsTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/MaterialsTab.tsx)
- [apps/web/src/components/daily_reports/InlineGridTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/InlineGridTab.tsx)

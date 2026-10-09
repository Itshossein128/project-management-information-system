# Decision: Add equipment row

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/edit`
- **Component**: `DailyReportEditPage`
- **Initial State**: Continue from Equipment section. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use the section’s add control and confirm/save the row.
- **Inputs**: Section row values; saved report ID and editable draft/rejected status.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Section handler shown in EquipmentTab; online API / supported offline row persistence.
- **State Change**: Section row state refreshes after save; approved/locked state remains read-only.
- **Navigation**: `/projects/:projectId/daily-reports/:reportId/edit`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Equipment section](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form-edit.tsx](../../../../../../../../../../apps/web/src/app/routes/daily-report-form-edit.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
- [apps/web/src/components/daily_reports/EquipmentTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/EquipmentTab.tsx)
- [apps/web/src/components/daily_reports/InlineGridTab.tsx](../../../../../../../../../../apps/web/src/components/daily_reports/InlineGridTab.tsx)

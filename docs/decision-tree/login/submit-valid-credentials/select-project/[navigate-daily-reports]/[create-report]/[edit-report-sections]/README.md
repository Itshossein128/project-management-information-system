# Decision: Edit report sections

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/new`
- **Component**: `DailyReportNewPage`
- **Initial State**: Continue from Create daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Switch Activities, Labor, Equipment, Materials, Concrete, Incidents or Labor Camp; add/edit/delete visible rows.
- **Inputs**: Section fields; saved report ID required for child rows.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Section save helpers / createChildRow, updateChildRow, deleteChildRow; offline-aware handlers where implemented.
- **State Change**: Rows save in their own sections; approved reports are read-only. Concrete placed in a report remains distinct from production batches and ready-mix deliveries.
- **Navigation**: `/projects/:projectId/daily-reports/new`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Activities section](open-activities/README.md)
- [Labor section](open-labor/README.md)
- [Equipment section](open-equipment/README.md)
- [Materials section](open-materials/README.md)
- [Concrete section](open-concrete/README.md)
- [Incidents section](open-incidents/README.md)
- [Labor-Camp section](open-labor-camp/README.md)

Continue / return links (the same state is documented once):

- [Create daily report](../README.md)
- [View daily report](../../%5Bview-report%5D/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-form.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-form.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/components/daily_reports/DailyReportForm.tsx](../../../../../../../../apps/web/src/components/daily_reports/DailyReportForm.tsx)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)

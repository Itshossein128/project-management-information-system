# Decision: Generate weekly/monthly progress report

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Progress dashboard. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Generate Weekly or Generate Monthly.
- **Inputs**: No user-supplied period dates; the component computes the current week or current calendar month.

## Authorization & Permissions

- **Required Permissions**: view_dashboard
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST generatePeriodReport.
- **State Change**: Period report appears; select it to inspect figures and source approval status.
- **Navigation**: `/projects/:projectId/progress`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The report creation view deliberately uses its read_permission even for POST; this is the actual implementation. The UI computes period_start/period_end using mondayOf/sundayOf or monthBounds; it has no editable period dates.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Override a report figure](%5Boverride-report-figure%5D/README.md)

Continue / return links (the same state is documented once):

- [Progress dashboard](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-progress.tsx](../../../../../../../apps/web/src/app/routes/project-progress.tsx)
- [apps/api/core/schedule/progress_views.py](../../../../../../../apps/api/core/schedule/progress_views.py)
- [apps/web/src/components/progress/PeriodReportsPanel.tsx](../../../../../../../apps/web/src/components/progress/PeriodReportsPanel.tsx)
- [apps/web/src/app/lib/api/progress.ts](../../../../../../../apps/web/src/app/lib/api/progress.ts)
- [apps/api/core/schedule/period_report_views.py](../../../../../../../apps/api/core/schedule/period_report_views.py)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../apps/web/src/app/lib/api/economic.ts)

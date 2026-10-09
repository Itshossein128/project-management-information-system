# Decision: Override a report figure

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Generate weekly/monthly progress report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select report and figure; enter override and reason, then save.
- **Inputs**: Figure ID, replacement value and reason.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST overridePeriodReportFigure.
- **State Change**: Override audit record updates the selected report figure.
- **Navigation**: `/projects/:projectId/progress`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Generate weekly/monthly progress report](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-progress.tsx](../../../../../../../../apps/web/src/app/routes/project-progress.tsx)
- [apps/api/core/schedule/progress_views.py](../../../../../../../../apps/api/core/schedule/progress_views.py)
- [apps/web/src/components/progress/PeriodReportsPanel.tsx](../../../../../../../../apps/web/src/components/progress/PeriodReportsPanel.tsx)
- [apps/web/src/app/lib/api/progress.ts](../../../../../../../../apps/web/src/app/lib/api/progress.ts)
- [apps/api/core/schedule/period_report_views.py](../../../../../../../../apps/api/core/schedule/period_report_views.py)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../../apps/web/src/app/lib/api/economic.ts)

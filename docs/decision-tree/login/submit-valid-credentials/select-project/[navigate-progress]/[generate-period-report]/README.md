# Decision: Generate weekly/monthly progress report

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Progress dashboard. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Generate Weekly or Generate Monthly.
- **Inputs**: No user-supplied period dates; the component computes the current Solar Hijri Saturday-to-Friday week or Solar Hijri month.

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

The report creation view deliberately uses its read_permission even for POST; this is the actual implementation. The server independently validates the Saturday-to-Friday or Solar Hijri month boundary and rejects arbitrary spans. Unapproved or missing daily dates remain visible in header warnings and are excluded from rollups.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Approve official report](%5Bapprove-official-report%5D/README.md)
- [Inspect figure provenance](%5Binspect-figure-provenance%5D/README.md)
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

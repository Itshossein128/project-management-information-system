# Decision: Approve measurement method

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Configure activity measurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Approve Measurement.
- **Inputs**: Activity ID and optional approval reason.

## Authorization & Permissions

- **Required Permissions**: approve_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST approveActivityMeasurement.
- **State Change**: Measurement is approved if backend gates pass.
- **Navigation**: `/projects/:projectId/progress`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

MeasurementEditor does not hide this button by approve_reports; backend still requires it.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Configure activity measurement](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-progress.tsx](../../../../../../../../apps/web/src/app/routes/project-progress.tsx)
- [apps/api/core/schedule/progress_views.py](../../../../../../../../apps/api/core/schedule/progress_views.py)
- [apps/web/src/components/progress/MeasurementEditor.tsx](../../../../../../../../apps/web/src/components/progress/MeasurementEditor.tsx)
- [apps/web/src/app/lib/api/progress.ts](../../../../../../../../apps/web/src/app/lib/api/progress.ts)
- [apps/api/core/schedule/measurement_views.py](../../../../../../../../apps/api/core/schedule/measurement_views.py)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../../apps/web/src/app/lib/api/economic.ts)

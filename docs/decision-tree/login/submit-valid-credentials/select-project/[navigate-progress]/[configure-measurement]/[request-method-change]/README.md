# Decision: Change approved measurement

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Component**: `ProjectProgressPage`
- **Initial State**: Continue from Configure activity measurement. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter a reason and click Request Change.
- **Inputs**: Approved activity and nonempty reason/proposed method.

## Authorization & Permissions

- **Required Permissions**: edit_activities
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST changeActivityMeasurement.
- **State Change**: Approved method enters the controlled change flow.
- **Navigation**: `/projects/:projectId/progress`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

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

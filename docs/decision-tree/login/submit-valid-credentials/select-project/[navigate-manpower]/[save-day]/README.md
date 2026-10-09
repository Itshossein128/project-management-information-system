# Decision: Save daily manpower

## Context & Screen

- **Route**: `/projects/:projectId/manpower`
- **Component**: `ProjectManpowerPage`
- **Initial State**: Continue from Manpower. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose date/category, edit job-title counts or add a custom title and Save.
- **Inputs**: The displayed form/row values.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: saveManpowerDay mutation.
- **State Change**: The screen’s affected query refreshes after acceptance.
- **Navigation**: `/projects/:projectId/manpower`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Manpower](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-manpower.tsx](../../../../../../../apps/web/src/app/routes/project-manpower.tsx)
- [apps/web/src/app/lib/api/manpower.ts](../../../../../../../apps/web/src/app/lib/api/manpower.ts)

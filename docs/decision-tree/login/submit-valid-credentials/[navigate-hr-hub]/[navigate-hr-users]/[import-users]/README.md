# Decision: Import HR users

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from HR users. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Excel Import, choose file and submit.
- **Inputs**: Import spreadsheet.

## Authorization & Permissions

- **Required Permissions**: IsHrOrAdmin
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: ExcelImportModal reads rows locally; useCreateHrUser sends POST /api/auth/users/ for each valid row.
- **State Change**: Import result appears and user list reloads for created records; row failures remain visible.
- **Navigation**: `/hr/users`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

There is no bulk import endpoint in this route; it creates users one by one. Partial import can leave already created users; row errors are not a transaction rollback.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [HR users](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/hr/users.tsx](../../../../../../../apps/web/src/app/routes/hr/users.tsx)
- [apps/api/core/authentication/views.py](../../../../../../../apps/api/core/authentication/views.py)
- [apps/api/core/authentication/permissions.py](../../../../../../../apps/api/core/authentication/permissions.py)

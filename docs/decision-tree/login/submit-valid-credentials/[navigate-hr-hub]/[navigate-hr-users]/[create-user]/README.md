# Decision: Create HR user

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from HR users. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open New User, enter details and submit.
- **Inputs**: Phone, first_name, last_name, password and confirmation.

## Authorization & Permissions

- **Required Permissions**: IsHrOrAdmin
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST /api/auth/users/ via useCreateHrUser.
- **State Change**: User table reloads; field/submit errors stay in modal.
- **Navigation**: `/hr/users`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Show/hide password](toggle-password-visibility/README.md)

Continue / return links (the same state is documented once):

- [HR users](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/hr/users.tsx](../../../../../../../apps/web/src/app/routes/hr/users.tsx)
- [apps/api/core/authentication/views.py](../../../../../../../apps/api/core/authentication/views.py)
- [apps/api/core/authentication/permissions.py](../../../../../../../apps/api/core/authentication/permissions.py)
- [apps/web/src/components/hr/create-hr-user-modal.tsx](../../../../../../../apps/web/src/components/hr/create-hr-user-modal.tsx)
- [apps/web/src/app/hooks/queries.ts](../../../../../../../apps/web/src/app/hooks/queries.ts)

# Decision: Register successfully

## Context & Screen

- **Route**: `/register`
- **Component**: `Register`
- **Initial State**: Continue from Open registration. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit the registration form.
- **Inputs**: phone_number, first_name, last_name, password, password_confirm.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/register/.
- **State Change**: Success establishes a session and navigates through /home to /projects.
- **Navigation**: `/projects`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Submit valid credentials](../../submit-valid-credentials/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/register.tsx](../../../../../apps/web/src/app/routes/register.tsx)

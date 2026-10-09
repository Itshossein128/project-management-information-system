# Decision: Submit recovery phone

## Context & Screen

- **Route**: `/forgot-password`
- **Component**: `ForgotPassword`
- **Initial State**: Continue from Request password recovery. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit Send Link.
- **Inputs**: phone_number.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/forgot-password/.
- **State Change**: Successful response replaces the form with confirmation; it does not authenticate the user.
- **Navigation**: `/forgot-password`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The confirmation uses email-oriented translation keys with the phone value. Do not infer that an email or SMS was delivered from this UI response.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Open reset link](open-reset-link/README.md)

Continue / return links (the same state is documented once):

- [Request password recovery](../README.md)
- [Open the application](../../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/forgot-password.tsx](../../../../../apps/web/src/app/routes/forgot-password.tsx)

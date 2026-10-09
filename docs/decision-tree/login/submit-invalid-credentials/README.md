# Decision: Submit invalid credentials

## Context & Screen

- **Route**: `/login`
- **Component**: `AuthLayout`
- **Initial State**: Continue from Open the application. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit Sign In with invalid credentials.
- **Inputs**: Incorrect phone/password, missing required field, or an authentication/network failure.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/login/ if native required-field validation permits submission.
- **State Change**: An API/network failure keeps the login form and displays login-global-error. Missing required values can stop submission in the browser.
- **Navigation**: `/login`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Retry with valid credentials](retry-with-valid-credentials/README.md)
- [Retry with invalid credentials](retry-with-invalid-credentials/README.md)
- [Open register](navigate-register/README.md)
- [Open forgot-password](navigate-forgot-password/README.md)

Continue / return links (the same state is documented once):

- [Open the application](../README.md)

## Source Evidence

- [apps/web/src/app/routes/index.tsx](../../../../apps/web/src/app/routes/index.tsx)
- [apps/web/src/app/routes/login.tsx](../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/_auth.tsx](../../../../apps/web/src/app/routes/_auth.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../apps/web/src/app/contexts/auth-context.tsx)

# Decision: Open the application

## Context & Screen

- **Route**: `/login`
- **Component**: `AuthLayout`
- **Initial State**: No stored session on first launch. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open / without a stored session, or open /login.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: Root index loader checks client storage / the SSR auth cookie; no login request yet.
- **State Change**: Unauthenticated entry redirects to /login; an existing session can continue to /projects.
- **Navigation**: `/login`
- **UI Feedback**: The updated screen is displayed.

## Outcomes & Guards

This is the unauthenticated entry state. A protected deep link adds redirectTo; an authenticated root visit skips this form.

## Subsequent Decisions

- [Submit valid credentials](submit-valid-credentials/README.md)
- [Submit invalid credentials](submit-invalid-credentials/README.md)
- [Open registration](navigate-register/README.md)
- [Request password recovery](navigate-forgot-password/README.md)
- [Change theme](toggle-theme/README.md)
- [Change language](change-language/README.md)
- [Show/hide password](toggle-password-visibility/README.md)

## Source Evidence

- [apps/web/src/app/routes/index.tsx](../../../apps/web/src/app/routes/index.tsx)
- [apps/web/src/app/routes/login.tsx](../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/_auth.tsx](../../../apps/web/src/app/routes/_auth.tsx)

# Decision: Retry with valid credentials

## Context & Screen

- **Route**: `/login`
- **Component**: `AuthLayout`
- **Initial State**: Continue from Submit invalid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Correct the fields and submit again.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/login/.
- **State Change**: Successful authentication follows the canonical signed-in branch.
- **Navigation**: `/login`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Submit valid credentials](../../submit-valid-credentials/README.md)

## Source Evidence

- [apps/web/src/app/routes/index.tsx](../../../../../apps/web/src/app/routes/index.tsx)
- [apps/web/src/app/routes/login.tsx](../../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/_auth.tsx](../../../../../apps/web/src/app/routes/_auth.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../../apps/web/src/app/contexts/auth-context.tsx)

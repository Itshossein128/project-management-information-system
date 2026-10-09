# Decision: Recover an expired session

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `AuthLayout`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Retry a protected action after receiving 401.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated or a recoverable stored refresh token.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/token/refresh/; retry original request once.
- **State Change**: Recovered token retries the request; failed recovery clears storage and redirects to login with redirectTo.
- **Navigation**: `Current screen after recovery; /login?redirectTo=... after failure.`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)
- [Open the application](../../README.md)

## Source Evidence

- [apps/web/src/app/routes/login.tsx](../../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/home.tsx](../../../../../apps/web/src/app/routes/home.tsx)
- [apps/web/src/app/routes/project-list.tsx](../../../../../apps/web/src/app/routes/project-list.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../../apps/web/src/app/contexts/auth-context.tsx)
- [apps/web/src/app/lib/auth-storage.ts](../../../../../apps/web/src/app/lib/auth-storage.ts)
- [apps/web/src/app/lib/api-client.ts](../../../../../apps/web/src/app/lib/api-client.ts)
- [apps/web/src/app/routes/_auth.tsx](../../../../../apps/web/src/app/routes/_auth.tsx)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../apps/web/src/app/lib/api/projects.ts)

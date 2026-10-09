# Decision: Retry failed load

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Retry on the displayed QueryErrorState.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: Refetch the query used by the screen’s onRetry handler.
- **State Change**: Loading state restarts; success or repeated failure determines the rendered content.
- **Navigation**: `/login → /projects`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

## Source Evidence

- [apps/web/src/app/routes/login.tsx](../../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/home.tsx](../../../../../apps/web/src/app/routes/home.tsx)
- [apps/web/src/app/routes/project-list.tsx](../../../../../apps/web/src/app/routes/project-list.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../../apps/web/src/app/contexts/auth-context.tsx)
- [apps/web/src/app/lib/auth-storage.ts](../../../../../apps/web/src/app/lib/auth-storage.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/components/layout/query-error-state.tsx](../../../../../apps/web/src/components/layout/query-error-state.tsx)

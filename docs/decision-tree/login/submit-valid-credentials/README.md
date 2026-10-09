# Decision: Submit valid credentials

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Open the application. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Submit Sign In or press Enter.
- **Inputs**: phone_number and password.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST /api/auth/login/ via AuthProvider.login.
- **State Change**: establishSession stores access/refresh/user; auth_token cookie and React auth state are synchronized.
- **Navigation**: `redirectTo if supplied; otherwise /home → /projects.`
- **UI Feedback**: Busy indicator while submitting; authenticated app shell after success.

## Outcomes & Guards

API_BASE is configurable; endpoint examples use its default /api path. Login honors redirectTo rather than always opening the project list.

## Subsequent Decisions

- [Change theme](toggle-theme/README.md)
- [Change language](change-language/README.md)
- [Sign out](logout/README.md)
- [Open mobile navigation](open-mobile-navigation/README.md)
- [Open notifications](open-notifications/README.md)
- [Create a project](create-project/README.md)
- [Select a project](select-project/README.md)
- [Open HR hub](%5Bnavigate-hr-hub%5D/README.md)
- [Template settings](%5Bnavigate-templates%5D/README.md)
- [Project-role settings](%5Bnavigate-roles%5D/README.md)
- [Organization references](%5Bnavigate-org-refs%5D/README.md)
- [Open legacy project area](%5Bopen-legacy-project%5D/README.md)
- [Portfolio liquidity allocation](open-portfolio-liquidity/README.md)
- [Retry failed load](retry-failed-load/README.md)
- [Recover an expired session](recover-expired-session/README.md)

## Source Evidence

- [apps/web/src/app/routes/login.tsx](../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/home.tsx](../../../../apps/web/src/app/routes/home.tsx)
- [apps/web/src/app/routes/project-list.tsx](../../../../apps/web/src/app/routes/project-list.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../apps/web/src/app/contexts/auth-context.tsx)
- [apps/web/src/app/lib/auth-storage.ts](../../../../apps/web/src/app/lib/auth-storage.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../apps/web/src/app/lib/api/projects.ts)

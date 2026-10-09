# Decision: Request password recovery

## Context & Screen

- **Route**: `/forgot-password`
- **Component**: `ForgotPassword`
- **Initial State**: Continue from Open the application. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Forgot Password on Login.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/forgot-password`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Submit recovery phone](submit-phone-for-reset/README.md)
- [Return to login](navigate-back-to-login/README.md)
- [Change theme](toggle-theme/README.md)
- [Change language](change-language/README.md)

Continue / return links (the same state is documented once):

- [Open the application](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../submit-valid-credentials/README.md).

## Source Evidence

- [apps/web/src/app/routes/forgot-password.tsx](../../../../apps/web/src/app/routes/forgot-password.tsx)

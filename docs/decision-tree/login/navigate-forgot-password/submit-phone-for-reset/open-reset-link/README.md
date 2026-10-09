# Decision: Open reset link

## Context & Screen

- **Route**: `/reset-password`
- **Component**: `ResetPassword`
- **Initial State**: Continue from Submit recovery phone. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open an externally supplied /reset-password?token=... URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/reset-password`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

There is no in-app reset link on the recovery confirmation; this edge represents entry via the externally supplied token URL.

## Subsequent Decisions

- [Reset password](submit-new-password/README.md)
- [Handle invalid reset inputs](submit-mismatched-or-missing-token/README.md)
- [Return to login](navigate-back-to-login/README.md)
- [Change theme](toggle-theme/README.md)
- [Change language](change-language/README.md)
- [Show/hide password](toggle-password-visibility/README.md)

Continue / return links (the same state is documented once):

- [Submit recovery phone](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../submit-valid-credentials/README.md).

## Source Evidence

- [apps/web/src/app/routes/reset-password.tsx](../../../../../../apps/web/src/app/routes/reset-password.tsx)

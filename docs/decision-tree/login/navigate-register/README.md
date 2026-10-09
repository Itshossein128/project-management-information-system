# Decision: Open registration

## Context & Screen

- **Route**: `/register`
- **Component**: `Register`
- **Initial State**: Continue from Open the application. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the registration link on Login.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: None (Public).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; navigation-only screen.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/register`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Register successfully](submit-valid-registration/README.md)
- [Registration validation fails](submit-invalid-registration/README.md)
- [Return to login](navigate-back-to-login/README.md)
- [Change theme](toggle-theme/README.md)
- [Change language](change-language/README.md)
- [Show/hide password](toggle-password-visibility/README.md)

Continue / return links (the same state is documented once):

- [Open the application](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../submit-valid-credentials/README.md).

## Source Evidence

- [apps/web/src/app/routes/register.tsx](../../../../apps/web/src/app/routes/register.tsx)

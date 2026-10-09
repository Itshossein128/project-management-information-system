# Decision: Return to login

## Context & Screen

- **Route**: `/reset-password`
- **Component**: `ResetPassword`
- **Initial State**: Continue from Open reset link. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Back to Sign In / Sign In.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Local selection changes; no server mutation.
- **Navigation**: `/login`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open the application](../../../../README.md)

## Source Evidence

- [apps/web/src/app/routes/reset-password.tsx](../../../../../../../apps/web/src/app/routes/reset-password.tsx)

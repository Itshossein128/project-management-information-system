# Decision: Change language

## Context & Screen

- **Route**: `/reset-password`
- **Component**: `ResetPassword`
- **Initial State**: Continue from Open reset link. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use LanguageSwitcher to select Persian or English.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; browser preference update.
- **State Change**: Language preference updates translations and text direction.
- **Navigation**: `/reset-password`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open reset link](../README.md)

## Source Evidence

- [apps/web/src/app/routes/reset-password.tsx](../../../../../../../apps/web/src/app/routes/reset-password.tsx)
- [apps/web/src/components/LanguageSwitcher.tsx](../../../../../../../apps/web/src/components/LanguageSwitcher.tsx)

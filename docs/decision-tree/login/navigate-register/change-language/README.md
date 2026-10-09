# Decision: Change language

## Context & Screen

- **Route**: `/register`
- **Component**: `Register`
- **Initial State**: Continue from Open registration. This node describes the state reached by the action below.

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
- **Navigation**: `/register`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open registration](../README.md)

## Source Evidence

- [apps/web/src/app/routes/register.tsx](../../../../../apps/web/src/app/routes/register.tsx)
- [apps/web/src/components/LanguageSwitcher.tsx](../../../../../apps/web/src/components/LanguageSwitcher.tsx)

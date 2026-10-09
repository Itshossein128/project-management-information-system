# Decision: Change theme

## Context & Screen

- **Route**: `/forgot-password`
- **Component**: `ForgotPassword`
- **Initial State**: Continue from Request password recovery. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click button-themeToggle once to switch light/dark theme.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; browser preference update.
- **State Change**: Theme preference updates the app presentation.
- **Navigation**: `/forgot-password`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Request password recovery](../README.md)

## Source Evidence

- [apps/web/src/app/routes/forgot-password.tsx](../../../../../apps/web/src/app/routes/forgot-password.tsx)
- [apps/web/src/components/AppPreferencesBar.tsx](../../../../../apps/web/src/components/AppPreferencesBar.tsx)
- [apps/web/src/components/ThemeToggle.tsx](../../../../../apps/web/src/components/ThemeToggle.tsx)

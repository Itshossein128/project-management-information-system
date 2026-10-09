# Decision: Show/hide password

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from Create HR user. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the eye button on a password input.
- **Inputs**: The selected password/confirmation input.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; PasswordInput.visible state.
- **State Change**: Input type toggles password/text; value is unchanged.
- **Navigation**: `/hr/users`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Create HR user](../README.md)

## Source Evidence

- [apps/web/src/app/routes/hr/users.tsx](../../../../../../../../apps/web/src/app/routes/hr/users.tsx)
- [apps/api/core/authentication/views.py](../../../../../../../../apps/api/core/authentication/views.py)
- [apps/api/core/authentication/permissions.py](../../../../../../../../apps/api/core/authentication/permissions.py)
- [apps/web/src/components/hr/create-hr-user-modal.tsx](../../../../../../../../apps/web/src/components/hr/create-hr-user-modal.tsx)
- [apps/web/src/app/hooks/queries.ts](../../../../../../../../apps/web/src/app/hooks/queries.ts)
- [apps/web/src/components/form/PasswordInput.tsx](../../../../../../../../apps/web/src/components/form/PasswordInput.tsx)

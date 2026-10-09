# Decision: Delete custom role

## Context & Screen

- **Route**: `/settings/roles`
- **Component**: `SettingsRolesPage`
- **Initial State**: Continue from Project-role settings. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Delete and confirm.
- **Inputs**: Role ID, name/description or permission selection.

## Authorization & Permissions

- **Required Permissions**: IsHrOrAdmin
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: deleteProjectRole mutation.
- **State Change**: Custom role is removed if reference rules allow.
- **Navigation**: `/settings/roles`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

System roles are immutable in the UI/backend checks; membership usage may prevent deletion.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project-role settings](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/settings-roles.tsx](../../../../../../apps/web/src/app/routes/settings-roles.tsx)
- [apps/api/core/projects/role_views.py](../../../../../../apps/api/core/projects/role_views.py)
- [apps/web/src/app/lib/api/roles.ts](../../../../../../apps/web/src/app/lib/api/roles.ts)

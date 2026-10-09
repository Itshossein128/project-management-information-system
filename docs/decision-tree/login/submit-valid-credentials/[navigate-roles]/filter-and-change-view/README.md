# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/settings/roles`
- **Component**: `SettingsRolesPage`
- **Initial State**: Continue from Project-role settings. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select a role; toggle individual permissions or Select All on a mutable role.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; local view state only.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/settings/roles`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project-role settings](../README.md)

## Source Evidence

- [apps/web/src/app/routes/settings-roles.tsx](../../../../../../apps/web/src/app/routes/settings-roles.tsx)
- [apps/api/core/projects/role_views.py](../../../../../../apps/api/core/projects/role_views.py)
- [apps/web/src/app/lib/api/roles.ts](../../../../../../apps/web/src/app/lib/api/roles.ts)

# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from HR users. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Search, filter, sort and paginate the HR users table.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET useHrUsersQuery parameters.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/hr/users`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [HR users](../README.md)

## Source Evidence

- [apps/web/src/app/routes/hr/users.tsx](../../../../../../../apps/web/src/app/routes/hr/users.tsx)
- [apps/api/core/authentication/views.py](../../../../../../../apps/api/core/authentication/views.py)
- [apps/api/core/authentication/permissions.py](../../../../../../../apps/api/core/authentication/permissions.py)

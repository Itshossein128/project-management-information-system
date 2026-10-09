# Decision: Inspect user assignments

## Context & Screen

- **Route**: `/hr/users`
- **Component**: `HrUsersPage`
- **Initial State**: Continue from HR users. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the assignments/detail action for a user.
- **Inputs**: User ID.

## Authorization & Permissions

- **Required Permissions**: IsHrOrAdmin
- **Required Roles / Groups**: Frontend: admin or hr. Backend IsHrOrAdmin also accepts staff/superuser where that class is used.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET user assignments via AllAssignmentsModal.
- **State Change**: Assignment detail modal opens.
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
- [apps/web/src/components/assignments/all-assignments-modal.tsx](../../../../../../../apps/web/src/components/assignments/all-assignments-modal.tsx)

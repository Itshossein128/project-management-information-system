# Decision: Inspect legacy assignment

## Context & Screen

- **Route**: `/projects/:businessId/users`
- **Component**: `BusinessUsersPage`
- **Initial State**: Continue from Legacy project members. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click an assignment detail button.
- **Inputs**: Selected assignment.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; selected assignment is passed into AssignmentDetailModal.
- **State Change**: Assignment modal opens with the legacy shape.
- **Navigation**: `/projects/:businessId/users`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Legacy project members](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-users.tsx](../../../../../../../apps/web/src/app/routes/business-users.tsx)
- [apps/api/core/projects/member_views.py](../../../../../../../apps/api/core/projects/member_views.py)
- [apps/web/src/components/assignments/assignment-detail-modal.tsx](../../../../../../../apps/web/src/components/assignments/assignment-detail-modal.tsx)

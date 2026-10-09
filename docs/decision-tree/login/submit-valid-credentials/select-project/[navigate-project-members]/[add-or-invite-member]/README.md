# Decision: Add/invite project member

## Context & Screen

- **Route**: `/projects/:projectId/settings/members`
- **Component**: `ProjectMembersPage`
- **Initial State**: Continue from Project members. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Add Member, choose user or email and role(s) and save.
- **Inputs**: User/email and role IDs, or existing member user ID.

## Authorization & Permissions

- **Required Permissions**: manage_members
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: addMember mutation.
- **State Change**: Membership or invitation is created.
- **Navigation**: `/projects/:projectId/settings/members`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project members](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-members.tsx](../../../../../../../apps/web/src/app/routes/project-members.tsx)
- [apps/api/core/projects/member_views.py](../../../../../../../apps/api/core/projects/member_views.py)
- [apps/web/src/components/projects/add-member-drawer.tsx](../../../../../../../apps/web/src/components/projects/add-member-drawer.tsx)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)

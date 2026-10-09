# Decision: Open a notification

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Open notifications. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a notification row.
- **Inputs**: Notification ID and optional link.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; target screen applies its own authorization.
- **Required Roles / Groups**: None.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: markRead mutation for an unread notification.
- **State Change**: Notification becomes read; if a link exists the popover closes and navigation follows it.
- **Navigation**: `Notification link, or current page when link is absent.`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Submit valid credentials](../../README.md)
- [Select a project](../../select-project/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/login.tsx](../../../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/home.tsx](../../../../../../apps/web/src/app/routes/home.tsx)
- [apps/web/src/app/routes/project-list.tsx](../../../../../../apps/web/src/app/routes/project-list.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../../../apps/web/src/app/contexts/auth-context.tsx)
- [apps/web/src/app/lib/auth-storage.ts](../../../../../../apps/web/src/app/lib/auth-storage.ts)
- [apps/web/src/components/notifications/NotificationBell.tsx](../../../../../../apps/web/src/components/notifications/NotificationBell.tsx)
- [apps/web/src/components/notifications/NotificationPanel.tsx](../../../../../../apps/web/src/components/notifications/NotificationPanel.tsx)
- [apps/web/src/app/hooks/useNotifications.ts](../../../../../../apps/web/src/app/hooks/useNotifications.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../apps/web/src/app/lib/api/projects.ts)

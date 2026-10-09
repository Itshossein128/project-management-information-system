# Decision: Mark all notifications read

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Open notifications. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Mark All Read.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: useNotificationActions.markAllRead mutation.
- **State Change**: Unread count and list update.
- **Navigation**: `/login → /projects`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open notifications](../README.md)
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

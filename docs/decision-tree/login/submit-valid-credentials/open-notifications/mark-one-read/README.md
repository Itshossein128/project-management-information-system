# Decision: Mark notification read

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Open notifications. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the per-notification read check button.
- **Inputs**: Notification ID.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: useNotificationActions.markRead.
- **State Change**: Read status/unread count refresh.
- **Navigation**: `/login → /projects`
- **UI Feedback**: Success updates the visible state. An unsuccessful request shows the handler’s error feedback and does not take the success navigation.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open notifications](../README.md)

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

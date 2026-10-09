# Decision: Open notifications

## Context & Screen

- **Route**: `/login → /projects`
- **Component**: `ProjectListPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the header bell.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: None.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET through useNotificationList / useUnreadCount.
- **State Change**: Notification popover opens.
- **Navigation**: `/login → /projects`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Mark all notifications read](mark-all-read/README.md)
- [Open a notification](%5Bopen-notification%5D/README.md)
- [Mark notification read](mark-one-read/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

## Source Evidence

- [apps/web/src/app/routes/login.tsx](../../../../../apps/web/src/app/routes/login.tsx)
- [apps/web/src/app/routes/home.tsx](../../../../../apps/web/src/app/routes/home.tsx)
- [apps/web/src/app/routes/project-list.tsx](../../../../../apps/web/src/app/routes/project-list.tsx)
- [apps/web/src/app/contexts/auth-context.tsx](../../../../../apps/web/src/app/contexts/auth-context.tsx)
- [apps/web/src/app/lib/auth-storage.ts](../../../../../apps/web/src/app/lib/auth-storage.ts)
- [apps/web/src/components/notifications/NotificationBell.tsx](../../../../../apps/web/src/components/notifications/NotificationBell.tsx)
- [apps/web/src/components/notifications/NotificationPanel.tsx](../../../../../apps/web/src/components/notifications/NotificationPanel.tsx)
- [apps/web/src/app/hooks/useNotifications.ts](../../../../../apps/web/src/app/hooks/useNotifications.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../apps/web/src/app/lib/api/projects.ts)

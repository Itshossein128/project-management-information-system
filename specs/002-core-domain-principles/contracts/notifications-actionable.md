# Contract: Actionable Notifications

**Feature**: `002-core-domain-principles`  
**Base path**: existing notifications API (extend payloads)

## Extended resource fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `responsible_user` | UUID \| null | required for actionable types | Owner of the action |
| `responsible_user_name` | string | read-only | Presentation |
| `due_at` | datetime \| null | required for time-bound actionable types | Deadline |
| `link` | string | required for actionable types | Deep link to record |

Existing fields (`user`, `project`, `title`, `message`, `notification_type`, `is_read`, …) unchanged.

## Create rules (service)

| Notification class | `responsible_user` | `due_at` | `link` |
|--------------------|--------------------|----------|--------|
| Actionable time-bound | required | required | required |
| Actionable informational | required | optional | required |
| Broadcast / system | optional | optional | optional |

## List/detail response example

```json
{
  "id": "uuid",
  "title": "...",
  "link": "/projects/{id}/daily-reports/{rid}",
  "responsible_user": "uuid",
  "due_at": "2026-10-10T12:00:00Z",
  "is_read": false
}
```

## Errors

| Code | HTTP | When |
|------|------|------|
| `notification_owner_required` | 400 | Actionable without responsible_user |
| `notification_link_required` | 400 | Actionable without link |
| `notification_due_required` | 400 | Time-bound without due_at |

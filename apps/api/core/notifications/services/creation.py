"""Notification creation helpers with actionable fields (FR-CORE-011)."""
from __future__ import annotations

from rest_framework.exceptions import ValidationError

from notifications.models import Notification, NotificationType

ACTIONABLE_TYPES = frozenset(
    {
        NotificationType.REPORT_SUBMITTED,
        NotificationType.REPORT_APPROVED,
        NotificationType.REPORT_REJECTED,
    }
)
TIME_BOUND_TYPES = frozenset(
    {
        NotificationType.REPORT_SUBMITTED,
    }
)


def create_notification(
    *,
    user,
    title: str,
    message: str = '',
    notification_type: str = NotificationType.GENERIC,
    project=None,
    link: str = '',
    responsible_user=None,
    due_at=None,
) -> Notification:
    actionable = notification_type in ACTIONABLE_TYPES
    if actionable:
        if responsible_user is None:
            raise ValidationError(
                {
                    'code': 'notification_owner_required',
                    'message': 'Actionable notifications require responsible_user.',
                }
            )
        if not (link or '').strip():
            raise ValidationError(
                {
                    'code': 'notification_link_required',
                    'message': 'Actionable notifications require link.',
                }
            )
        if notification_type in TIME_BOUND_TYPES and due_at is None:
            raise ValidationError(
                {
                    'code': 'notification_due_required',
                    'message': 'Time-bound notifications require due_at.',
                }
            )

    return Notification.objects.create(
        user=user,
        project=project,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link or '',
        responsible_user=responsible_user,
        due_at=due_at,
    )

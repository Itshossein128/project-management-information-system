"""HSE incident notification handler (feature 033, T046).

Creates one project-scoped notification per incident row. Repeated submits and
rebuilds reuse the existing notification (idempotent on the incident id).
"""
from __future__ import annotations

from notifications.models import Notification, NotificationType


def ensure_hse_notification(incident, *, user):
    """Return the notification for this incident, creating it when missing."""
    if incident is None or user is None:
        return None
    link = f'hse-incident:{incident.id}'
    project_id = incident.sub_report.project_id
    existing = Notification.objects.filter(project_id=project_id, link=link).first()
    if existing is not None:
        return existing
    return Notification.objects.create(
        user=user,
        project_id=project_id,
        notification_type=NotificationType.GENERIC,
        title='HSE incident',
        message=(incident.text or '')[:1000],
        link=link,
        responsible_user=user,
    )


def ensure_hse_notifications_for_report(report, user):
    """Emit notifications for every non-deleted HSE row on this version."""
    created = []
    for row in report.hse_incidents.filter(is_deleted=False).order_by('row_number', 'id'):
        note = ensure_hse_notification(row, user=user)
        if note is not None:
            created.append(note)
    return created

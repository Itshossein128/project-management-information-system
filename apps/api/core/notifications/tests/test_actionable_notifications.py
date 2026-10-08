"""US5: actionable notification fields."""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from notifications.models import NotificationType
from notifications.services.creation import create_notification


@pytest.mark.django_db
def test_actionable_requires_owner_and_link(user, project):
    with pytest.raises(ValidationError) as exc:
        create_notification(
            user=user,
            title='t',
            notification_type=NotificationType.REPORT_SUBMITTED,
            project=project,
            link='',
            responsible_user=user,
            due_at=timezone.now() + timedelta(days=1),
        )
    assert 'notification_link_required' in str(exc.value)

    with pytest.raises(ValidationError):
        create_notification(
            user=user,
            title='t',
            notification_type=NotificationType.REPORT_SUBMITTED,
            project=project,
            link='/x',
            responsible_user=None,
            due_at=timezone.now() + timedelta(days=1),
        )


@pytest.mark.django_db
def test_actionable_create_and_serialize(auth_client, user, project):
    due = timezone.now() + timedelta(days=2)
    n = create_notification(
        user=user,
        title='Report submitted',
        notification_type=NotificationType.REPORT_SUBMITTED,
        project=project,
        link=f'/projects/{project.id}/daily-reports/1',
        responsible_user=user,
        due_at=due,
    )
    resp = auth_client.get('/api/v1/notifications/')
    assert resp.status_code == 200
    rows = resp.json() if isinstance(resp.json(), list) else resp.json().get('results', [])
    match = next(r for r in rows if str(r['id']) == str(n.id))
    assert match['responsible_user'] == str(user.id)
    assert match['link']
    assert match.get('due_at')

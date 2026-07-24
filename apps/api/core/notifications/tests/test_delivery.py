"""Tests for multi-channel alert notification delivery (K-04)."""

import pytest
from django.core import mail

from alerts.models import AlertRule
from alerts.services.alert_engine import fire_alert
from notifications.models import Notification
from notifications.services.delivery import deliver_alert_notifications


@pytest.mark.django_db
def test_deliver_in_app_and_email(settings, project, user):
    settings.ALERT_NOTIFY_CHANNELS = 'in_app,email'
    user.email = 'pm@example.com'
    user.save(update_fields=['email'])

    sent = deliver_alert_notifications(
        user_ids=[user.id],
        project_id=project.id,
        title='Test alert',
        message='Something happened',
        link='/projects/x/alerts',
    )
    assert sent == 1
    assert Notification.objects.filter(user=user, project=project).count() == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Test alert'
    assert 'Something happened' in mail.outbox[0].body


@pytest.mark.django_db
def test_deliver_sms_channel_logs(settings, project, user, caplog):
    settings.ALERT_NOTIFY_CHANNELS = 'in_app,sms'
    import logging

    with caplog.at_level(logging.INFO, logger='notifications.services.delivery'):
        deliver_alert_notifications(
            user_ids=[user.id],
            project_id=project.id,
            title='SMS title',
            message='SMS body',
        )
    assert any('SMS to' in r.message for r in caplog.records)


@pytest.mark.django_db
def test_fire_alert_uses_delivery(settings, project, user):
    settings.ALERT_NOTIFY_CHANNELS = 'in_app,email'
    user.email = 'pm@example.com'
    user.save(update_fields=['email'])

    rule = AlertRule.objects.create(
        project=None,
        alert_type='budget_overrun',
        name='Budget',
        notify_roles='project_manager',
        is_active=True,
    )
    log = fire_alert(rule.id, 'delivery:1', 'Delivery test', project.id)
    assert log is not None
    assert log.notifications_sent >= 1
    assert Notification.objects.filter(project=project).exists()
    assert len(mail.outbox) >= 1

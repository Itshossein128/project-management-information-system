"""Multi-channel notification delivery (blueprint K-04)."""

from __future__ import annotations

import logging
from typing import Iterable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from notifications.models import Notification, NotificationType

logger = logging.getLogger(__name__)
User = get_user_model()


def configured_channels() -> list[str]:
    raw = getattr(settings, 'ALERT_NOTIFY_CHANNELS', 'in_app,email')
    return [c.strip().lower() for c in str(raw).split(',') if c.strip()]


class ConsoleSmsBackend:
    """Default SMS backend — logs only unless SMS_PROVIDER is configured."""

    def send(self, phone: str, message: str) -> bool:
        logger.info('SMS to %s: %s', phone, message[:200])
        return True


def get_sms_backend():
    provider = getattr(settings, 'SMS_PROVIDER', 'console') or 'console'
    if provider == 'console':
        return ConsoleSmsBackend()
    return ConsoleSmsBackend()


def deliver_alert_notifications(
    *,
    user_ids: Iterable,
    project_id,
    title: str,
    message: str,
    link: str = '',
) -> int:
    """
    Deliver alert to recipients across configured channels.
    Returns count of successful in-app deliveries (AlertLog.notifications_sent).
    """
    channels = set(configured_channels())
    if not channels:
        channels = {'in_app'}

    id_list = list(user_ids)
    users = {str(u.id): u for u in User.objects.filter(id__in=id_list)}
    in_app_sent = 0
    sms = get_sms_backend() if 'sms' in channels else None

    for uid in id_list:
        user = users.get(str(uid))
        if 'in_app' in channels:
            Notification.objects.create(
                user_id=uid,
                project_id=project_id,
                notification_type=NotificationType.GENERIC,
                title=title,
                message=message,
                link=link,
            )
            in_app_sent += 1

        if user is None:
            continue

        if 'email' in channels and user.email:
            try:
                send_mail(
                    subject=title,
                    message=f'{message}\n\n{link}'.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:  # noqa: BLE001
                logger.exception('Email delivery failed for user %s', user.id)

        if sms is not None:
            phone = getattr(user, 'mobile', None) or getattr(user, 'phone_number', None)
            if phone:
                try:
                    sms.send(str(phone), f'{title}: {message}')
                except Exception:  # noqa: BLE001
                    logger.exception('SMS delivery failed for user %s', user.id)

    return in_app_sent

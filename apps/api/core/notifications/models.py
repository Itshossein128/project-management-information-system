"""In-app notification model (Sprint 4, Section 5)."""
from django.conf import settings
from django.db import models

from common.models import TimeStampedModel, UUIDModel


class NotificationType(models.TextChoices):
    REPORT_SUBMITTED = 'report_submitted', 'گزارش ارسال شد'
    REPORT_APPROVED = 'report_approved', 'گزارش تأیید شد'
    REPORT_REJECTED = 'report_rejected', 'گزارش رد شد'
    GENERIC = 'generic', 'عمومی'


class Notification(UUIDModel, TimeStampedModel):
    """A per-user in-app notification, optionally scoped to a project."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        default=NotificationType.GENERIC,
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default='')
    link = models.CharField(max_length=512, blank=True, default='')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.title} -> {self.user_id}'

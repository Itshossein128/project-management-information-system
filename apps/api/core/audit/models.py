from django.conf import settings
from django.db import models

from common.models import UUIDModel


class AuditLog(UUIDModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    http_method = models.CharField(max_length=10)
    path = models.CharField(max_length=512)
    resource_type = models.CharField(max_length=120, blank=True, default='')
    resource_id = models.UUIDField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        indexes = [
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

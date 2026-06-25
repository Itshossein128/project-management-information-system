from django.conf import settings
from django.db import models

from common.models import UUIDModel


class AlertCondition(models.TextChoices):
    GT = 'gt', 'Greater than'
    LT = 'lt', 'Less than'
    EQ = 'eq', 'Equal'
    GTE = 'gte', 'Greater than or equal'
    LTE = 'lte', 'Less than or equal'


class AlertRule(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alert_rules',
    )
    alert_type = models.CharField(max_length=60, blank=True, default='')
    threshold = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=AlertCondition.choices, blank=True, default='')
    recipient_ids = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'alert_rules'


class AlertLog(UUIDModel):
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='log_entries',
    )
    fired_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, default='')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
    )

    class Meta:
        db_table = 'alert_log'

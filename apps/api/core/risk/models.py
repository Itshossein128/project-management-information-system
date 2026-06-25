from django.conf import settings
from django.db import models

from common.models import UUIDModel


class EventType(models.TextChoices):
    DELAY = 'delay', 'Delay'
    BARRIER = 'barrier', 'Barrier'
    RISK = 'risk', 'Risk'
    CLAIM = 'claim', 'Claim'
    CHANGE_ORDER = 'change_order', 'Change order'


class Severity(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class RiskEvent(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='risk_events')
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_events',
    )
    event_date = models.DateField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    description = models.TextField(blank=True, default='')
    responsible_party = models.CharField(max_length=80, blank=True, default='')
    time_impact_days = models.IntegerField(null=True, blank=True)
    cost_impact = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    probability = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True, default='')
    status = models.CharField(max_length=20, default='open')
    corrective_action = models.TextField(blank=True, default='')
    target_resolution_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_risk_events',
    )

    class Meta:
        db_table = 'risk_events'

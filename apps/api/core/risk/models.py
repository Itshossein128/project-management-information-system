from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel


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


class BarrierCategory(models.TextChoices):
    EQUIPMENT_FAILURE = 'equipment_failure', 'خرابی تجهیزات'
    PAYMENT_DELAY = 'payment_delay', 'تأخیر پرداخت'
    DESIGN_CHANGE = 'design_change', 'تغییر طراحی'
    WEATHER = 'weather', 'شرایط جوی'
    SUBCONTRACTOR = 'subcontractor', 'پیمانکار'
    SAFETY = 'safety', 'ایمنی'
    OTHER = 'other', 'سایر'


class BarrierStatus(models.TextChoices):
    OPEN = 'open', 'باز'
    IN_PROGRESS = 'in_progress', 'در حال پیگیری'
    RESOLVED = 'resolved', 'رفع شده'


class RiskEvent(AuditSoftDeleteModel):
    """
    Represents an event logged against a project, which can be of various types
    such as delay, barrier, risk, claim, or change order.

    Tracks details including the event's impact on schedule and cost, its
    probability, severity, and current status (e.g., open, in progress, resolved).
    """

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
    category = models.CharField(max_length=30, choices=BarrierCategory.choices, blank=True, default='')
    impact_on_schedule = models.BooleanField(default=False)
    impact_on_cost = models.BooleanField(default=False)
    responsible_party = models.CharField(max_length=80, blank=True, default='')
    time_impact_days = models.IntegerField(null=True, blank=True)
    cost_impact = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    probability = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True, default='')
    status = models.CharField(max_length=20, choices=BarrierStatus.choices, default=BarrierStatus.OPEN)
    corrective_action = models.TextField(blank=True, default='')
    target_resolution_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_risk_events',
    )
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='barrier_assignments',
    )

    class Meta:
        db_table = 'risk_events'

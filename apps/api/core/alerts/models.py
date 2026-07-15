from django.conf import settings
from django.db import models

from common.models import UUIDModel


class AlertCondition(models.TextChoices):
    GT = 'gt', 'Greater than'
    LT = 'lt', 'Less than'
    EQ = 'eq', 'Equal'
    GTE = 'gte', 'Greater than or equal'
    LTE = 'lte', 'Less than or equal'


class AlertType(models.TextChoices):
    IPC_PAYMENT_OVERDUE = 'ipc_payment_overdue', 'IPC payment overdue'
    GUARANTEE_EXPIRING = 'guarantee_expiring', 'Guarantee expiring'
    BUDGET_OVERRUN = 'budget_overrun', 'Budget overrun'
    CASH_GAP_DETECTED = 'cash_gap_detected', 'Cash gap detected'
    LOW_STOCK = 'low_stock', 'Low stock'
    ACTIVITY_BEHIND_SCHEDULE = 'activity_behind_schedule', 'Activity behind schedule'
    MISSING_DAILY_REPORT = 'missing_daily_report', 'Missing daily report'
    DAILY_REPORT_NOT_APPROVED = 'daily_report_not_approved', 'Daily report not approved'
    BASELINE_NOT_SET = 'baseline_not_set', 'Baseline not set'
    SUBCONTRACTOR_AT_RISK = 'subcontractor_at_risk', 'Subcontractor at risk'
    SUBCONTRACTOR_SCORE_LOW = 'subcontractor_score_low', 'Subcontractor score low'
    CORRESPONDENCE_RESPONSE_DUE = 'correspondence_response_due', 'Correspondence response due'
    SYNC_CONFLICT_UNRESOLVED = 'sync_conflict_unresolved', 'Sync conflict unresolved'


class AlertRule(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alert_rules',
    )
    alert_type = models.CharField(max_length=60, choices=AlertType.choices, blank=True, default='')
    name = models.CharField(max_length=120, blank=True, default='')
    threshold = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=AlertCondition.choices, blank=True, default='')
    recipient_ids = models.JSONField(default=list, blank=True)
    notify_roles = models.CharField(max_length=200, blank=True, default='')
    cooldown_hours = models.PositiveIntegerField(default=24)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alert_rules'

    @property
    def threshold_value(self):
        return self.threshold


class AlertLog(UUIDModel):
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='log_entries',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alert_logs',
    )
    fired_at = models.DateTimeField(auto_now_add=True)
    trigger_reference = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField(blank=True, default='')
    notifications_sent = models.PositiveIntegerField(default=0)
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

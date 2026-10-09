from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel


class EventType(models.TextChoices):
    """Enumeration of various types of risk events."""
    DELAY = 'delay', 'Delay'
    BARRIER = 'barrier', 'Barrier'
    RISK = 'risk', 'Risk'
    ISSUE = 'issue', 'Issue'
    CLAIM = 'claim', 'Claim'
    CHANGE_ORDER = 'change_order', 'Change order'


class Severity(models.TextChoices):
    """Enumeration defining the severity levels of a risk event."""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class BarrierCategory(models.TextChoices):
    """Enumeration for categorizing the type of barrier."""
    EQUIPMENT_FAILURE = 'equipment_failure', 'خرابی تجهیزات'
    PAYMENT_DELAY = 'payment_delay', 'تأخیر پرداخت'
    DESIGN_CHANGE = 'design_change', 'تغییر طراحی'
    WEATHER = 'weather', 'شرایط جوی'
    SUBCONTRACTOR = 'subcontractor', 'پیمانکار'
    SAFETY = 'safety', 'ایمنی'
    OTHER = 'other', 'سایر'


class RiskStatus(models.TextChoices):
    """FR-RSK risk/issue lifecycle statuses."""
    OPEN = 'open', 'باز'
    UNDER_REVIEW = 'under_review', 'در بررسی'
    MITIGATED = 'mitigated', 'کاهش‌یافته'
    CLOSED = 'closed', 'بسته'
    RESIDUAL = 'residual', 'باقیمانده'


class BarrierStatus:
    """Legacy barrier status aliases (normalized to RiskStatus on write)."""

    OPEN = RiskStatus.OPEN
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'


class RiskActionStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    DONE = 'done', 'Done'


class InspectionStage(models.TextChoices):
    PLAN = 'plan', 'Plan'
    REQUEST = 'request', 'Request'
    RESULT = 'result', 'Result'


class InspectionResult(models.TextChoices):
    PASS = 'pass', 'Pass'
    FAIL = 'fail', 'Fail'
    CONDITIONAL = 'conditional', 'Conditional'
    PENDING = 'pending', 'Pending'


class NonconformityStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'


class CorrectiveActionStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    DONE = 'done', 'Done'


class HseEventKind(models.TextChoices):
    INCIDENT = 'incident', 'Incident'
    NEAR_MISS = 'near_miss', 'Near miss'


class HseEventStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'


class WorkPermitStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CLOSED = 'closed', 'Closed'
    EXPIRED = 'expired', 'Expired'


class RiskEvent(AuditSoftDeleteModel):
    """
    Model representing a risk, issue, barrier, or delay event in a project.
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
    cause = models.TextField(blank=True, default='')
    consequence = models.TextField(blank=True, default='')
    response = models.TextField(blank=True, default='')
    category = models.CharField(max_length=30, choices=BarrierCategory.choices, blank=True, default='')
    impact_on_schedule = models.BooleanField(default=False)
    impact_on_cost = models.BooleanField(default=False)
    impact_on_quality = models.BooleanField(default=False)
    impact_on_safety = models.BooleanField(default=False)
    impact_on_contract = models.BooleanField(default=False)
    impact_on_liquidity = models.BooleanField(default=False)
    responsible_party = models.CharField(max_length=80, blank=True, default='')
    time_impact_days = models.IntegerField(null=True, blank=True)
    cost_impact = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    probability = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    probability_level = models.PositiveSmallIntegerField(null=True, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True, default='')
    impact_severity_level = models.PositiveSmallIntegerField(null=True, blank=True)
    composite_score = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=RiskStatus.choices, default=RiskStatus.OPEN)
    corrective_action = models.TextField(blank=True, default='')
    target_resolution_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
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
    cost_item = models.ForeignKey(
        'cost_control.CostBreakdownNode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_risk_events',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_risk_events',
    )
    related_decision_ref = models.CharField(max_length=64, blank=True, default='')
    related_decision_note = models.TextField(blank=True, default='')
    related_daily_report = models.ForeignKey(
        'field_reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_risk_events',
    )
    related_correspondence = models.ForeignKey(
        'documents.Correspondence',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_risk_events',
    )

    class Meta:
        db_table = 'risk_events'


class RiskAction(AuditSoftDeleteModel):
    """Mitigation / follow-up action on a risk or issue."""

    risk_event = models.ForeignKey(
        RiskEvent,
        on_delete=models.CASCADE,
        related_name='actions',
    )
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_risk_actions',
    )
    status = models.CharField(
        max_length=10,
        choices=RiskActionStatus.choices,
        default=RiskActionStatus.OPEN,
    )

    class Meta:
        db_table = 'risk_actions'


class Inspection(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='inspections')
    wbs = models.ForeignKey('projects.WBS', on_delete=models.PROTECT, related_name='inspections')
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='responsible_inspections',
    )
    inspection_date = models.DateField()
    stage = models.CharField(
        max_length=20,
        choices=InspectionStage.choices,
        default=InspectionStage.RESULT,
    )
    result = models.CharField(
        max_length=20,
        choices=InspectionResult.choices,
        blank=True,
        default='',
    )
    description = models.TextField(blank=True, default='')
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
    )

    class Meta:
        db_table = 'inspections'


class Nonconformity(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='nonconformities')
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nonconformities',
    )
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nonconformities',
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=NonconformityStatus.choices,
        default=NonconformityStatus.OPEN,
    )
    raised_date = models.DateField()

    class Meta:
        db_table = 'nonconformities'


class CorrectiveAction(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='quality_corrective_actions',
    )
    nonconformity = models.ForeignKey(
        Nonconformity,
        on_delete=models.CASCADE,
        related_name='corrective_actions',
    )
    description = models.TextField()
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_corrective_actions',
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=CorrectiveActionStatus.choices,
        default=CorrectiveActionStatus.OPEN,
    )
    completed_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'corrective_actions'


class HseEvent(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='hse_events')
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hse_events',
    )
    kind = models.CharField(max_length=20, choices=HseEventKind.choices)
    event_date = models.DateField()
    description = models.TextField()
    severity = models.CharField(max_length=40, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=HseEventStatus.choices,
        default=HseEventStatus.OPEN,
    )

    class Meta:
        db_table = 'hse_events'


class WorkPermit(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='work_permits')
    permit_date = models.DateField()
    permit_type = models.CharField(max_length=80, blank=True, default='')
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_permits',
    )
    description = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=WorkPermitStatus.choices,
        default=WorkPermitStatus.ACTIVE,
    )

    class Meta:
        db_table = 'work_permits'


class SafetyTraining(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='safety_trainings',
    )
    training_date = models.DateField()
    topic = models.CharField(max_length=200)
    trainer_or_responsible = models.CharField(max_length=120, blank=True, default='')
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_trainings',
    )
    attendees_count = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'safety_trainings'

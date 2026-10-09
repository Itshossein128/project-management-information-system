from django.conf import settings
from django.db import models, transaction

from common.models import AuditSoftDeleteModel, TimeStampedModel, UUIDModel


class WorkingCalendar(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='working_calendars',
    )
    name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)
    work_monday = models.BooleanField(default=True)
    work_tuesday = models.BooleanField(default=True)
    work_wednesday = models.BooleanField(default=True)
    work_thursday = models.BooleanField(default=True)
    work_friday = models.BooleanField(default=True)
    work_saturday = models.BooleanField(default=False)
    work_sunday = models.BooleanField(default=False)

    class Meta:
        db_table = 'working_calendars'
        ordering = ['name']

    def __str__(self):
        return self.name


class CalendarException(AuditSoftDeleteModel):
    calendar = models.ForeignKey(
        WorkingCalendar,
        on_delete=models.CASCADE,
        related_name='exceptions',
    )
    exception_date = models.DateField()
    is_working = models.BooleanField(default=False)
    name = models.CharField(max_length=120, blank=True, default='')

    class Meta:
        db_table = 'calendar_exceptions'
        constraints = [
            models.UniqueConstraint(
                fields=['calendar', 'exception_date'],
                condition=models.Q(is_deleted=False),
                name='unique_active_calendar_exception_date',
            ),
        ]
        ordering = ['exception_date']

    def __str__(self):
        return f'{self.exception_date} ({self.calendar_id})'


class ScheduleChangeRequestStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ScheduleChangeRequest(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='schedule_change_requests',
    )
    base_baseline = models.ForeignKey(
        'schedule.BaselineSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_requests_as_base',
    )
    reason = models.TextField(blank=True, default='')
    milestone_impact = models.TextField(blank=True, default='')
    cost_impact = models.TextField(blank=True, default='')
    contract_impact = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=ScheduleChangeRequestStatus.choices,
        default=ScheduleChangeRequestStatus.DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_change_requests_decided',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True, default='')
    resulting_baseline = models.ForeignKey(
        'schedule.BaselineSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_requests_resulting',
    )

    class Meta:
        db_table = 'schedule_change_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'SCR {self.id} ({self.status})'


class ScheduleChangeItem(UUIDModel):
    change_request = models.ForeignKey(
        ScheduleChangeRequest,
        on_delete=models.CASCADE,
        related_name='items',
    )
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.CASCADE,
        related_name='schedule_change_items',
    )
    proposed_planned_start = models.DateField(null=True, blank=True)
    proposed_planned_finish = models.DateField(null=True, blank=True)
    proposed_duration_days = models.IntegerField(null=True, blank=True)
    proposed_forecast_start = models.DateField(null=True, blank=True)
    proposed_forecast_finish = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'schedule_change_items'


class BaselineSchedule(AuditSoftDeleteModel):
    """Approved/locked baseline versions. Soft-delete only — never hard-delete history."""

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='baselines')
    version_name = models.CharField(max_length=60, blank=True, default='')
    approved_at = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_baselines',
    )
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_baselines',
    )
    source_change_request = models.ForeignKey(
        'schedule.ScheduleChangeRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produced_baselines',
    )

    class Meta:
        db_table = 'baseline_schedules'

    def save(self, *args, **kwargs):
        becoming_current = False
        if self.pk:
            try:
                old = BaselineSchedule.all_objects.get(pk=self.pk)
                becoming_current = self.is_current and not old.is_current
            except BaselineSchedule.DoesNotExist:
                becoming_current = self.is_current
        else:
            becoming_current = self.is_current

        if self.is_current:
            with transaction.atomic():
                BaselineSchedule.objects.filter(
                    project_id=self.project_id,
                    is_current=True,
                ).exclude(pk=self.pk).update(is_current=False)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

        if becoming_current:
            from schedule.tasks import compute_baseline_progress

            compute_baseline_progress.delay(str(self.pk))

    def delete(self, using=None, keep_parents=False):
        """Hard delete is forbidden; always soft-delete to preserve history (FR-009)."""
        self.soft_delete()


class BaselineActivity(UUIDModel):
    """Snapshot row owned by a baseline. Retained while baseline exists (incl. soft-deleted parent)."""

    baseline = models.ForeignKey(BaselineSchedule, on_delete=models.CASCADE, related_name='baseline_activities')
    activity = models.ForeignKey('projects.Activity', on_delete=models.CASCADE, related_name='baseline_entries')
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    planned_duration = models.IntegerField(null=True, blank=True)
    planned_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    planned_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    total_float = models.IntegerField(null=True, blank=True)
    free_float = models.IntegerField(null=True, blank=True)
    is_critical = models.BooleanField(default=False)

    class Meta:
        db_table = 'baseline_activities'


class ActivityProgress(UUIDModel):
    class ProgressSource(models.TextChoices):
        DAILY_REPORT = 'daily_report', 'Daily report'
        MANUAL = 'manual', 'Manual'

    activity = models.ForeignKey('projects.Activity', on_delete=models.CASCADE, related_name='progress_entries')
    report_date = models.DateField()
    planned_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    actual_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cumulative_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    deviation = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=ProgressSource.choices,
        default=ProgressSource.DAILY_REPORT,
    )
    notes = models.TextField(blank=True, default='')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_progress_updates',
    )
    # FR-PRG four-way progress: actual_progress is the cumulative recorded value.
    period_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    approved_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    measurement_version = models.ForeignKey(
        'schedule.ActivityMeasurementVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progress_entries',
    )
    technical_approved_at = models.DateTimeField(null=True, blank=True)
    technical_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='technically_approved_progress',
    )
    evidence_refs = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activity_progress'
        unique_together = [['activity', 'report_date']]


class MeasurementMethod(models.TextChoices):
    QUANTITY = 'quantity', 'Quantity'
    WEIGHTED_MILESTONES = 'weighted_milestones', 'Weighted milestones'
    EVIDENCE_PERCENT = 'evidence_percent', 'Evidence percent'


class MeasurementStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    APPROVED = 'approved', 'Approved'


class ActivityMeasurementDefinition(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='measurement_definitions',
    )
    activity = models.OneToOneField(
        'projects.Activity',
        on_delete=models.CASCADE,
        related_name='measurement_definition',
    )
    method = models.CharField(
        max_length=30,
        choices=MeasurementMethod.choices,
        default=MeasurementMethod.QUANTITY,
    )
    status = models.CharField(
        max_length=20,
        choices=MeasurementStatus.choices,
        default=MeasurementStatus.DRAFT,
    )
    total_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='measurement_definitions',
    )
    milestones = models.JSONField(default=list, blank=True)
    evidence_rules = models.TextField(blank=True, default='')
    pending_change_reason = models.TextField(blank=True, default='')
    current_version = models.ForeignKey(
        'schedule.ActivityMeasurementVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_measurement_definitions',
    )

    class Meta:
        db_table = 'activity_measurement_definitions'

    def __str__(self):
        return f'{self.activity_id}:{self.method}:{self.status}'


class ActivityMeasurementVersion(UUIDModel):
    definition = models.ForeignKey(
        ActivityMeasurementDefinition,
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    method = models.CharField(max_length=30, choices=MeasurementMethod.choices)
    basis_snapshot = models.JSONField(default=dict, blank=True)
    change_reason = models.TextField(blank=True, default='')
    approved_at = models.DateTimeField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_measurement_versions',
    )

    class Meta:
        db_table = 'activity_measurement_versions'
        ordering = ['version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['definition', 'version_number'],
                name='uniq_measurement_version_number',
            ),
        ]


class ActivityQuantityChangeStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ActivityQuantityChange(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='activity_quantity_changes',
    )
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.CASCADE,
        related_name='quantity_changes',
    )
    previous_total = models.DecimalField(max_digits=18, decimal_places=4)
    new_total = models.DecimalField(max_digits=18, decimal_places=4)
    status = models.CharField(
        max_length=20,
        choices=ActivityQuantityChangeStatus.choices,
        default=ActivityQuantityChangeStatus.DRAFT,
    )
    reason = models.TextField(blank=True, default='')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_quantity_changes',
    )

    class Meta:
        db_table = 'activity_quantity_changes'
        ordering = ['-created_at']


class PeriodReportKind(models.TextChoices):
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class PeriodReportStatus(models.TextChoices):
    GENERATED = 'generated', 'Generated'
    SUPERSEDED = 'superseded', 'Superseded'


class ProjectPeriodReport(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='period_reports',
    )
    kind = models.CharField(max_length=20, choices=PeriodReportKind.choices)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PeriodReportStatus.choices,
        default=PeriodReportStatus.GENERATED,
    )
    generated_at = models.DateTimeField()
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_period_reports',
    )
    superseded_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supersedes',
    )
    title = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        db_table = 'project_period_reports'
        ordering = ['-period_start', '-generated_at']
        indexes = [
            models.Index(fields=['project', 'kind', 'period_start', 'period_end'], name='ppr_project_kind_period_idx'),
        ]

    def __str__(self):
        return self.title or f'{self.kind} {self.period_start}..{self.period_end}'


class FigureValueStatus(models.TextChoices):
    RECORDED = 'recorded', 'Recorded'
    NOT_RECORDED = 'not_recorded', 'Not recorded'


class PeriodReportFigure(UUIDModel):
    report = models.ForeignKey(
        ProjectPeriodReport,
        on_delete=models.CASCADE,
        related_name='figures',
    )
    section = models.CharField(max_length=60)
    label_key = models.CharField(max_length=120)
    value = models.JSONField(null=True, blank=True)
    value_status = models.CharField(
        max_length=20,
        choices=FigureValueStatus.choices,
        default=FigureValueStatus.NOT_RECORDED,
    )
    source_type = models.CharField(max_length=40, blank=True, default='')
    source_id = models.UUIDField(null=True, blank=True)
    source_path = models.CharField(max_length=255, blank=True, default='')
    source_approved = models.BooleanField(default=False)
    last_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'period_report_figures'
        ordering = ['section']


class PeriodReportFigureOverride(UUIDModel, TimeStampedModel):
    figure = models.ForeignKey(
        PeriodReportFigure,
        on_delete=models.CASCADE,
        related_name='overrides',
    )
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    reason = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='period_figure_overrides',
    )

    class Meta:
        db_table = 'period_report_figure_overrides'
        ordering = ['-created_at']


class MspImportStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    DONE = 'done', 'Done'
    FAILED = 'failed', 'Failed'


class BaseImportJob(UUIDModel, TimeStampedModel):
    task_id = models.CharField(max_length=64, blank=True, default='')
    status = models.CharField(max_length=20, choices=MspImportStatus.choices, default=MspImportStatus.PENDING)
    progress_pct = models.PositiveSmallIntegerField(default=0)
    filename = models.CharField(max_length=255, blank=True, default='')
    replace_existing = models.BooleanField(default=False)
    file_data = models.BinaryField(null=True, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        abstract = True


class MspImportJob(BaseImportJob):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='msp_import_jobs')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='msp_import_jobs',
    )

    class Meta:
        db_table = 'msp_import_jobs'
        ordering = ['-created_at']


class P6ImportJob(BaseImportJob):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='p6_import_jobs')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='p6_import_jobs',
    )

    class Meta:
        db_table = 'p6_import_jobs'
        ordering = ['-created_at']

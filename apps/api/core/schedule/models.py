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

    class Meta:
        db_table = 'activity_progress'
        unique_together = [['activity', 'report_date']]


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

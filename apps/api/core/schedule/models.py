from django.conf import settings
from django.db import models

from common.models import UUIDModel


class BaselineSchedule(UUIDModel):
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

    class Meta:
        db_table = 'baseline_schedules'


class BaselineActivity(UUIDModel):
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
    activity = models.ForeignKey('projects.Activity', on_delete=models.CASCADE, related_name='progress_entries')
    report_date = models.DateField()
    planned_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    actual_progress = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cumulative_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    deviation = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
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

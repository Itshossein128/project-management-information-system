from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel
from field_reports.models import WeatherCondition


class Discipline(models.TextChoices):
    CIVIL = 'civil', 'Civil'
    ELECTRICAL = 'electrical', 'Electrical'
    MECHANICAL = 'mechanical', 'Mechanical'
    PLUMBING = 'plumbing', 'Plumbing'
    HVAC = 'hvac', 'HVAC'
    FINISHING = 'finishing', 'Finishing'


class SubReportStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class DisciplineSubReport(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='discipline_sub_reports')
    report_date = models.DateField()
    discipline = models.CharField(max_length=20, choices=Discipline.choices, default=Discipline.CIVIL)
    weather_condition = models.CharField(max_length=20, choices=WeatherCondition.choices, blank=True, default='')
    form_code = models.CharField(max_length=60, blank=True, default='')
    revision_number = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=SubReportStatus.choices, default=SubReportStatus.DRAFT)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_sub_reports',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sub_reports',
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    linked_daily_report = models.ForeignKey(
        'field_reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discipline_sub_reports',
    )

    class Meta:
        db_table = 'discipline_sub_reports'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'report_date', 'discipline'],
                condition=models.Q(is_deleted=False),
                name='unique_active_sub_report_per_discipline_date',
            ),
        ]


class DisciplineSubReportActivity(UUIDModel):
    sub_report = models.ForeignKey(DisciplineSubReport, on_delete=models.CASCADE, related_name='activities')
    row_number = models.PositiveIntegerField()
    shift = models.CharField(max_length=20)
    crew_name = models.CharField(max_length=120)
    foreman_count = models.PositiveIntegerField(null=True, blank=True)
    worker_count = models.PositiveIntegerField(null=True, blank=True)
    zone = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    activity_description = models.TextField()
    unit = models.CharField(max_length=40, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    execution_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_report_activities',
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_activities'
        ordering = ['row_number']

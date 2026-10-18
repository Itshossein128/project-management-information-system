from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel
from field_reports.models import LaborCategory, SiteStatus, WeatherCondition


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


class SubReportNoteType(models.TextChoices):
    ISSUE = 'issue', 'Issue'
    VISIT = 'visit', 'Visit'
    OTHER = 'other', 'Other'


DEFAULT_EXPECTED_DISCIPLINES = (
    Discipline.CIVIL,
    Discipline.ELECTRICAL,
    Discipline.MECHANICAL,
)


class DisciplineSubReport(AuditSoftDeleteModel):
    """
    Represents a discipline-specific sub-report within a project, which can optionally
    be linked to a daily report. It tracks the status of the report (draft, submitted,
    approved, rejected) along with relevant environmental and auditing details.
    """
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='discipline_sub_reports')
    report_date = models.DateField()
    discipline = models.CharField(max_length=20, choices=Discipline.choices, default=Discipline.CIVIL)
    weather_condition = models.CharField(max_length=20, choices=WeatherCondition.choices, blank=True, default='')
    site_status = models.CharField(
        max_length=10, choices=SiteStatus.choices, default=SiteStatus.ACTIVE,
    )
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
    """
    Represents an individual work activity tracked within a specific discipline sub-report.
    It captures details about the workforce (crew, foreman, workers), location (zone, block, floor),
    and execution details (quantity, percentage) mapped to a project schedule activity.
    """
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


class DisciplineSubReportLabor(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='labor_entries',
    )
    labor_category = models.CharField(max_length=10, choices=LaborCategory.choices)
    job_title = models.CharField(max_length=120)
    present_count = models.PositiveIntegerField(default=0)
    leave_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_labor'


class DisciplineSubReportMaterial(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='material_entries',
    )
    material_description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit = models.CharField(max_length=40)
    notes = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_materials'


class DisciplineSubReportConcrete(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='concrete_entries',
    )
    concrete_description = models.CharField(max_length=120)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=3)
    zone = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_concrete'


class DisciplineSubReportGeneralActivity(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='general_activities',
    )
    activity_description = models.TextField()
    location = models.CharField(max_length=120, blank=True, default='')
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_general_activities'


class DisciplineSubReportNote(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='notes',
    )
    note_type = models.CharField(max_length=20, choices=SubReportNoteType.choices)
    text = models.TextField()
    row_number = models.PositiveIntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_notes'
        ordering = ['row_number']

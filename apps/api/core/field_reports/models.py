from django.conf import settings
from django.db import models

from common.jalali import persian_day_of_week
from common.models import AuditSoftDeleteModel, UUIDModel


class ReportShift(models.TextChoices):
    DAY = 'day', 'Day'
    NIGHT = 'night', 'Night'
    FULL = 'full', 'Full'


class ReportStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class WeatherCondition(models.TextChoices):
    SUNNY = 'sunny', 'آفتابی'
    CLOUDY = 'cloudy', 'ابری'
    PARTLY_CLOUDY = 'partly_cloudy', 'نیمه‌ابری'
    RAINY = 'rainy', 'بارانی'
    STORMY = 'stormy', 'طوفانی'
    SNOWY = 'snowy', 'برفی'
    FOGGY = 'foggy', 'مه‌آلود'


class SiteStatus(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    INACTIVE = 'inactive', 'غیرفعال'


class ActivityRowShift(models.TextChoices):
    SHIFT_1 = 'shift_1', 'شیفت ۱'
    SHIFT_2 = 'shift_2', 'شیفت ۲'
    SHIFT_3 = 'shift_3', 'شیفت ۳'


class LaborCategory(models.TextChoices):
    INDIRECT = 'indirect', 'ستادی'
    DIRECT = 'direct', 'اجرایی'


class EquipmentStatus(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    STANDBY = 'standby', 'آماده'
    BROKEN = 'broken', 'خراب'


class OwnershipType(models.TextChoices):
    OWNED = 'owned', 'تملیکی'
    RENTED = 'rented', 'اجاره‌ای'


class MaterialTransactionType(models.TextChoices):
    RECEIPT = 'receipt', 'وارده'
    ISSUE = 'issue', 'مصرف شده'
    WASTE = 'waste', 'ضایعات'


class IncidentType(models.TextChoices):
    SAFETY = 'safety', 'Safety'
    QUALITY = 'quality', 'Quality'
    ENVIRONMENTAL = 'environmental', 'Environmental'
    STOPPAGE = 'stoppage', 'Stoppage'
    VISITOR = 'visitor', 'Visitor'


class ChildRowModel(UUIDModel):
    """Abstract base for daily-report child rows with soft delete."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class DailyReport(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    shift = models.CharField(max_length=10, choices=ReportShift.choices, default=ReportShift.FULL)
    weather_condition = models.CharField(
        max_length=20,
        choices=WeatherCondition.choices,
        null=True,
        blank=True,
    )
    temp_max = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    temp_min = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    site_status = models.CharField(max_length=10, choices=SiteStatus.choices, default=SiteStatus.ACTIVE)
    general_notes = models.TextField(blank=True, default='')

    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prepared_reports',
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_reports',
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports',
    )

    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')

    synced_from_offline = models.BooleanField(default=False)
    local_id = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        db_table = 'daily_reports'
        ordering = ['-report_date']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'report_date', 'shift'],
                condition=models.Q(is_deleted=False),
                name='unique_active_daily_report_per_date_shift',
            ),
        ]


class DailyReportActivity(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='activities')
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activities',
    )
    activity_description = models.TextField()
    shift = models.CharField(max_length=10, choices=ActivityRowShift.choices)
    subcontractor_name = models.CharField(max_length=120, blank=True, default='')
    subcontractor_ref = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activities',
    )
    headcount = models.PositiveIntegerField(null=True, blank=True)
    zone = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    location_detail = models.CharField(max_length=120, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    quantity_measured = models.BooleanField(default=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    execution_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    photo_file = models.ForeignKey(
        'storage.StoredFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activities',
    )

    class Meta:
        db_table = 'daily_report_activities'


class DailyReportLabor(ChildRowModel):
    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='labor_entries',
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='standalone_labor_entries',
        null=True,
        blank=True,
    )
    report_date = models.DateField(null=True, blank=True)
    labor_category = models.CharField(max_length=10, choices=LaborCategory.choices)
    job_title = models.CharField(max_length=120)
    custom_title = models.CharField(max_length=120, blank=True, default='')
    shift_1_count = models.PositiveIntegerField(default=0)
    shift_2_count = models.PositiveIntegerField(default=0)
    shift_3_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    work_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'daily_report_labor'
        constraints = [
            models.UniqueConstraint(
                fields=['report', 'labor_category', 'job_title'],
                condition=models.Q(is_deleted=False, report__isnull=False),
                name='unique_active_labor_row',
            ),
            models.UniqueConstraint(
                fields=['project', 'report_date', 'labor_category', 'job_title'],
                condition=models.Q(is_deleted=False, report__isnull=True),
                name='unique_standalone_labor_row',
            ),
        ]

    def save(self, *args, **kwargs):
        self.total_count = (
            (self.shift_1_count or 0) + (self.shift_2_count or 0) + (self.shift_3_count or 0)
        )
        if self.report_id and not self.report_date:
            self.report_date = self.report.report_date
        if self.report_id and not self.project_id:
            self.project_id = self.report.project_id
        super().save(*args, **kwargs)


class DailyReportEquipment(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='equipment_entries')
    equipment = models.ForeignKey(
        'field_reports.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_entries',
    )
    equipment_name = models.CharField(max_length=120)
    equipment_ref = models.CharField(max_length=60, blank=True, default='')
    shift = models.CharField(max_length=10, choices=ReportShift.choices)
    status = models.CharField(max_length=10, choices=EquipmentStatus.choices)
    ownership_type = models.CharField(max_length=10, choices=OwnershipType.choices)
    work_start = models.TimeField(null=True, blank=True)
    work_end = models.TimeField(null=True, blank=True)
    repair_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    idle_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    idle_reason = models.TextField(blank=True, default='')
    productive_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_equipment',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_report_equipment'


class DailyReportMaterial(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='material_entries')
    material_ref = models.ForeignKey(
        'resources.Material',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_materials',
    )
    material_description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40)
    transaction_type = models.CharField(max_length=10, choices=MaterialTransactionType.choices)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_materials',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_report_materials'


class DailyReportConcreteLog(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='concrete_logs')
    concrete_description = models.CharField(max_length=120)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=3)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_concrete_logs',
    )
    zone = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_report_concrete_logs'


class DailyReportLaborCamp(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='labor_camp_entries')
    connex_number = models.CharField(max_length=60)
    subcontractor_name = models.CharField(max_length=120)
    total_residents = models.PositiveIntegerField()
    present_count = models.PositiveIntegerField()
    on_leave_count = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

    class Meta:
        db_table = 'daily_report_labor_camp'


class DailyReportIncident(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='incidents')
    incident_type = models.CharField(max_length=40, choices=IncidentType.choices)
    description = models.TextField()
    corrective_action = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_report_incidents'


class LaborJobTitle(UUIDModel):
    """Seeded reference list of fixed job titles for the labor grid."""

    category = models.CharField(max_length=10, choices=LaborCategory.choices)
    title = models.CharField(max_length=120)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'labor_job_titles'
        ordering = ['category', 'display_order']
        unique_together = [['category', 'title']]


class WeatherLog(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='weather_logs')
    log_date = models.DateField()
    day_of_week = models.CharField(max_length=20, blank=True, default='')
    temp_max = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    temp_min = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weather_condition = models.CharField(max_length=20, choices=WeatherCondition.choices)
    site_status = models.CharField(max_length=10, choices=SiteStatus.choices, default=SiteStatus.ACTIVE)

    class Meta:
        db_table = 'weather_logs'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'log_date'],
                condition=models.Q(is_deleted=False),
                name='unique_active_weather_log_per_date',
            ),
        ]
        ordering = ['-log_date']

    def save(self, *args, **kwargs):
        if self.log_date:
            self.day_of_week = persian_day_of_week(self.log_date)
        super().save(*args, **kwargs)


class LaborCampReport(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='labor_camp_reports')
    report_date = models.DateField()
    connex_number = models.CharField(max_length=60)
    subcontractor_name = models.CharField(max_length=120)
    total_residents = models.PositiveIntegerField()
    present_count = models.PositiveIntegerField()
    on_leave_count = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

    class Meta:
        db_table = 'labor_camp_reports'
        ordering = ['-report_date', 'connex_number']


class Equipment(AuditSoftDeleteModel):
    """Project equipment registry (master list)."""

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='equipment_registry')
    equipment_code = models.CharField(max_length=30)
    equipment_name = models.CharField(max_length=120)
    equipment_type = models.CharField(max_length=80, blank=True, default='')
    ownership_type = models.CharField(max_length=10, choices=OwnershipType.choices, default=OwnershipType.OWNED)
    plate_number = models.CharField(max_length=30, blank=True, default='')
    default_hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'equipment_registry'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'equipment_code'],
                name='uniq_equipment_project_code',
            ),
        ]
        ordering = ['equipment_name']

    def __str__(self):
        return self.equipment_name


class EquipmentLog(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='equipment_logs')
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    log_date = models.DateField()
    equipment_name = models.CharField(max_length=120)
    equipment_ref = models.CharField(max_length=60, blank=True, default='')
    shift = models.CharField(max_length=10, choices=ReportShift.choices)
    status = models.CharField(max_length=10, choices=EquipmentStatus.choices)
    ownership_type = models.CharField(max_length=10, choices=OwnershipType.choices)
    work_start = models.TimeField(null=True, blank=True)
    work_end = models.TimeField(null=True, blank=True)
    repair_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    idle_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    idle_reason = models.TextField(blank=True, default='')
    productive_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_logs',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'equipment_logs'
        ordering = ['-log_date', 'equipment_name']


class SyncConflictLog(UUIDModel):
    """Unresolved offline sync conflict tracked for alert engine."""

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sync_conflict_logs',
    )
    local_id = models.CharField(max_length=64, blank=True, default='')
    daily_report = models.ForeignKey(
        'field_reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sync_conflict_logs',
    )
    conflict_reason = models.TextField()
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sync_conflict_logs'
        indexes = [
            models.Index(fields=['project', 'resolved_at'], name='synclog_project_resolved_idx'),
        ]

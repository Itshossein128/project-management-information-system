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
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class DailyReport(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    shift = models.CharField(max_length=10, choices=ReportShift.choices, default=ReportShift.FULL)
    weather = models.CharField(max_length=40, blank=True, default='')
    temperature_min = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    temperature_max = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    general_notes = models.TextField(blank=True, default='')
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prepared_daily_reports',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_daily_reports',
    )
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    synced_from_offline = models.BooleanField(default=False)

    class Meta:
        db_table = 'daily_reports'
        unique_together = [['project', 'report_date', 'shift']]


class DailyActivity(UUIDModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='activities')
    activity = models.ForeignKey('projects.Activity', on_delete=models.CASCADE, related_name='daily_activities')
    work_front = models.CharField(max_length=120, blank=True, default='')
    executed_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_activities'


class DailyLabor(UUIDModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='labor_entries')
    labor_type = models.CharField(max_length=60, blank=True, default='')
    discipline = models.CharField(max_length=60, blank=True, default='')
    headcount = models.IntegerField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_labor',
    )

    class Meta:
        db_table = 'daily_labor'


class DailyEquipment(UUIDModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='equipment_entries')
    equipment_type = models.CharField(max_length=80, blank=True, default='')
    equipment_code = models.CharField(max_length=30, blank=True, default='')
    work_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    idle_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    idle_reason = models.TextField(blank=True, default='')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_equipment_operations',
    )
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_equipment',
    )
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'daily_equipment'


class DailyMaterialUsage(UUIDModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='material_usage')
    material = models.ForeignKey('resources.Material', on_delete=models.CASCADE, related_name='daily_usage')
    quantity_used = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_material_usage',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_material_usage'


class IncidentType(models.TextChoices):
    SAFETY = 'safety', 'Safety'
    QUALITY = 'quality', 'Quality'
    ENVIRONMENTAL = 'environmental', 'Environmental'
    STOPPAGE = 'stoppage', 'Stoppage'
    VISITOR = 'visitor', 'Visitor'


class DailyIncident(UUIDModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='incidents')
    incident_type = models.CharField(max_length=40, choices=IncidentType.choices)
    description = models.TextField(blank=True, default='')
    corrective_action = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_incidents'


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

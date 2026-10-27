from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
    CLEAR = 'clear', 'آفتابی / صاف'
    CLOUDY = 'cloudy', 'ابری'
    RAINY = 'rainy', 'بارانی'
    SNOWY = 'snowy', 'برفی'
    STORMY = 'stormy', 'طوفانی / گرد و غبار'


class InactivityReason(models.TextChoices):
    WEATHER = 'weather', 'نامساعد بودن شرایط جوی'
    HOLIDAY = 'holiday', 'تعطیل رسمی / تقویمی'
    STRIKE_OR_DISPUTE = 'strike_or_dispute', 'اختلاف یا اعتصاب'
    CLIENT_STOP_ORDER = 'client_stop_order', 'دستور توقف کارفرما / مشاور'
    SAFETY_INCIDENT = 'safety_incident', 'حادثه ایمنی'


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
    RETURN = 'return', 'برگشتی'


class IncidentType(models.TextChoices):
    SAFETY = 'safety', 'Safety'
    QUALITY = 'quality', 'Quality'
    ENVIRONMENTAL = 'environmental', 'Environmental'
    STOPPAGE = 'stoppage', 'Stoppage'
    VISITOR = 'visitor', 'Visitor'
    SITE_INSTRUCTION = 'site_instruction', 'Site instruction'
    BARRIER = 'barrier', 'Barrier'


class CorrectionRequestStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    CANCELLED = 'cancelled', 'Cancelled'
    REJECTED = 'rejected', 'Rejected'


class SamplingState(models.TextChoices):
    NOT_SAMPLED = 'not_sampled', 'Not sampled'
    SAMPLING_DECLARED = 'sampling_declared', 'Sampling declared'


class ReconciliationStatus(models.TextChoices):
    MATCH = 'match', 'Match'
    MISMATCH = 'mismatch', 'Mismatch'
    INSUFFICIENT_DATA = 'insufficient_data', 'Insufficient data'


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
    work_front = models.CharField(max_length=120, blank=True, default='')
    location_notes = models.CharField(max_length=200, blank=True, default='')
    weather_condition = models.CharField(
        max_length=20,
        choices=WeatherCondition.choices,
        null=True,
        blank=True,
    )
    temp_max = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(-40), MaxValueValidator(60)],
    )
    temp_min = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(-40), MaxValueValidator(60)],
    )
    site_status = models.CharField(max_length=10, choices=SiteStatus.choices, default=SiteStatus.ACTIVE)
    inactivity_reason = models.CharField(
        max_length=30,
        choices=InactivityReason.choices,
        blank=True,
        default='',
    )
    weather_impact_notes = models.TextField(blank=True, default='')
    general_notes = models.TextField(blank=True, default='')
    management_opinion = models.TextField(blank=True, default='')
    weather_override = models.BooleanField(default=False)
    site_status_override = models.BooleanField(default=False)
    is_auto_summary = models.BooleanField(default=False)
    aggregated_at = models.DateTimeField(null=True, blank=True)

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

    lineage_id = models.UUIDField(null=True, blank=True, db_index=True)
    version_number = models.PositiveIntegerField(default=1)
    supersedes = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='superseded_by_reports',
    )
    is_current = models.BooleanField(default=True)

    synced_from_offline = models.BooleanField(default=False)
    local_id = models.CharField(max_length=36, null=True, blank=True)

    # Feature 032: canonical completeness binding + rebuild fingerprint.
    reporting_configuration = models.ForeignKey(
        'project_templates.ProjectReportingConfiguration',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_reports',
    )
    aggregation_fingerprint = models.CharField(max_length=64, blank=True, default='')

    @property
    def issues(self):
        """Derived issue/barrier rows (feature 033). HSE rows stay on ``hse_incidents``."""
        return self.incidents.filter(incident_type__in=['issue', 'barrier'])

    @property
    def hse_incidents(self):
        return self.incidents.filter(incident_type='safety')

    class Meta:
        db_table = 'daily_reports'
        ordering = ['-report_date']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'report_date', 'shift'],
                condition=models.Q(is_deleted=False, is_current=True),
                name='unique_current_daily_report_per_date_shift',
            ),
        ]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        errors = {}
        if self.temp_min is not None and (self.temp_min < -40 or self.temp_min > 60):
            errors['temp_min'] = 'دمای کمینه باید بین ۴۰- تا ۶۰+ درجه سانتی‌گراد باشد.'
        if self.temp_max is not None and (self.temp_max < -40 or self.temp_max > 60):
            errors['temp_max'] = 'دمای بیشینه باید بین ۴۰- تا ۶۰+ درجه سانتی‌گراد باشد.'
        if self.temp_min is not None and self.temp_max is not None and self.temp_max < self.temp_min:
            errors['temp_max'] = 'دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.'
        if self.site_status == SiteStatus.INACTIVE and not self.inactivity_reason:
            errors['inactivity_reason'] = 'در صورت تعطیلی کارگاه، انتخاب علت الزامی است.'
        if self.site_status == SiteStatus.ACTIVE and self.inactivity_reason:
            self.inactivity_reason = ''
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.site_status == SiteStatus.ACTIVE and self.inactivity_reason:
            self.inactivity_reason = ''
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and self.lineage_id is None:
            type(self).objects.filter(pk=self.pk).update(lineage_id=self.id)
            self.lineage_id = self.id

    @property
    def is_locked(self) -> bool:
        return self.status == ReportStatus.APPROVED


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
    contractor_ref = models.ForeignKey(
        'projects.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activities_as_contractor',
    )
    # Feature 033 (data-model §3.1): crew and contractor are separate derived
    # columns (never merged), headcount keeps its foreman/worker components and
    # parcel joins the location set.
    crew_name = models.CharField(max_length=120, blank=True, default='')
    headcount = models.PositiveIntegerField(null=True, blank=True)
    foreman_count = models.PositiveIntegerField(null=True, blank=True)
    worker_count = models.PositiveIntegerField(null=True, blank=True)
    parcel = models.CharField(max_length=60, null=True, blank=True)
    zone = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    location_detail = models.CharField(max_length=120, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    quantity_measured = models.BooleanField(default=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    execution_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activity_responsibilities',
    )
    responsible_name = models.CharField(max_length=120, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    photo_file = models.ForeignKey(
        'storage.StoredFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_activities',
    )
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_activities',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=False)

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
    contractor_ref = models.ForeignKey(
        'projects.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_labor_entries',
    )
    contractor_name = models.CharField(max_length=120, blank=True, default='')
    shift_1_count = models.PositiveIntegerField(default=0)
    shift_2_count = models.PositiveIntegerField(default=0)
    shift_3_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    work_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    absence_count = models.PositiveIntegerField(null=True, blank=True)
    # Feature 033 (data-model §3.2): DailyReportDerivedSource is the source of
    # truth; the legacy columns above stay as compat aliases only. The marker
    # records that the derived row's source set was written completely.
    source_set_complete = models.BooleanField(default=False)
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_labor',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=False)

    class Meta:
        db_table = 'daily_report_labor'
        constraints = [
            models.UniqueConstraint(
                fields=['report', 'labor_category', 'job_title', 'contractor_ref'],
                condition=models.Q(is_deleted=False, report__isnull=False),
                name='unique_active_labor_row',
            ),
            models.UniqueConstraint(
                fields=['project', 'report_date', 'labor_category', 'job_title', 'contractor_ref'],
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


class BaseEquipmentEntry(models.Model):
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
    notes = models.TextField(blank=True, default='')

    class Meta:
        abstract = True


class DailyReportEquipment(ChildRowModel, BaseEquipmentEntry):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='equipment_entries')
    equipment = models.ForeignKey(
        'field_reports.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_entries',
    )
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_equipment',
    )

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
    consumption_location = models.CharField(max_length=120, blank=True, default='')
    # Feature 033 (data-model §3.4): receipts-only display is computed from the
    # resolved-vs-unresolved marker; reconciliation fields are written by the
    # document-anchored reconciliation service, never by product users.
    supplier = models.CharField(max_length=120, blank=True, default='')
    warehouse_document_reference = models.CharField(max_length=120, blank=True, default='')
    receipt_resolved = models.BooleanField(null=True, blank=True)
    reconciliation_status = models.CharField(
        max_length=20, choices=ReconciliationStatus.choices, null=True, blank=True,
    )
    reconciliation_document_id = models.CharField(max_length=64, blank=True, default='')
    reconciliation_checked_at = models.DateTimeField(null=True, blank=True)
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_materials',
    )
    notes = models.TextField(blank=True, default='')
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_materials',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=False)

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
    # Feature 033 (data-model §3.5): derived pour rows keep the full §2.5
    # column set so the summary is as rich as the source.
    structural_element = models.CharField(max_length=120, blank=True, default='')
    parcel = models.CharField(max_length=60, blank=True, default='')
    batching_plant = models.CharField(max_length=120, blank=True, default='')
    truck_delivery_note_number = models.CharField(max_length=60, blank=True, default='')
    lab_sample_code = models.CharField(max_length=60, blank=True, default='')
    sampling_state = models.CharField(
        max_length=20, choices=SamplingState.choices, blank=True, default='',
    )
    test_sheet_count = models.PositiveIntegerField(null=True, blank=True)
    qc_inspection = models.ForeignKey(
        'risk.Inspection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_concrete_pours',
    )
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_concrete',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=False)

    class Meta:
        db_table = 'daily_report_concrete_logs'


class BaseLaborCampEntry(models.Model):
    connex_number = models.CharField(max_length=60)
    subcontractor_name = models.CharField(max_length=120)
    contractor_ref = models.ForeignKey(
        'projects.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_contractor_rows',
    )
    total_residents = models.PositiveIntegerField()
    present_count = models.PositiveIntegerField()
    on_leave_count = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

    class Meta:
        abstract = True


class DailyReportLaborCamp(ChildRowModel, BaseLaborCampEntry):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='labor_camp_entries')

    class Meta:
        db_table = 'daily_report_labor_camp'


class HseSeverity(models.TextChoices):
    MINOR = 'minor', 'Minor'
    MODERATE = 'moderate', 'Moderate'
    MAJOR = 'major', 'Major'


class DailyReportIncident(ChildRowModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='incidents')
    incident_type = models.CharField(max_length=40, choices=IncidentType.choices)
    description = models.TextField()
    corrective_action = models.TextField(blank=True, default='')
    follow_up_owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_incident_followups',
    )
    follow_up_owner_name = models.CharField(max_length=120, blank=True, default='')
    due_date = models.DateField(null=True, blank=True)
    # Feature 033 (data-model §3.7): HSE incident rows carry a nullable severity
    # and the notification reference generated at submit; structured provenance
    # for the source row lives in DailyReportDerivedSource.
    severity = models.CharField(max_length=10, choices=HseSeverity.choices, null=True, blank=True)
    notification_id = models.CharField(max_length=64, blank=True, default='')
    row_number = models.PositiveIntegerField(default=1)
    source_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_incidents',
    )
    source_row_id = models.CharField(max_length=64, blank=True, default='')

    class Meta:
        db_table = 'daily_report_incidents'
        ordering = ['row_number']


class DailyReportMachineryRow(ChildRowModel):
    """Derived machinery daily-status row (feature 033, data-model §3.3).

    Rows with ``equipment_ref`` are item rows (identity-deduped across
    contributing units); rows without are type rows. Written only by the
    aggregation service.
    """

    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='machinery_rows')
    equipment_type = models.CharField(max_length=120)
    equipment_ref = models.ForeignKey(
        'field_reports.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_machinery_rows',
    )
    status_total = models.PositiveIntegerField(default=0)
    status_active = models.PositiveIntegerField(default=0)
    status_ready = models.PositiveIntegerField(default=0)
    status_inactive = models.PositiveIntegerField(default=0)
    status_under_repair = models.PositiveIntegerField(default=0)
    operating_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stoppage_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    repair_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stoppage_reason_code = models.CharField(max_length=60, blank=True, default='')
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_machinery',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=True)

    class Meta:
        db_table = 'daily_report_machinery_rows'
        indexes = [
            models.Index(fields=['report', 'equipment_type'], name='drmr_report_type_idx'),
        ]


class DailyReportGeneralActivity(ChildRowModel):
    """Structured derived general-activity row (feature 033, data-model §3.6).

    Replaces preformatted text-encoding of general activities in the summary.
    """

    report = models.ForeignKey(
        DailyReport, on_delete=models.CASCADE, related_name='general_activities',
    )
    row_number = models.PositiveIntegerField()
    activity_description = models.TextField()
    location = models.CharField(max_length=120, blank=True, default='')
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_general_activities',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=True)

    class Meta:
        db_table = 'daily_report_general_activities'
        ordering = ['row_number']


class DailyReportVisit(ChildRowModel):
    """Structured derived visit row (feature 033, data-model §3.7)."""

    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='visits')
    row_number = models.PositiveIntegerField()
    text = models.TextField()
    source_sub_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_daily_visits',
    )
    source_discipline = models.CharField(max_length=20, blank=True, default='')
    is_derived = models.BooleanField(default=True)

    class Meta:
        db_table = 'daily_report_visits'
        ordering = ['row_number']


class DailyReportCorrectionRequest(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='daily_report_correction_requests',
    )
    source_report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='correction_requests_as_source',
    )
    result_report = models.ForeignKey(
        DailyReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='correction_requests_as_result',
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=CorrectionRequestStatus.choices,
        default=CorrectionRequestStatus.SUBMITTED,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_corrections_requested',
    )
    requested_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_report_corrections_decided',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'daily_report_correction_requests'
        ordering = ['-requested_at', '-created_at']


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
    temp_max = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(-40), MaxValueValidator(60)],
    )
    temp_min = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(-40), MaxValueValidator(60)],
    )
    weather_condition = models.CharField(max_length=20, choices=WeatherCondition.choices)
    site_status = models.CharField(max_length=10, choices=SiteStatus.choices, default=SiteStatus.ACTIVE)
    wind_speed = models.CharField(max_length=50, blank=True, default='')
    soil_condition = models.CharField(max_length=100, blank=True, default='')

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

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        errors = {}
        if self.temp_min is not None and (self.temp_min < -40 or self.temp_min > 60):
            errors['temp_min'] = 'دمای کمینه باید بین ۴۰- تا ۶۰+ درجه سانتی‌گراد باشد.'
        if self.temp_max is not None and (self.temp_max < -40 or self.temp_max > 60):
            errors['temp_max'] = 'دمای بیشینه باید بین ۴۰- تا ۶۰+ درجه سانتی‌گراد باشد.'
        if self.temp_min is not None and self.temp_max is not None and self.temp_max < self.temp_min:
            errors['temp_max'] = 'دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.log_date:
            self.day_of_week = persian_day_of_week(self.log_date)
        super().save(*args, **kwargs)


class LaborCampReport(AuditSoftDeleteModel, BaseLaborCampEntry):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='labor_camp_reports')
    report_date = models.DateField()

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


class EquipmentLog(AuditSoftDeleteModel, BaseEquipmentEntry):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='equipment_logs')
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    log_date = models.DateField()
    activity_ref = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_logs',
    )

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


class DailyReportDerivedSource(UUIDModel):
    """Normalized many-source provenance for every derived row or combined
    value in a project daily summary (feature 032, data-model §8).

    A single-source row has exactly one source; a combined value has all
    contributing sources in deterministic order. No last-source-wins rule.
    """

    daily_report = models.ForeignKey(
        'field_reports.DailyReport', on_delete=models.CASCADE, related_name='derived_sources',
    )
    derived_kind = models.CharField(max_length=40)
    derived_row_id = models.CharField(max_length=64)
    # Nullable FK for navigation/integrity; snapshots below survive even if a
    # future retention action nulls the FK.
    source_report = models.ForeignKey(
        'sub_reports.DisciplineSubReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_sources',
    )
    source_report_id_snapshot = models.UUIDField()
    source_report_version = models.PositiveIntegerField(default=1)
    source_unit = models.CharField(max_length=20)
    source_row_kind = models.CharField(max_length=40)
    # String representation supporting both UUID and existing integer source IDs.
    source_row_id = models.CharField(max_length=64)
    contribution_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    ordinal = models.PositiveIntegerField(default=0)

    class Meta(UUIDModel.Meta):
        db_table = 'daily_report_derived_sources'
        ordering = ['derived_kind', 'ordinal', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'derived_kind', 'derived_row_id', 'source_report_id_snapshot',
                    'source_row_kind', 'source_row_id',
                ],
                name='unique_derived_source_key',
            ),
        ]
        indexes = [
            models.Index(fields=['daily_report', 'derived_kind'], name='drds_report_kind_idx'),
        ]

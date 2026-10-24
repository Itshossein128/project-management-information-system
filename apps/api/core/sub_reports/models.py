from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel
from common.reporting_units import SpecialtyUnit
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


class IssueKind(models.TextChoices):
    """Feature 033 (data-model §2.6): structured narrative rows."""

    ISSUE = 'issue', 'Issue'
    BARRIER = 'barrier', 'Barrier'


class HseIncidentSeverity(models.TextChoices):
    MINOR = 'minor', 'Minor'
    MODERATE = 'moderate', 'Moderate'
    MAJOR = 'major', 'Major'


class SamplingState(models.TextChoices):
    NOT_SAMPLED = 'not_sampled', 'Not sampled'
    SAMPLING_DECLARED = 'sampling_declared', 'Sampling declared'


class MaterialTransactionKind(models.TextChoices):
    """Warehouse transaction kind on unit-report material rows (data-model §2.4)."""

    RECEIPT = 'receipt', 'Receipt'
    CONSUMPTION = 'consumption', 'Consumption'


DEFAULT_EXPECTED_DISCIPLINES = (
    Discipline.CIVIL,
    Discipline.ELECTRICAL,
    Discipline.MECHANICAL,
)


class UnitReportEventType(models.TextChoices):
    CREATED = 'created', 'Created'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CORRECTED = 'corrected', 'Corrected'
    DELETED = 'deleted', 'Deleted'
    SUPERSEDED = 'superseded', 'Superseded'


class MigrationDisposition(models.TextChoices):
    MIGRATED = 'migrated', 'Migrated'
    HISTORICAL = 'historical', 'Historical'
    DUPLICATE_ALIAS = 'duplicate_alias', 'Duplicate alias'
    QUARANTINED = 'quarantined', 'Quarantined'


class DisciplineSubReport(AuditSoftDeleteModel):
    """
    Represents a discipline-specific sub-report within a project, which can optionally
    be linked to a daily report. It tracks the status of the report (draft, submitted,
    approved, rejected) along with relevant environmental and auditing details.
    """
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='discipline_sub_reports')
    report_date = models.DateField()
    discipline = models.CharField(max_length=20, choices=Discipline.choices, default=Discipline.CIVIL)
    # Canonical unit identity (feature 032 expand phase). Nullable only during
    # migration/quarantine; product-visible rows require a valid canonical unit.
    unit = models.CharField(max_length=20, choices=SpecialtyUnit.choices, null=True, blank=True, db_index=True)
    # Preserved original discipline evidence for migration trace/rollback.
    legacy_discipline = models.CharField(max_length=20, blank=True, default='')
    # Version lineage: all versions of one project/date/unit report share a
    # lineage_id; version_number is monotonic within the lineage.
    lineage_id = models.UUIDField(null=True, blank=True, db_index=True)
    version_number = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)
    supersedes = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='superseded_by_unit_reports',
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_unit_reports',
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
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
                condition=models.Q(is_deleted=False, unit__isnull=True),
                name='unique_active_sub_report_per_discipline_date',
            ),
            # Canonical one-current-version rule (data-model §4). Only rows with
            # a canonical unit participate; legacy rows (unit NULL) are covered
            # by the legacy constraint above until migration completes.
            models.UniqueConstraint(
                fields=['project', 'report_date', 'unit'],
                condition=models.Q(is_current=True, is_deleted=False, unit__isnull=False),
                name='unique_current_unit_report_per_key',
            ),
            models.UniqueConstraint(
                fields=['lineage_id', 'version_number'],
                name='unique_unit_report_lineage_version',
            ),
            # Product-visible rows require a valid canonical unit (data-model §4, T069)
            models.CheckConstraint(
                check=models.Q(is_current=False) | models.Q(is_deleted=True) | models.Q(
                    unit__isnull=False,
                    unit__in=[
                        SpecialtyUnit.BUILDINGS,
                        SpecialtyUnit.ELECTRICAL,
                        SpecialtyUnit.MECHANICAL,
                        SpecialtyUnit.MACHINERY,
                        SpecialtyUnit.WAREHOUSE,
                        SpecialtyUnit.SECURITY,
                    ],
                ),
                name='check_product_visible_requires_canonical_unit',
            ),
            # Supersedes link requires version_number > 1
            models.CheckConstraint(
                check=models.Q(supersedes__isnull=True) | models.Q(version_number__gt=1),
                name='check_supersedes_requires_version_gt_1',
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
    parcel = models.CharField(max_length=60, null=True, blank=True)
    block = models.CharField(max_length=60, null=True, blank=True)
    floor = models.CharField(max_length=60, null=True, blank=True)
    activity_description = models.TextField()
    notes = models.TextField(blank=True, default='')
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
    # Feature 033 (data-model §2.1): contractor is a required project-scoped
    # stakeholder reference with contractor role; crew name stays a separate,
    # never-substituted column.
    contractor_ref = models.ForeignKey(
        'projects.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unit_report_activities_as_contractor',
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Feature 033 (§1, T014): derived total maintained on every save as
    # foreman_count + worker_count; the components stay authoritative columns.
    headcount = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_activities'
        ordering = ['row_number']

    def save(self, *args, **kwargs):
        # headcount is always the sum of its components when any is provided.
        if self.foreman_count is not None or self.worker_count is not None:
            self.headcount = (self.foreman_count or 0) + (self.worker_count or 0)
        super().save(*args, **kwargs)


class DisciplineSubReportLabor(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='labor_entries',
    )
    labor_category = models.CharField(max_length=10, choices=LaborCategory.choices)
    job_title = models.CharField(max_length=120)
    present_count = models.PositiveIntegerField(default=0)
    leave_count = models.PositiveIntegerField(default=0)
    # Feature 033 (data-model §2.2): man-hours are computed at aggregation time
    # from the configuration rule; only the overtime component is stored here.
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    contractor_ref = models.ForeignKey(
        'projects.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unit_report_labor_rows',
    )
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
    # Feature 033 (data-model §2.4): transaction typing, project-scoped material
    # reference, consumption location and the verbatim warehouse document
    # reference. Nullability stays backfill-compatible; serializer validation
    # enforces the receipt/consumption contract at save and submit.
    transaction_type = models.CharField(
        max_length=12, choices=MaterialTransactionKind.choices, null=True, blank=True,
    )
    material_ref = models.ForeignKey(
        'resources.Material',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unit_report_material_rows',
    )
    consumption_location = models.CharField(max_length=120, blank=True, default='')
    supplier = models.CharField(max_length=120, blank=True, default='')
    warehouse_document_reference = models.CharField(max_length=120, blank=True, default='')
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
    # Feature 033 (data-model §2.5): full pour record columns + QC traceability.
    structural_element = models.CharField(max_length=120, blank=True, default='')
    parcel = models.CharField(max_length=60, blank=True, default='')
    batching_plant = models.CharField(max_length=120, blank=True, default='')
    truck_delivery_note_number = models.CharField(max_length=60, blank=True, default='')
    lab_sample_code = models.CharField(max_length=60, blank=True, default='')
    sampling_state = models.CharField(
        max_length=20, choices=SamplingState.choices, default=SamplingState.NOT_SAMPLED,
    )
    test_sheet_count = models.PositiveIntegerField(null=True, blank=True)
    qc_inspection = models.ForeignKey(
        'risk.Inspection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='concrete_pours',
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_concrete'


class DisciplineSubReportGeneralActivity(UUIDModel):
    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='general_activities',
    )
    row_number = models.PositiveIntegerField(default=1)
    activity_description = models.TextField()
    location = models.CharField(max_length=120, blank=True, default='')
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_general_activities'


class DisciplineSubReportMachinery(UUIDModel):
    """Machinery status-grid row (feature 033, data-model §2.3).

    Rows that declare a stable ``equipment_ref`` identity are item rows
    (enable item-level dedupe); rows without are type rows. `status_total` is
    the declared type total; the other four counts are the five-status parts.
    """

    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='machinery_rows',
    )
    row_number = models.PositiveIntegerField()
    equipment_type = models.CharField(max_length=120)
    equipment_ref = models.ForeignKey(
        'field_reports.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unit_report_machinery_rows',
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
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_machinery'
        ordering = ['row_number']


class DisciplineSubReportIssue(UUIDModel):
    """Structured issue/barrier row (feature 033, data-model §2.6).

    Barriers require an owner and a due date; issues keep them optional with a
    recommendation. Validation lives in the section serializer (T046).
    """

    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='issues',
    )
    row_number = models.PositiveIntegerField()
    kind = models.CharField(max_length=10, choices=IssueKind.choices, default=IssueKind.ISSUE)
    text = models.TextField()
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_unit_report_issues',
    )
    due_date = models.DateField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_issues'
        ordering = ['row_number']


class DisciplineSubReportVisit(UUIDModel):
    """Structured visit row (feature 033, data-model §2.6)."""

    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='visits',
    )
    row_number = models.PositiveIntegerField()
    text = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_visits'
        ordering = ['row_number']


class DisciplineSubReportHseIncident(UUIDModel):
    """Structured HSE incident row (feature 033, data-model §2.6).

    ``immediate_action`` is required at creation (serializer validation); a
    submitted version containing an incident triggers the required
    notification through the HSE notification handler (T046).
    """

    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='hse_incidents',
    )
    row_number = models.PositiveIntegerField()
    text = models.TextField()
    severity = models.CharField(max_length=10, choices=HseIncidentSeverity.choices)
    immediate_action = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'discipline_sub_report_hse_incidents'
        ordering = ['row_number']


class UnitReportAttachment(UUIDModel):
    """Activity-image attachment on a unit-report version (data-model §2.7).

    Files are content-validated at upload (JPEG/PNG signature, ≤ 10 MB); the
    storage holder is environment-dependent (MinIO when available). Metadata is
    inherited from the parent version (source unit + project).
    """

    sub_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='attachments',
    )
    row_kind = models.CharField(max_length=40, blank=True, default='')
    row_id = models.CharField(max_length=64, blank=True, default='')
    storage_key = models.CharField(max_length=255, blank=True, default='')
    declared_content_type = models.CharField(max_length=60, blank=True, default='')
    size_bytes = models.PositiveIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, blank=True, default='')
    capture_date = models.DateField(null=True, blank=True)
    work_front = models.CharField(max_length=120, blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'unit_report_attachments'
        ordering = ['id']


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


class UnitReportStatusEvent(UUIDModel):
    """Append-only domain transition history for unit-report versions.

    Events cannot be updated or deleted through product APIs. Pre-feature
    history is not fabricated; migration creates a baseline event describing
    only the evidence present at migration time (data-model §5).
    """
    report_version = models.ForeignKey(
        DisciplineSubReport, on_delete=models.CASCADE, related_name='status_events',
    )
    from_status = models.CharField(max_length=20, choices=SubReportStatus.choices, blank=True, default='')
    to_status = models.CharField(max_length=20, choices=SubReportStatus.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unit_report_status_events',
    )
    occurred_at = models.DateTimeField()
    reason = models.TextField(blank=True, default='')
    event_type = models.CharField(max_length=20, choices=UnitReportEventType.choices)

    class Meta(UUIDModel.Meta):
        db_table = 'unit_report_status_events'
        ordering = ['occurred_at', 'id']
        indexes = [
            models.Index(fields=['report_version', 'occurred_at'], name='urse_version_occurred_idx'),
        ]


class UnitReportMigrationTrace(UUIDModel):
    """Permanent accounting and rollback ledger for the 032 migration.

    Unique (source_system, source_model, source_id) makes the backfill
    resumable/idempotent (data-model §9).
    """
    source_system = models.CharField(max_length=60)
    source_model = models.CharField(max_length=120)
    source_id = models.CharField(max_length=64)
    original_category = models.CharField(max_length=64, blank=True, default='')
    original_deleted = models.BooleanField(default=False)
    original_link_id = models.CharField(max_length=64, blank=True, default='')
    canonical_unit = models.CharField(max_length=20, choices=SpecialtyUnit.choices, null=True, blank=True)
    target_report = models.ForeignKey(
        DisciplineSubReport, on_delete=models.SET_NULL, null=True, blank=True, related_name='migration_traces',
    )
    lineage_id = models.UUIDField(null=True, blank=True)
    version_number = models.PositiveIntegerField(null=True, blank=True)
    selected_current = models.BooleanField(default=False)
    disposition = models.CharField(max_length=20, choices=MigrationDisposition.choices)
    resolution_reason = models.TextField(blank=True, default='')
    source_checksum = models.CharField(max_length=64, blank=True, default='')
    snapshot = models.JSONField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta(UUIDModel.Meta):
        db_table = 'unit_report_migration_traces'
        constraints = [
            models.UniqueConstraint(
                fields=['source_system', 'source_model', 'source_id'],
                name='unique_migration_trace_source',
            ),
        ]
        indexes = [
            models.Index(fields=['canonical_unit', 'disposition'], name='urt_unit_disp_idx'),
        ]


class UnitReportMigrationQuarantine(UUIDModel):
    """A migration trace that cannot be mapped safely (data-model §10).

    Quarantined rows remain readable to authorized migration operators, are
    never current, and never contribute to a project daily summary.
    """
    trace = models.OneToOneField(
        UnitReportMigrationTrace, on_delete=models.CASCADE, related_name='quarantine',
    )
    reason_code = models.CharField(max_length=60)
    raw_category = models.CharField(max_length=64, blank=True, default='')
    raw_payload = models.JSONField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_unit_report_quarantines',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default='')

    class Meta(UUIDModel.Meta):
        db_table = 'unit_report_migration_quarantines'
        ordering = ['detected_at']

from django.conf import settings
from django.db import models
from treebeard.mp_tree import MP_Node

import uuid

from django.utils import timezone

from common.models import AuditSoftDeleteModel, TimeStampedModel, UUIDModel


class ProjectStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING_APPROVAL = 'pending_approval', 'Pending approval'
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'
    ARCHIVED = 'archived', 'Archived'
    # Legacy synonym retained for migration/read compatibility only.
    HANDED_OVER = 'handed_over', 'Handed over'


class ProjectCurrency(models.TextChoices):
    IRR = 'IRR', 'Rial'
    IRT = 'IRT', 'Toman'


class CapabilityMode(models.TextChoices):
    REQUIRED = 'required', 'Required'
    OPTIONAL = 'optional', 'Optional'
    DISABLED = 'disabled', 'Disabled'


# Seed catalog for per-project capability toggles (FR-CORE-012).
CAPABILITY_CATALOG = (
    'risk',
    'economic',
    'procurement',
    'cash_flow',
    'documents',
    'alerts',
    'subcontractors',
    'hr',
)


class Project(UUIDModel, TimeStampedModel):
    project_code = models.CharField(max_length=30, unique=True)
    project_name = models.CharField(max_length=200)
    purpose = models.TextField(blank=True, default='')
    scope_description = models.TextField(blank=True, default='')
    main_deliverables = models.TextField(blank=True, default='')
    employer = models.CharField(max_length=120, blank=True, default='')
    contractor = models.CharField(max_length=120, blank=True, default='')
    consultant = models.CharField(max_length=120, blank=True, default='')
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
    )
    location = models.TextField(blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    planned_finish_date = models.DateField(null=True, blank=True)
    contract_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    contract_type = models.CharField(max_length=60, blank=True, default='')
    contract_number = models.CharField(max_length=60, blank=True, default='')
    currency = models.CharField(
        max_length=3,
        choices=ProjectCurrency.choices,
        default=ProjectCurrency.IRR,
    )
    status = models.CharField(
        max_length=30,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
    )
    budget_approved_at = models.DateTimeField(null=True, blank=True)
    budget_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_approved_projects',
    )
    cut_off_date = models.DateField(null=True, blank=True)
    max_depth = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        help_text='Maximum WBS depth for this project. Null means unlimited.',
    )
    owning_unit = models.ForeignKey(
        'master_data.OrganizationUnit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_projects',
    )

    class Meta:
        db_table = 'projects'
        ordering = ['project_name']
        indexes = [
            models.Index(fields=['status'], name='projects_status_idx'),
        ]

    def __str__(self):
        return self.project_name

    @property
    def name(self):
        return self.project_name

    @property
    def slug(self):
        return self.project_code


class ProjectChangeRequestStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'


PROTECTED_PROJECT_FIELDS = frozenset({
    'start_date',
    'planned_finish_date',
    'contract_amount',
    'employer',
    'scope_description',
})


class ProjectKickoffCharter(AuditSoftDeleteModel):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='kickoff_charter',
    )
    justification = models.TextField(blank=True, default='')
    success_criteria = models.TextField(blank=True, default='')
    constraints = models.TextField(blank=True, default='')
    assumptions = models.TextField(blank=True, default='')
    key_stakeholders_summary = models.TextField(blank=True, default='')
    pm_authority = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'project_kickoff_charters'


class ProjectChangeRequest(AuditSoftDeleteModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='change_requests',
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ProjectChangeRequestStatus.choices,
        default=ProjectChangeRequestStatus.DRAFT,
    )
    proposed_changes = models.JSONField(default=dict, blank=True)
    previous_values = models.JSONField(default=dict, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='project_change_requests_requested',
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_change_requests_decided',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'project_change_requests'
        ordering = ['-requested_at']


class WBSStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    ON_HOLD = 'on_hold', 'On hold'


class WBS(UUIDModel, TimeStampedModel, MP_Node):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='wbs_nodes')
    wbs_code = models.CharField(max_length=30)
    wbs_name = models.CharField(max_length=200)
    weight_physical = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    weight_financial = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    description = models.TextField(blank=True, default='')
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_wbs_nodes',
    )
    acceptance_criteria = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=WBSStatus.choices,
        default=WBSStatus.ACTIVE,
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    node_order_by = ['wbs_code']

    class Meta:
        db_table = 'wbs'
        unique_together = [['project', 'wbs_code']]
        verbose_name = 'WBS'
        verbose_name_plural = 'WBS'

    def __str__(self):
        return f'{self.wbs_code} — {self.wbs_name}'

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        # Free unique (project, wbs_code) while retaining the row.
        self.wbs_code = f'd_{self.pk.hex[:28]}'
        update_fields = ['is_deleted', 'deleted_at', 'wbs_code']
        if user is not None:
            self.updated_by = user
            update_fields.append('updated_by')
        self.save(update_fields=update_fields)


class ProjectCapabilitySetting(UUIDModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='capability_settings')
    capability_key = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)
    mode = models.CharField(
        max_length=20,
        choices=CapabilityMode.choices,
        default=CapabilityMode.OPTIONAL,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        db_table = 'project_capability_settings'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'capability_key'],
                name='uniq_project_capability_key',
            ),
        ]

    @property
    def is_effectively_disabled(self) -> bool:
        return (not self.enabled) or self.mode == CapabilityMode.DISABLED


class FiscalPeriodLock(UUIDModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fiscal_period_locks')
    period_start = models.DateField()
    period_end = models.DateField()
    closed_at = models.DateTimeField()
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='fiscal_locks_closed',
    )
    reason = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fiscal_period_locks'
        ordering = ['-period_end', '-closed_at']

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.period_end < self.period_start:
            raise ValidationError({'period_end': 'period_end must be >= period_start'})
        if not self.reason or len(self.reason.strip()) < 3:
            raise ValidationError({'reason': 'reason must be at least 3 characters'})



class ActivityStatus(models.TextChoices):
    NOT_STARTED = 'not_started', 'Not started'
    IN_PROGRESS = 'in_progress', 'In progress'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'


class Activity(AuditSoftDeleteModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE, related_name='activities')
    activity_code = models.CharField(max_length=30)
    activity_name = models.CharField(max_length=200)
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
    )
    total_quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_finish = models.DateField(null=True, blank=True)
    duration_days = models.IntegerField(null=True, blank=True)
    is_milestone = models.BooleanField(default=False)
    forecast_start = models.DateField(null=True, blank=True)
    forecast_finish = models.DateField(null=True, blank=True)
    working_calendar = models.ForeignKey(
        'schedule.WorkingCalendar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_activities',
    )
    status = models.CharField(
        max_length=20,
        choices=ActivityStatus.choices,
        default=ActivityStatus.NOT_STARTED,
    )
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'activities'
        unique_together = [['project', 'activity_code']]

    def __str__(self):
        return f'{self.activity_code} — {self.activity_name}'

    @property
    def planned_duration(self):
        if self.planned_start and self.planned_finish:
            return (self.planned_finish - self.planned_start).days + 1
        return None

    @property
    def actual_duration(self):
        if self.actual_start and self.actual_finish:
            return (self.actual_finish - self.actual_start).days
        return None

    @property
    def is_overdue(self):
        today = timezone.localdate()
        return (
            self.planned_finish is not None
            and self.planned_finish < today
            and self.status != ActivityStatus.COMPLETED
        )


class RelationType(models.TextChoices):
    FS = 'FS', 'Finish-to-Start'
    SS = 'SS', 'Start-to-Start'
    FF = 'FF', 'Finish-to-Finish'
    SF = 'SF', 'Start-to-Finish'


class ActivityRelation(AuditSoftDeleteModel):
    predecessor = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='successor_relations',
    )
    successor = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='predecessor_relations',
    )
    relation_type = models.CharField(max_length=4, choices=RelationType.choices, default=RelationType.FS)
    lag_days = models.IntegerField(default=0)

    class Meta:
        db_table = 'activity_relations'
        constraints = [
            models.UniqueConstraint(
                fields=['predecessor', 'successor'],
                condition=models.Q(is_deleted=False),
                name='unique_active_activity_relation',
            ),
        ]

    def __str__(self):
        return f'{self.predecessor_id} -> {self.successor_id} ({self.relation_type})'


class StakeholderStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class Stakeholder(AuditSoftDeleteModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stakeholders')
    name = models.CharField(max_length=200)
    organization_name = models.CharField(max_length=200, blank=True, default='')
    role = models.CharField(max_length=120, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=40, blank=True, default='')
    influence = models.PositiveSmallIntegerField(null=True, blank=True)
    interest = models.PositiveSmallIntegerField(null=True, blank=True)
    communication_need = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=StakeholderStatus.choices,
        default=StakeholderStatus.ACTIVE,
    )

    class Meta:
        db_table = 'stakeholders'
        ordering = ['name']

    def clean(self):
        from django.core.exceptions import ValidationError

        for field in ('influence', 'interest'):
            value = getattr(self, field)
            if value is not None and not (1 <= int(value) <= 5):
                raise ValidationError({field: 'Must be between 1 and 5'})

    def __str__(self):
        return self.name

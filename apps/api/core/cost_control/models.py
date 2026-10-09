from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from treebeard.mp_tree import MP_Node

from common.models import AuditSoftDeleteModel, TimeStampedModel, UUIDModel


class CostCategory(models.TextChoices):
    LABOR = 'labor', 'Labor'
    MATERIAL = 'material', 'Material'
    EQUIPMENT = 'equipment', 'Equipment'
    SUBCONTRACT = 'subcontract', 'Subcontract'
    SITE_OVERHEAD = 'site_overhead', 'Site overhead'
    HQ_OVERHEAD = 'hq_overhead', 'HQ overhead'
    TRANSPORT = 'transport', 'Transport'
    OTHER = 'other', 'Other'


class PoolStatus(models.TextChoices):
    UNALLOCATED = 'unallocated', 'Unallocated'
    PARTIALLY_ALLOCATED = 'partially_allocated', 'Partially allocated'
    FULLY_ALLOCATED = 'fully_allocated', 'Fully allocated'


class CostType(models.TextChoices):
    DIRECT = 'direct', 'Direct'
    ALLOCATED_HISTORICAL = 'allocated_historical', 'Allocated historical'
    ESTIMATED_HISTORICAL = 'estimated_historical', 'Estimated historical'
    UNALLOCATED = 'unallocated', 'Unallocated'


class ConfidenceLevel(models.TextChoices):
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'


class CostPool(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='cost_pools')
    pool_name = models.CharField(max_length=120, blank=True, default='')
    cost_category = models.CharField(max_length=40, choices=CostCategory.choices, blank=True, default='')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    allocated_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=PoolStatus.choices, default=PoolStatus.UNALLOCATED)
    data_source = models.CharField(max_length=60, blank=True, default='')
    confidence_level = models.CharField(max_length=10, choices=ConfidenceLevel.choices, blank=True, default='')

    class Meta:
        db_table = 'cost_pools'

    @property
    def remaining(self):
        total = self.total_amount or 0
        return total - (self.allocated_amount or 0)

    def _update_status(self):
        total = self.total_amount or 0
        remaining = float(total) - float(self.allocated_amount or 0)
        if remaining <= 0 and total:
            self.status = PoolStatus.FULLY_ALLOCATED
        elif remaining >= float(total):
            self.status = PoolStatus.UNALLOCATED
        else:
            self.status = PoolStatus.PARTIALLY_ALLOCATED

    def save(self, *args, **kwargs):
        self._update_status()
        super().save(*args, **kwargs)


class CostBreakdownNode(UUIDModel, TimeStampedModel, MP_Node):
    """CBS hierarchy — distinct from WBS."""

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='cbs_nodes',
    )
    cbs_code = models.CharField(max_length=30)
    cbs_name = models.CharField(max_length=200)
    cost_type = models.CharField(max_length=40, choices=CostCategory.choices, blank=True, default='')
    description = models.TextField(blank=True, default='')
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

    node_order_by = ['cbs_code']

    class Meta:
        db_table = 'cbs_nodes'
        unique_together = [['project', 'cbs_code']]

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.cbs_code = f'd_{self.pk.hex[:28]}'
        update_fields = ['is_deleted', 'deleted_at', 'cbs_code']
        if user is not None:
            self.updated_by = user
            update_fields.append('updated_by')
        self.save(update_fields=update_fields)

    def __str__(self):
        return f'{self.cbs_code} — {self.cbs_name}'


class CommitmentStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    APPROVED = 'approved', 'Approved'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'


class Commitment(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='commitments')
    commitment_number = models.CharField(max_length=60)
    counterparty = models.CharField(max_length=200, blank=True, default='')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='IRR')
    fx_rate = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    commitment_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commitments',
    )
    cbs = models.ForeignKey(
        CostBreakdownNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commitments',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cost_commitments',
    )
    requisition = models.ForeignKey(
        'procurement.RequisitionHeader',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commitments',
    )
    status = models.CharField(
        max_length=20,
        choices=CommitmentStatus.choices,
        default=CommitmentStatus.DRAFT,
    )
    payment_terms = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    document_ref = models.CharField(max_length=80, blank=True, default='')

    class Meta:
        db_table = 'commitments'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'commitment_number'],
                condition=models.Q(is_deleted=False),
                name='uniq_active_commitment_number',
            ),
        ]


class PaymentStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    POSTED = 'posted', 'Posted'
    VOID = 'void', 'Void'


class Payment(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='payments')
    commitment = models.ForeignKey(
        Commitment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    actual_cost = models.ForeignKey(
        'cost_control.ActualCost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='IRR')
    fx_rate = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    paid_at = models.DateField()
    document_ref = models.CharField(max_length=80, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.POSTED,
    )
    duplicate_exception_reason = models.TextField(blank=True, default='')
    duplicate_exception_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_duplicate_exceptions',
    )

    class Meta:
        db_table = 'cost_payments'
        ordering = ['-paid_at']


class BudgetVersionKind(models.TextChoices):
    INITIAL = 'initial', 'Initial'
    APPROVED = 'approved', 'Approved'
    REVISED = 'revised', 'Revised'
    FINAL_FORECAST = 'final_forecast', 'Final forecast'


class BudgetVersionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class BudgetLineLevel(models.TextChoices):
    PROJECT = 'project', 'Project'
    PHASE = 'phase', 'Phase'
    CONTRACT = 'contract', 'Contract'
    WBS = 'wbs', 'WBS package'
    CBS = 'cbs', 'CBS'
    ACTIVITY = 'activity', 'Activity'


class BudgetChangeRequestStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'


class BudgetVersion(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budget_versions',
    )
    kind = models.CharField(max_length=20, choices=BudgetVersionKind.choices)
    status = models.CharField(
        max_length=20,
        choices=BudgetVersionStatus.choices,
        default=BudgetVersionStatus.DRAFT,
    )
    version_number = models.PositiveIntegerField()
    name = models.CharField(max_length=200, blank=True, default='')
    currency = models.CharField(max_length=3, default='IRR')
    notes = models.TextField(blank=True, default='')
    is_control = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_versions_submitted',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_versions_approved',
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_versions_rejected',
    )
    rejection_reason = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'budget_versions'
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'version_number'],
                condition=models.Q(is_deleted=False),
                name='uniq_active_budget_version_number',
            ),
        ]

    def __str__(self):
        return f'v{self.version_number} {self.kind} ({self.status})'


class Budget(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='budgets')
    version = models.ForeignKey(
        BudgetVersion,
        on_delete=models.CASCADE,
        related_name='lines',
        null=True,
        blank=True,
    )
    level = models.CharField(
        max_length=20,
        choices=BudgetLineLevel.choices,
        default=BudgetLineLevel.WBS,
    )
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets',
    )
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets',
    )
    cbs = models.ForeignKey(
        CostBreakdownNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_lines',
    )
    cost_category = models.CharField(max_length=40, choices=CostCategory.choices)
    budget_amount = models.DecimalField(max_digits=18, decimal_places=2)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'budgets'
        indexes = [
            models.Index(fields=['project', 'cost_category'], name='budget_project_cat_idx'),
            models.Index(fields=['version', 'cost_category'], name='budget_version_cat_idx'),
        ]

    def clean(self):
        level = self.level or BudgetLineLevel.WBS
        if level == BudgetLineLevel.PROJECT:
            return
        if level == BudgetLineLevel.CONTRACT and not self.contract_id:
            raise ValidationError({'contract': 'contract is required for contract-level budget lines.'})
        if level in (BudgetLineLevel.PHASE, BudgetLineLevel.WBS) and not self.wbs_id:
            raise ValidationError({'wbs': 'wbs is required for this budget level.'})
        if level == BudgetLineLevel.CBS and not self.cbs_id:
            raise ValidationError({'cbs': 'cbs is required for cbs-level budget lines.'})
        if level == BudgetLineLevel.ACTIVITY and not self.activity_id:
            raise ValidationError({'activity': 'activity is required for activity-level budget lines.'})
        if level == BudgetLineLevel.WBS and not self.wbs_id and not self.activity_id:
            raise ValidationError('At least one of wbs or activity must be set.')
        if self.activity_id and not self.wbs_id:
            self.wbs_id = self.activity.wbs_id

    def save(self, *args, **kwargs):
        if self.activity_id and not self.wbs_id:
            self.wbs_id = self.activity.wbs_id
        if not self.level:
            if self.activity_id:
                self.level = BudgetLineLevel.ACTIVITY
            elif self.cbs_id and not self.wbs_id:
                self.level = BudgetLineLevel.CBS
            elif self.contract_id and not self.wbs_id:
                self.level = BudgetLineLevel.CONTRACT
            else:
                self.level = BudgetLineLevel.WBS
        super().save(*args, **kwargs)


class BudgetChangeRequest(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budget_change_requests',
    )
    base_version = models.ForeignKey(
        BudgetVersion,
        on_delete=models.PROTECT,
        related_name='change_requests_from',
    )
    resulting_version = models.ForeignKey(
        BudgetVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_requests_result',
    )
    reason = models.TextField()
    amount_delta = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    project_impact = models.TextField()
    affected_lines = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BudgetChangeRequestStatus.choices,
        default=BudgetChangeRequestStatus.DRAFT,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='budget_change_requests_requested',
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_change_requests_decided',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'budget_change_requests'
        ordering = ['-requested_at']


class BudgetTransfer(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='budget_transfers',
    )
    version = models.ForeignKey(
        BudgetVersion,
        on_delete=models.CASCADE,
        related_name='transfers',
    )
    from_line = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        related_name='transfers_from',
    )
    to_line = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        related_name='transfers_to',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    note = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'budget_transfers'
        ordering = ['-created_at']


class ActualCostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    APPROVED = 'approved', 'Approved'
    VOID = 'void', 'Void'


class ActualCost(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='actual_costs')
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    wbs = models.ForeignKey(
        'projects.WBS',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    cbs = models.ForeignKey(
        CostBreakdownNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    commitment = models.ForeignKey(
        Commitment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    cost_date = models.DateField()  # occurrence date
    registered_at = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ActualCostStatus.choices,
        default=ActualCostStatus.DRAFT,
    )
    cost_category = models.CharField(max_length=40, choices=CostCategory.choices, blank=True, default='')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(blank=True, default='')
    invoice_number = models.CharField(max_length=60, blank=True, default='')
    document_ref = models.CharField(max_length=80, blank=True, default='')
    supplier = models.ForeignKey(
        'resources.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_costs',
    )
    cost_type = models.CharField(max_length=20, choices=CostType.choices, default=CostType.DIRECT)
    confidence_level = models.CharField(max_length=10, choices=ConfidenceLevel.choices, blank=True, default='')
    allocation_method = models.TextField(blank=True, default='')
    cost_pool = models.ForeignKey(
        CostPool,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )
    daily_report = models.ForeignKey(
        'field_reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_costs',
    )

    class Meta:
        db_table = 'actual_costs'
        indexes = [
            models.Index(fields=['project', 'cost_date'], name='actualcost_project_date_idx'),
        ]

    def save(self, *args, **kwargs):
        if self.activity_id and not self.wbs_id:
            self.wbs_id = self.activity.wbs_id
        if self.registered_at is None:
            self.registered_at = timezone.localdate()
        super().save(*args, **kwargs)

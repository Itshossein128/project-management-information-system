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
    status = models.CharField(
        max_length=20,
        choices=CommitmentStatus.choices,
        default=CommitmentStatus.DRAFT,
    )
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

    class Meta:
        db_table = 'cost_payments'
        ordering = ['-paid_at']


class Budget(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='budgets')
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
    cost_category = models.CharField(max_length=40, choices=CostCategory.choices)
    budget_amount = models.DecimalField(max_digits=18, decimal_places=2)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'budgets'
        indexes = [
            models.Index(fields=['project', 'cost_category'], name='budget_project_cat_idx'),
        ]

    def clean(self):
        if not self.wbs_id and not self.activity_id:
            raise ValidationError('At least one of wbs or activity must be set.')
        if self.activity_id and not self.wbs_id:
            self.wbs_id = self.activity.wbs_id

    def save(self, *args, **kwargs):
        if self.activity_id and not self.wbs_id:
            self.wbs_id = self.activity.wbs_id
        super().save(*args, **kwargs)


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
    cost_date = models.DateField()
    cost_category = models.CharField(max_length=40, choices=CostCategory.choices, blank=True, default='')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(blank=True, default='')
    invoice_number = models.CharField(max_length=60, blank=True, default='')
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
        super().save(*args, **kwargs)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.models import AuditSoftDeleteModel


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

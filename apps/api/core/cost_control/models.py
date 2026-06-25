from django.conf import settings
from django.db import models

from common.models import UUIDModel


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


class CostPool(UUIDModel):
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


class Budget(UUIDModel):
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

    class Meta:
        db_table = 'budgets'


class ActualCost(UUIDModel):
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

    class Meta:
        db_table = 'actual_costs'

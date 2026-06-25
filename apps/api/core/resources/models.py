from django.db import models

from common.models import UUIDModel


class Supplier(UUIDModel):
    supplier_name = models.CharField(max_length=120)
    contact_info = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return self.supplier_name


class Material(UUIDModel):
    material_code = models.CharField(max_length=30, unique=True)
    material_name = models.CharField(max_length=120)
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
    )
    category = models.CharField(max_length=60, blank=True, default='')
    min_stock_level = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'materials'

    def __str__(self):
        return self.material_name


class TransactionType(models.TextChoices):
    IN = 'in', 'In'
    OUT = 'out', 'Out'
    WASTE = 'waste', 'Waste'
    ADJUST = 'adjust', 'Adjust'


class InventoryTransaction(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='inventory_transactions')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    tx_date = models.DateField()
    tx_type = models.CharField(max_length=10, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
    )
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions',
    )
    document_ref = models.CharField(max_length=60, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'inventory_transactions'

from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel


class Supplier(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='suppliers',
    )
    supplier_name = models.CharField(max_length=120)
    supplier_code = models.CharField(max_length=30, blank=True, default='')
    contact_person = models.CharField(max_length=80, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.CharField(max_length=120, blank=True, default='')
    address = models.TextField(blank=True, default='')
    contact_info = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return self.supplier_name


class Material(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='materials',
    )
    material_code = models.CharField(max_length=30)
    material_name = models.CharField(max_length=200)
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
    )
    category = models.CharField(max_length=60, blank=True, default='')
    discipline = models.CharField(max_length=20, blank=True, default='general')
    location = models.CharField(max_length=120, blank=True, default='')
    block_type = models.CharField(max_length=80, blank=True, default='')
    estimated_total_qty = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    qty_per_block = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    min_stock_level = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'materials'
        constraints = [
            models.UniqueConstraint(fields=['project', 'material_code'], name='uniq_material_project_code'),
        ]

    def __str__(self):
        return self.material_name


class TransactionType(models.TextChoices):
    IN = 'in', 'In'
    OUT = 'out', 'Out'
    WASTE = 'waste', 'Waste'
    ADJUST = 'adjust', 'Adjust'


class InventoryTransaction(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='inventory_transactions')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='transactions')
    tx_date = models.DateField()
    tx_type = models.CharField(max_length=10, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    block_ref = models.CharField(max_length=60, blank=True, default='')
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
    daily_report = models.ForeignKey(
        'field_reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions',
    )
    document_ref = models.CharField(max_length=60, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'inventory_transactions'
        indexes = [
            models.Index(fields=['material', 'tx_date'], name='invtx_material_date_idx'),
        ]


class MaterialRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    ORDERED = 'ordered', 'Ordered'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class MaterialRequest(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='material_requests')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='requests')
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='material_requests',
    )
    request_number = models.PositiveIntegerField()
    requested_qty = models.DecimalField(max_digits=18, decimal_places=4)
    unit = models.CharField(max_length=40)
    request_date = models.DateField(null=True, blank=True)
    required_by_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=MaterialRequestStatus.choices,
        default=MaterialRequestStatus.PENDING,
    )
    approved_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_material_requests',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'material_requests'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'material', 'request_number'],
                name='uniq_material_request_number',
            ),
        ]


class PurchaseOrder(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='purchase_orders')
    material_request = models.OneToOneField(
        MaterialRequest,
        on_delete=models.CASCADE,
        related_name='purchase_order',
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    po_number = models.PositiveIntegerField()
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    ordered_qty = models.DecimalField(max_digits=18, decimal_places=4)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'purchase_orders'
        constraints = [
            models.UniqueConstraint(fields=['project', 'po_number'], name='uniq_po_project_number'),
        ]

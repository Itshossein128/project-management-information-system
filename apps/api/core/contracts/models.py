from django.db import models

from common.models import AuditSoftDeleteModel


class ContractType(models.TextChoices):
    MAIN = 'main', 'Main'
    SUBCONTRACT = 'subcontract', 'Subcontract'
    PURCHASE = 'purchase', 'Purchase'
    EQUIPMENT_RENTAL = 'equipment_rental', 'Equipment rental'


class ContractStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'
    TERMINATED = 'terminated', 'Terminated'


class Contract(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=60, blank=True, default='')
    contract_type = models.CharField(max_length=40, choices=ContractType.choices, blank=True, default='')
    counterparty = models.CharField(max_length=120, blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    original_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    adjusted_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    advance_payment_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    retention_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    insurance_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    performance_guarantee_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    performance_guarantee_expiry = models.DateField(null=True, blank=True)
    advance_guarantee_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    advance_guarantee_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ContractStatus.choices, default=ContractStatus.DRAFT)
    file_url = models.CharField(max_length=500, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'contracts'

    @property
    def effective_amount(self):
        return self.adjusted_amount if self.adjusted_amount is not None else (self.original_amount or 0)

    @property
    def advance_amount(self):
        return float(self.effective_amount) * float(self.advance_payment_pct or 0) / 100


class ContractItem(AuditSoftDeleteModel):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='items')
    activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contract_items',
    )
    boq_code = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    unit = models.ForeignKey(
        'master_data.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contract_items',
    )
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'contract_items'

    @property
    def total_amount(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity


class ChangeOrderStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ChangeOrder(AuditSoftDeleteModel):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='change_orders')
    change_number = models.PositiveIntegerField()
    description = models.TextField(blank=True, default='')
    amount_change = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    approved_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ChangeOrderStatus.choices, default=ChangeOrderStatus.DRAFT)
    file_url = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'change_orders'
        unique_together = [['contract', 'change_number']]


class IPCStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under review'
    APPROVED = 'approved', 'Approved'
    PAID = 'paid', 'Paid'


class IPC(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='ipcs')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='ipcs')
    ipc_number = models.IntegerField()
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    prepared_date = models.DateField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    planned_payment_date = models.DateField(null=True, blank=True)
    actual_payment_date = models.DateField(null=True, blank=True)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=IPCStatus.choices, default=IPCStatus.DRAFT)
    rejection_reason = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'ipcs'
        unique_together = [['project', 'contract', 'ipc_number']]


class IPCItem(AuditSoftDeleteModel):
    ipc = models.ForeignKey(IPC, on_delete=models.CASCADE, related_name='items')
    contract_item = models.ForeignKey(
        ContractItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ipc_items',
    )
    description = models.TextField(blank=True, default='')
    unit = models.CharField(max_length=40, blank=True, default='')
    qty_previous = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    qty_current = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    qty_cumulative = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    amount_current = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    amount_cumulative = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = 'ipc_items'


class DeductionType(models.TextChoices):
    RETENTION = 'retention', 'Retention'
    TAX = 'tax', 'Tax'
    INSURANCE = 'insurance', 'Insurance'
    ADVANCE_RECOVERY = 'advance_recovery', 'Advance recovery'
    MATERIAL_PRICE_DIFF = 'material_price_diff', 'Material price diff'
    OTHER = 'other', 'Other'


class IPCDeduction(AuditSoftDeleteModel):
    ipc = models.ForeignKey(IPC, on_delete=models.CASCADE, related_name='deductions')
    deduction_type = models.CharField(max_length=40, choices=DeductionType.choices)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        db_table = 'ipc_deductions'

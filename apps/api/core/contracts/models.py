from django.db import models

from common.models import UUIDModel


class Contract(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=60, unique=True, null=True, blank=True)
    contract_type = models.CharField(max_length=40, blank=True, default='')
    counterparty = models.CharField(max_length=120, blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    original_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    adjusted_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    advance_payment_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    retention_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    insurance_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tax_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    file_url = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'contracts'


class ContractItem(UUIDModel):
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


class IPCStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under review'
    APPROVED = 'approved', 'Approved'
    PAID = 'paid', 'Paid'


class IPC(UUIDModel):
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
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=IPCStatus.choices, default=IPCStatus.DRAFT)

    class Meta:
        db_table = 'ipcs'
        unique_together = [['project', 'contract', 'ipc_number']]


class IPCItem(UUIDModel):
    ipc = models.ForeignKey(IPC, on_delete=models.CASCADE, related_name='items')
    contract_item = models.ForeignKey(
        ContractItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ipc_items',
    )
    qty_previous = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    qty_current = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    qty_cumulative = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    amount_current = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount_cumulative = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'ipc_items'


class DeductionType(models.TextChoices):
    RETENTION = 'retention', 'Retention'
    TAX = 'tax', 'Tax'
    INSURANCE = 'insurance', 'Insurance'
    ADVANCE_RECOVERY = 'advance_recovery', 'Advance recovery'
    MATERIAL_PRICE_DIFF = 'material_price_diff', 'Material price diff'
    OTHER = 'other', 'Other'


class IPCDeduction(UUIDModel):
    ipc = models.ForeignKey(IPC, on_delete=models.CASCADE, related_name='deductions')
    deduction_type = models.CharField(max_length=40, choices=DeductionType.choices)
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'ipc_deductions'

from django.core.exceptions import ValidationError
from django.db import models

from common.jalali import parse_jalali_or_gregorian
from common.models import AuditSoftDeleteModel


class CashTransactionType(models.TextChoices):
    IN = 'in', 'In'
    OUT = 'out', 'Out'


class InflowCategory(models.TextChoices):
    IPC_RECEIPT = 'ipc_receipt', 'IPC receipt'
    ADVANCE_RECEIPT = 'advance_receipt', 'Advance receipt'
    GUARANTEE_RECEIPT = 'guarantee_receipt', 'Guarantee receipt'
    OTHER_INCOME = 'other_income', 'Other income'


class OutflowCategory(models.TextChoices):
    SUBCONTRACTOR_PAYMENT = 'subcontractor_payment', 'Subcontractor payment'
    SUPPLIER_PAYMENT = 'supplier_payment', 'Supplier payment'
    SALARY = 'salary', 'Salary'
    EQUIPMENT_RENTAL = 'equipment_rental', 'Equipment rental'
    SITE_OVERHEAD = 'site_overhead', 'Site overhead'
    TAX_PAYMENT = 'tax_payment', 'Tax payment'
    ADVANCE_PAYMENT = 'advance_payment', 'Advance payment'
    GUARANTEE_PAYMENT = 'guarantee_payment', 'Guarantee payment'
    OTHER_EXPENSE = 'other_expense', 'Other expense'


INFLOW_CATEGORIES = frozenset(c.value for c in InflowCategory)
OUTFLOW_CATEGORIES = frozenset(c.value for c in OutflowCategory)


class CashTransaction(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='cash_transactions')
    tx_date = models.DateField()
    tx_type = models.CharField(max_length=10, choices=CashTransactionType.choices)
    category = models.CharField(max_length=60, blank=True, default='')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(blank=True, default='')
    ipc = models.ForeignKey(
        'contracts.IPC',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_transactions',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_transactions',
    )
    counterparty = models.CharField(max_length=120, blank=True, default='')
    is_forecast = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    document_ref = models.CharField(max_length=60, blank=True, default='')

    class Meta:
        db_table = 'cash_transactions'
        indexes = [
            models.Index(fields=['project', 'tx_date'], name='cashtx_project_date_idx'),
        ]

    def clean(self):
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})
        if self.tx_type == CashTransactionType.IN and self.category:
            if self.category not in INFLOW_CATEGORIES:
                raise ValidationError({'category': 'Invalid inflow category.'})
        if self.tx_type == CashTransactionType.OUT and self.category:
            if self.category not in OUTFLOW_CATEGORIES:
                raise ValidationError({'category': 'Invalid outflow category.'})


class CashFlowForecast(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='cash_flow_forecasts')
    month = models.DateField()
    expected_inflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    expected_outflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    confidence_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'cash_flow_forecasts'
        unique_together = [['project', 'month']]

    @property
    def net_monthly(self):
        return (self.expected_inflow or 0) - (self.expected_outflow or 0)

    def save(self, *args, **kwargs):
        if self.month:
            if isinstance(self.month, str):
                parsed = parse_jalali_or_gregorian(self.month)
                if parsed:
                    self.month = parsed
            try:
                self.month = self.month.replace(day=1)
            except TypeError:
                pass
        super().save(*args, **kwargs)

from django.db import models

from common.models import UUIDModel


class CashTransactionType(models.TextChoices):
    IN = 'in', 'In'
    OUT = 'out', 'Out'


class CashTransaction(UUIDModel):
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
    is_forecast = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cash_transactions'


class CashFlowForecast(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='cash_flow_forecasts')
    month = models.DateField()
    expected_inflow = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    expected_outflow = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    confidence_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'cash_flow_forecasts'
        unique_together = [['project', 'month']]

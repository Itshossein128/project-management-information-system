from django.db import models

from common.models import UUIDModel


class InflationIndex(UUIDModel):
    index_name = models.CharField(max_length=80)
    index_date = models.DateField()
    index_value = models.DecimalField(max_digits=12, decimal_places=4)
    source = models.CharField(max_length=120, blank=True, default='')

    class Meta:
        db_table = 'inflation_indices'
        unique_together = [['index_name', 'index_date']]


class CostCategoryInflationMapping(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inflation_mappings',
    )
    cost_category = models.CharField(max_length=40)
    index_name = models.CharField(max_length=80)
    weight = models.DecimalField(max_digits=5, decimal_places=4, default=1)

    class Meta:
        db_table = 'cost_category_inflation_mappings'


class EconomicSnapshot(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='economic_snapshots')
    snapshot_date = models.DateField()
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    inflation_adj_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    financing_cost = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    revenue_to_date = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    accounting_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    real_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    economic_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    working_capital = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    avg_payment_delay_days = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'economic_snapshots'
        unique_together = [['project', 'snapshot_date']]


class SimulationResult(UUIDModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='simulation_results')
    run_at = models.DateTimeField(auto_now_add=True)
    iterations = models.IntegerField(null=True, blank=True)
    p10_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p50_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    p90_profit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    prob_of_loss = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    max_working_capital = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sensitivity_json = models.JSONField(default=dict, blank=True)
    scenario_params_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'simulation_results'

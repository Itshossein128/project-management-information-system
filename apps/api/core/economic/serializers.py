from rest_framework import serializers

from economic.models import EconomicSnapshot, InflationIndex, SimulationResult


class EconomicSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicSnapshot
        fields = [
            'id', 'snapshot_date', 'actual_cost', 'inflation_adj_cost', 'financing_cost',
            'revenue_to_date', 'accounting_profit', 'real_profit', 'economic_profit',
            'working_capital', 'avg_payment_delay_days',
        ]


class SimulationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationResult
        fields = [
            'id', 'run_at', 'iterations', 'p10_profit', 'p50_profit', 'p90_profit',
            'prob_of_loss', 'max_working_capital', 'sensitivity_json', 'scenario_params_json',
        ]


class InflationIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = InflationIndex
        fields = ['id', 'index_name', 'index_date', 'index_value', 'source']

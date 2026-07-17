from rest_framework import serializers

from economic.models import CostCategoryInflationMapping, EconomicSnapshot, InflationIndex, SimulationResult


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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['p10'] = data.get('p10_profit')
        data['p50'] = data.get('p50_profit')
        data['p90'] = data.get('p90_profit')
        return data


class CostCategoryInflationMappingSerializer(serializers.ModelSerializer):
    is_global = serializers.SerializerMethodField()

    class Meta:
        model = CostCategoryInflationMapping
        fields = ['id', 'cost_category', 'index_name', 'weight', 'is_global']
        read_only_fields = ['id', 'is_global']

    def get_is_global(self, obj) -> bool:
        return obj.project_id is None


class InflationIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = InflationIndex
        fields = ['id', 'index_name', 'index_date', 'index_value', 'source']

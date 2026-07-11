"""Cash flow serializers."""

from rest_framework import serializers

from cash_flow.models import (
    INFLOW_CATEGORIES,
    OUTFLOW_CATEGORIES,
    CashFlowForecast,
    CashTransaction,
    CashTransactionType,
    InflowCategory,
    OutflowCategory,
)
from common.serializers import JalaliDateField


def _format_amount(value) -> str:
    if value is None:
        return '0'
    return f'{float(value):,.0f}'


CATEGORY_LABELS = {
    **{c.value: c.label for c in InflowCategory},
    **{c.value: c.label for c in OutflowCategory},
}


class CashTransactionSerializer(serializers.ModelSerializer):
    tx_date = JalaliDateField()
    due_date = JalaliDateField(required=False, allow_null=True)
    actual_date = JalaliDateField(required=False, allow_null=True)
    amount_display = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = CashTransaction
        fields = [
            'id',
            'tx_date',
            'tx_type',
            'category',
            'category_label',
            'amount',
            'amount_display',
            'description',
            'counterparty',
            'document_ref',
            'is_forecast',
            'due_date',
            'actual_date',
            'ipc',
            'contract',
            'source',
        ]
        read_only_fields = ['id', 'ipc', 'contract']

    def get_amount_display(self, obj):
        return _format_amount(obj.amount)

    def get_category_label(self, obj):
        return CATEGORY_LABELS.get(obj.category, obj.category)

    def get_source(self, obj):
        return 'ipc' if obj.ipc_id else 'direct'

    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, attrs):
        tx_type = attrs.get('tx_type', getattr(self.instance, 'tx_type', None))
        category = attrs.get('category', getattr(self.instance, 'category', ''))
        if tx_type == CashTransactionType.IN and category and category not in INFLOW_CATEGORIES:
            raise serializers.ValidationError({'category': 'Invalid inflow category.'})
        if tx_type == CashTransactionType.OUT and category and category not in OUTFLOW_CATEGORIES:
            raise serializers.ValidationError({'category': 'Invalid outflow category.'})
        return attrs


class CashFlowForecastSerializer(serializers.ModelSerializer):
    month = serializers.DateField(format='%Y-%m', input_formats=['%Y-%m', '%Y-%m-%d'])
    net_monthly = serializers.SerializerMethodField()

    class Meta:
        model = CashFlowForecast
        fields = [
            'id',
            'month',
            'expected_inflow',
            'expected_outflow',
            'net_monthly',
            'confidence_pct',
            'notes',
        ]
        read_only_fields = ['id']

    def get_net_monthly(self, obj):
        return float((obj.expected_inflow or 0) - (obj.expected_outflow or 0))

    def validate_month(self, value):
        return value.replace(day=1)

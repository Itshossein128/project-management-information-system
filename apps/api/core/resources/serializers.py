"""Resources serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from resources.models import InventoryTransaction, Material, MaterialRequest


class MaterialSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.symbol', read_only=True, default='')

    class Meta:
        model = Material
        fields = [
            'id',
            'material_code',
            'material_name',
            'unit',
            'unit_name',
            'category',
            'discipline',
            'location',
            'block_type',
            'estimated_total_qty',
            'qty_per_block',
            'min_stock_level',
        ]
        read_only_fields = ['id']


class MaterialRequestSerializer(serializers.ModelSerializer):
    request_date = JalaliDateField(required=False, allow_null=True)
    required_by_date = JalaliDateField(required=False, allow_null=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)

    class Meta:
        model = MaterialRequest
        fields = [
            'id',
            'material',
            'material_name',
            'request_number',
            'requested_qty',
            'unit',
            'request_date',
            'required_by_date',
            'status',
            'notes',
        ]
        read_only_fields = ['id', 'request_number']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    tx_date = JalaliDateField()
    material_name = serializers.CharField(source='material.material_name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = [
            'id',
            'material',
            'material_name',
            'tx_date',
            'tx_type',
            'quantity',
            'unit_cost',
            'block_ref',
            'document_ref',
            'supplier',
            'activity',
            'daily_report',
            'notes',
        ]
        read_only_fields = ['id', 'daily_report']

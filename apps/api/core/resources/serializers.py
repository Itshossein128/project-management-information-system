"""Resources serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from resources.models import InventoryTransaction, Material, MaterialRequest, PurchaseOrder


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
    activity_name = serializers.CharField(source='activity.activity_name', read_only=True, default='')
    purchase_order = serializers.SerializerMethodField()

    class Meta:
        model = MaterialRequest
        fields = [
            'id',
            'material',
            'material_name',
            'activity',
            'activity_name',
            'request_number',
            'requested_qty',
            'unit',
            'request_date',
            'required_by_date',
            'status',
            'approved_at',
            'notes',
            'purchase_order',
        ]
        read_only_fields = ['id', 'request_number', 'status', 'approved_at', 'purchase_order']
        extra_kwargs = {'unit': {'required': False, 'allow_blank': True}}

    def get_purchase_order(self, obj):
        try:
            po = obj.purchase_order
        except PurchaseOrder.DoesNotExist:
            return None
        if po.is_deleted:
            return None
        return PurchaseOrderSerializer(po).data


class PurchaseOrderSerializer(serializers.ModelSerializer):
    order_date = JalaliDateField()
    expected_delivery_date = JalaliDateField(required=False, allow_null=True)
    actual_delivery_date = JalaliDateField(required=False, allow_null=True)
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'po_number',
            'supplier',
            'supplier_name',
            'order_date',
            'expected_delivery_date',
            'actual_delivery_date',
            'ordered_qty',
            'unit_price',
            'notes',
        ]
        read_only_fields = ['id', 'po_number']


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

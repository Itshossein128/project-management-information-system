"""PO, inventory allocation, and transfer serializers."""
from decimal import Decimal
from rest_framework import serializers

from procurement.models import InventoryAllocation, InternalTransfer


class InventoryAllocationSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    block_code = serializers.CharField(source='block.block_code', read_only=True)
    available_qty = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAllocation
        fields = [
            'id', 'requisition_item', 'block', 'block_code',
            'material', 'material_name', 'mr_tag',
            'allocated_qty', 'received_qty', 'issued_qty', 'available_qty',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'mr_tag', 'created_at', 'updated_at']

    def get_available_qty(self, obj):
        return obj.received_qty - obj.issued_qty


class InternalTransferSerializer(serializers.ModelSerializer):
    source_block_code = serializers.CharField(source='source_block.block_code', read_only=True)
    target_block_code = serializers.CharField(source='target_block.block_code', read_only=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InternalTransfer
        fields = [
            'id', 'source_block', 'source_block_code',
            'target_block', 'target_block_code',
            'material', 'material_name', 'quantity', 'reason',
            'approved_by', 'approved_at', 'status', 'status_display',
            'cost_adjustment_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'approved_by', 'approved_at', 'status',
            'status_display', 'created_at', 'updated_at',
        ]

    def validate(self, attrs):
        if attrs.get('source_block') == attrs.get('target_block'):
            raise serializers.ValidationError(
                {'target_block': 'Source and target blocks must be different.'}
            )
        return attrs


class GRNSerializer(serializers.Serializer):
    """Input for recording goods receipt (GRN)."""
    requisition_item_id = serializers.UUIDField()
    received_qty = serializers.DecimalField(max_digits=18, decimal_places=4, min_value=Decimal('0.0001'))


class IssueStockSerializer(serializers.Serializer):
    """Input for issuing stock against an allocation."""
    allocation_id = serializers.UUIDField()
    issue_qty = serializers.DecimalField(max_digits=18, decimal_places=4, min_value=Decimal('0.0001'))


class AssignItemsSerializer(serializers.Serializer):
    """Input for line-item splitting assignment."""

    class AssignmentSerializer(serializers.Serializer):
        item_id = serializers.UUIDField()
        assigned_to_id = serializers.IntegerField(allow_null=True)

    assignments = AssignmentSerializer(many=True, min_length=1)


class PartialApproveSerializer(serializers.Serializer):
    """Input for partial approval of requisition items."""

    class ItemApprovalSerializer(serializers.Serializer):
        item_id = serializers.UUIDField()
        approved_qty = serializers.DecimalField(
            max_digits=18, decimal_places=4,
            allow_null=True, min_value=Decimal('0'),
        )

    approvals = ItemApprovalSerializer(many=True, min_length=1)

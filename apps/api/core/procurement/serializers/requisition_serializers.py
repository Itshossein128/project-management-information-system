"""Requisition serializers."""
from rest_framework import serializers

from procurement.models import (
    Block,
    RequisitionHeader,
    RequisitionItem,
    RequisitionStatus,
    RequisitionType,
    RequisitionPriority,
    ItemStatus,
)


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = [
            'id', 'project', 'block_code', 'block_name', 'wbs',
            'budget', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RequisitionItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_code = serializers.CharField(source='material.material_code', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = RequisitionItem
        fields = [
            'id', 'line_number', 'material', 'material_name', 'material_code',
            'wbs_node', 'requested_qty', 'approved_qty', 'purchased_qty',
            'status', 'status_display', 'assigned_to', 'assigned_to_name', 'notes',
        ]
        read_only_fields = ['id', 'purchased_qty', 'status_display', 'material_name', 'material_code']

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return str(obj.assigned_to)
        return None


class RequisitionHeaderSerializer(serializers.ModelSerializer):
    """Full detail serializer with nested items."""
    items = RequisitionItemSerializer(many=True, read_only=True)
    block_code = serializers.CharField(source='block.block_code', read_only=True)
    block_name = serializers.CharField(source='block.block_name', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requisition_type_display = serializers.CharField(source='get_requisition_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = RequisitionHeader
        fields = [
            'id', 'project', 'block', 'block_code', 'block_name',
            'requisition_number', 'requisition_type', 'requisition_type_display',
            'priority', 'priority_display', 'urgency', 'status', 'status_display',
            'requested_by', 'requested_by_name', 'request_date', 'required_by_date',
            'is_grn_provisional', 'notes', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'requisition_number', 'status', 'created_at', 'updated_at',
            'block_code', 'block_name', 'requested_by_name', 'status_display',
            'requisition_type_display', 'priority_display',
        ]

    def get_requested_by_name(self, obj):
        return str(obj.requested_by) if obj.requested_by else None


class RequisitionHeaderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a requisition with items."""
    items = RequisitionItemSerializer(many=True)

    class Meta:
        model = RequisitionHeader
        fields = [
            'project', 'block', 'requisition_type', 'priority', 'urgency',
            'request_date', 'required_by_date', 'is_grn_provisional', 'notes', 'items',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        header = RequisitionHeader.objects.create(
            **validated_data,
            requested_by=user,
            status=RequisitionStatus.DRAFT,
            created_by=user,
            updated_by=user,
        )
        for idx, item_data in enumerate(items_data, start=1):
            item_data.setdefault('line_number', idx)
            RequisitionItem.objects.create(
                header=header,
                created_by=user,
                updated_by=user,
                **item_data,
            )
        return header

    def validate(self, attrs):
        items = attrs.get('items', [])
        if not items:
            raise serializers.ValidationError({'items': 'At least one item is required.'})
        return attrs


class RequisitionHeaderListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer."""
    block_code = serializers.CharField(source='block.block_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requisition_type_display = serializers.CharField(source='get_requisition_type_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = RequisitionHeader
        fields = [
            'id', 'requisition_number', 'block', 'block_code',
            'status', 'status_display', 'requisition_type', 'requisition_type_display',
            'priority', 'request_date', 'required_by_date', 'item_count',
        ]

    def get_item_count(self, obj):
        return obj.items.filter(is_deleted=False).count()

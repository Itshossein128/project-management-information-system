"""Requisition serializers."""
from rest_framework import serializers

from procurement.models import (
    Block,
    BlockKind,
    RequisitionHeader,
    RequisitionItem,
    RequisitionScope,
    RequisitionStatus,
    RequisitionType,
    RequisitionPriority,
    ItemStatus,
    WORKSHOP_BLOCK_CODE,
)
from procurement.services.fast_track_notify import notify_fast_track_requisition
from procurement.services.workshop_block_service import ensure_workshop_block


class BlockSerializer(serializers.ModelSerializer):
    wbs_code = serializers.CharField(source='wbs.wbs_code', read_only=True, default=None)
    wbs_name = serializers.CharField(source='wbs.wbs_name', read_only=True, default=None)
    block_kind_display = serializers.CharField(source='get_block_kind_display', read_only=True)
    is_system = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = [
            'id', 'project', 'block_code', 'block_name', 'wbs',
            'wbs_code', 'wbs_name',
            'budget', 'is_active', 'block_kind', 'block_kind_display', 'is_system',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'project', 'created_at', 'updated_at',
            'wbs_code', 'wbs_name', 'block_kind', 'block_kind_display', 'is_system',
        ]

    def get_is_system(self, obj):
        return obj.block_kind == BlockKind.WORKSHOP

    def validate_block_code(self, value):
        if self.instance and self.instance.block_kind == BlockKind.WORKSHOP:
            raise serializers.ValidationError('System workshop block cannot be modified.')
        project_id = self.context['view'].get_project_id()
        qs = Block.objects.filter(project_id=project_id, block_code=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'A block with this code already exists in the project.'
            )
        return value

    def validate_wbs(self, value):
        if value is None:
            return value
        project_id = self.context['view'].get_project_id()
        if str(value.project_id) != str(project_id):
            raise serializers.ValidationError(
                'WBS node must belong to the same project.'
            )
        return value

    def validate(self, attrs):
        if self.instance and self.instance.block_kind == BlockKind.WORKSHOP:
            raise serializers.ValidationError(
                {'detail': 'System workshop block cannot be modified.'}
            )
        return attrs


class RequisitionItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_code = serializers.CharField(source='material.material_code', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    line_number = serializers.IntegerField(required=False)

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
    block_code = serializers.SerializerMethodField()
    block_name = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requisition_type_display = serializers.CharField(source='get_requisition_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    workflow_timeline = serializers.SerializerMethodField()
    next_approver = serializers.SerializerMethodField()
    approval_summary = serializers.SerializerMethodField()

    class Meta:
        model = RequisitionHeader
        fields = [
            'id', 'project', 'scope', 'scope_display', 'block', 'block_code', 'block_name',
            'requisition_number', 'requisition_type', 'requisition_type_display',
            'priority', 'priority_display', 'urgency', 'status', 'status_display',
            'requested_by', 'requested_by_name', 'request_date', 'required_by_date',
            'is_grn_provisional', 'notes', 'items',
            'workflow_timeline', 'next_approver', 'approval_summary',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'requisition_number', 'status', 'created_at', 'updated_at',
            'block_code', 'block_name', 'requested_by_name', 'status_display',
            'requisition_type_display', 'priority_display', 'scope_display',
            'workflow_timeline', 'next_approver', 'approval_summary',
        ]

    def get_block_code(self, obj):
        if obj.scope == RequisitionScope.WORKSHOP:
            return WORKSHOP_BLOCK_CODE
        return obj.block.block_code

    def get_block_name(self, obj):
        if obj.scope == RequisitionScope.WORKSHOP:
            return obj.block.block_name
        return obj.block.block_name

    def get_requested_by_name(self, obj):
        return str(obj.requested_by) if obj.requested_by else None

    def get_workflow_timeline(self, obj):
        from procurement.services.workflow_timeline_service import build_workflow_timeline

        return build_workflow_timeline(obj)

    def get_next_approver(self, obj):
        from procurement.services.workflow_timeline_service import get_next_approver

        return get_next_approver(obj)

    def get_approval_summary(self, obj):
        from procurement.services.workflow_timeline_service import build_approval_summary

        return build_approval_summary(obj)


class RequisitionHeaderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a requisition with items."""
    items = RequisitionItemSerializer(many=True)
    scope = serializers.ChoiceField(
        choices=RequisitionScope.choices,
        default=RequisitionScope.BLOCK,
        required=False,
    )
    block = serializers.PrimaryKeyRelatedField(
        queryset=Block.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = RequisitionHeader
        fields = [
            'id', 'project', 'scope', 'block', 'requisition_type', 'priority', 'urgency',
            'request_date', 'required_by_date', 'is_grn_provisional', 'notes', 'items',
        ]
        read_only_fields = ['id', 'block']
        extra_kwargs = {
            'block': {'required': False, 'allow_null': True},
        }

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
        from procurement.services.workflow_timeline_service import log_requisition_created

        log_requisition_created(header, user)
        notify_fast_track_requisition(header)
        return header

    def validate(self, attrs):
        items = attrs.get('items', [])
        if not items:
            raise serializers.ValidationError({'items': 'At least one item is required.'})

        scope = attrs.get('scope', RequisitionScope.BLOCK)
        block = attrs.get('block')
        project = attrs.get('project')

        req_type = attrs.get('requisition_type', RequisitionType.PLANNED)
        default_priority = {
            RequisitionType.PLANNED: RequisitionPriority.NORMAL,
            RequisitionType.FAST_TRACK: RequisitionPriority.HIGH,
            RequisitionType.POST_FACTO: RequisitionPriority.EMERGENCY,
        }.get(req_type, RequisitionPriority.NORMAL)
        if not attrs.get('priority'):
            attrs['priority'] = default_priority
        if req_type == RequisitionType.POST_FACTO:
            attrs.setdefault('is_grn_provisional', True)

        if scope == RequisitionScope.WORKSHOP:
            workshop_block = ensure_workshop_block(project, created_by=self.context['request'].user)
            attrs['block'] = workshop_block
        else:
            if not block:
                raise serializers.ValidationError({'block': 'Block is required for block-scoped requests.'})
            if block.block_kind == BlockKind.WORKSHOP:
                raise serializers.ValidationError(
                    {'block': 'Workshop system block cannot be selected for block-scoped requests.'}
                )
            if str(block.project_id) != str(project.id):
                raise serializers.ValidationError({'block': 'Block must belong to the same project.'})

        return attrs


class RequisitionHeaderListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer."""
    block_code = serializers.SerializerMethodField()
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requisition_type_display = serializers.CharField(source='get_requisition_type_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    last_action_at = serializers.SerializerMethodField()
    last_action_by_name = serializers.SerializerMethodField()
    last_action_display = serializers.SerializerMethodField()
    next_approver_role = serializers.SerializerMethodField()
    next_approver_role_label = serializers.SerializerMethodField()
    workflow_progress = serializers.SerializerMethodField()
    workflow_step_label = serializers.SerializerMethodField()

    class Meta:
        model = RequisitionHeader
        fields = [
            'id', 'requisition_number', 'scope', 'scope_display', 'block', 'block_code',
            'status', 'status_display', 'requisition_type', 'requisition_type_display',
            'priority', 'request_date', 'required_by_date', 'item_count',
            'last_action_at', 'last_action_by_name', 'last_action_display',
            'next_approver_role', 'next_approver_role_label',
            'workflow_progress', 'workflow_step_label',
        ]

    def get_block_code(self, obj):
        if obj.scope == RequisitionScope.WORKSHOP:
            return WORKSHOP_BLOCK_CODE
        return obj.block.block_code

    def get_item_count(self, obj):
        # ⚡ Bolt: Use python iteration over prefetched items collection to avoid N+1 queries from .filter().count()
        return sum(1 for item in obj.items.all() if not item.is_deleted)

    def _get_last_action_summary(self, obj):
        if hasattr(obj, '_cached_last_action'):
            return obj._cached_last_action
        from procurement.services.workflow_timeline_service import get_last_action_summary

        obj._cached_last_action = get_last_action_summary(obj)
        return obj._cached_last_action

    def get_last_action_at(self, obj):
        # ⚡ Bolt: Fast-path for annotated subquery field from RequisitionHeaderViewSet list queryset
        if hasattr(obj, '_last_action_at'):
            val = obj._last_action_at
            if val is None:
                return None
            return val.isoformat() if hasattr(val, 'isoformat') else str(val)
        summary = self._get_last_action_summary(obj)
        return summary['at'] if summary else None

    def get_last_action_by_name(self, obj):
        # ⚡ Bolt: Fast-path for annotated subquery field from RequisitionHeaderViewSet list queryset
        if hasattr(obj, '_last_action_by_name'):
            return obj._last_action_by_name
        summary = self._get_last_action_summary(obj)
        return summary['by_name'] if summary else None

    def get_last_action_display(self, obj):
        summary = self._get_last_action_summary(obj)
        return summary['action_display'] if summary else None

    def get_next_approver_role(self, obj):
        from procurement.services.workflow_timeline_service import get_next_approver

        approver = get_next_approver(obj)
        return approver['role'] if approver else None

    def get_next_approver_role_label(self, obj):
        from procurement.services.workflow_timeline_service import get_next_approver

        approver = get_next_approver(obj)
        return approver['role_label'] if approver else None

    def get_workflow_progress(self, obj):
        from procurement.services.workflow_timeline_service import compute_workflow_progress

        return compute_workflow_progress(obj)

    def get_workflow_step_label(self, obj):
        from procurement.services.workflow_timeline_service import get_current_step_label

        return get_current_step_label(obj)

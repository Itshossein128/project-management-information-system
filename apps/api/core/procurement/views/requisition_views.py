"""Requisition CRUD views."""
from django.db.models import OuterRef, Prefetch, Subquery
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from procurement.models import (
    ApprovalLog,
    Block,
    BlockKind,
    RequisitionHeader,
    RequisitionItem,
    RequisitionStatus,
)
from procurement.serializers import (
    BlockSerializer,
    RequisitionHeaderCreateSerializer,
    RequisitionHeaderListSerializer,
    RequisitionHeaderSerializer,
    RequisitionItemSerializer,
)


class BlockViewSet(ProjectScopedViewSet):
    """CRUD for project blocks (virtual warehouses)."""
    queryset = Block.objects.select_related('project', 'wbs')
    serializer_class = BlockSerializer
    view_permission = 'view_procurement'
    edit_permission = 'edit_reports'

    def get_queryset(self):
        qs = super().get_queryset().order_by('block_code')
        if self.action != 'list':
            return qs

        params = self.request.query_params
        include_system = params.get('include_system', '').lower() in ('1', 'true', 'yes')
        exclude_system_raw = params.get('exclude_system')
        exclude_system_false = (
            exclude_system_raw is not None
            and exclude_system_raw.lower() in ('0', 'false', 'no')
        )
        block_kind = params.get('block_kind')

        if block_kind:
            qs = qs.filter(block_kind=block_kind)
        elif include_system or exclude_system_false:
            pass
        else:
            qs = qs.exclude(block_kind=BlockKind.WORKSHOP)

        return qs

    def perform_update(self, serializer):
        if serializer.instance.block_kind == BlockKind.WORKSHOP:
            raise ValidationError({'detail': 'System workshop block cannot be modified.'})
        super().perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.block_kind == BlockKind.WORKSHOP:
            raise ValidationError({'detail': 'System workshop block cannot be deleted.'})
        if RequisitionHeader.objects.filter(block=instance, is_deleted=False).exists():
            raise ValidationError(
                {'detail': 'Cannot delete a block that has purchase requisitions.'}
            )
        return super().destroy(request, *args, **kwargs)


class RequisitionHeaderViewSet(viewsets.ModelViewSet):
    """
    CRUD for requisition headers (purchase requests).
    Editing is only allowed in DRAFT status.
    """

    def get_serializer_class(self):
        if self.action == 'create':
            return RequisitionHeaderCreateSerializer
        if self.action == 'list':
            return RequisitionHeaderListSerializer
        return RequisitionHeaderSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        qs = RequisitionHeader.objects.filter(is_deleted=False)
        if project_id:
            qs = qs.filter(project_id=project_id)

        params = self.request.query_params
        block_id = params.get('block')
        if block_id:
            qs = qs.filter(block_id=block_id)
        req_status = params.get('status')
        if req_status:
            qs = qs.filter(status=req_status)
        req_type = params.get('type')
        if req_type:
            qs = qs.filter(requisition_type=req_type)
        priority = params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)
        scope = params.get('scope')
        if scope:
            qs = qs.filter(scope=scope)

        if self.action == 'list':
            latest_log = ApprovalLog.objects.filter(
                requisition=OuterRef('pk'),
            ).order_by('-performed_at')
            qs = qs.annotate(
                _last_action_at=Subquery(latest_log.values('performed_at')[:1]),
                _last_action_by_name=Subquery(
                    latest_log.values('performed_by__full_name')[:1]
                ),
            ).prefetch_related(
                Prefetch(
                    'approval_logs',
                    queryset=ApprovalLog.objects.select_related('performed_by').order_by(
                        '-performed_at'
                    ),
                ),
            )
        elif self.action == 'retrieve':
            qs = qs.prefetch_related(
                Prefetch(
                    'approval_logs',
                    queryset=ApprovalLog.objects.select_related('performed_by').order_by(
                        'performed_at'
                    ),
                ),
            )

        return qs.select_related('project', 'block', 'requested_by').prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != RequisitionStatus.DRAFT:
            raise ValidationError(
                {'detail': 'Requisition can only be edited in DRAFT status.'}
            )
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != RequisitionStatus.DRAFT:
            raise ValidationError(
                {'detail': 'Only DRAFT requisitions can be deleted.'}
            )
        instance.soft_delete(user=self.request.user)


class RequisitionItemHoldView(APIView):
    """Put a requisition item on hold (awaiting budget)."""

    def patch(self, request, project_pk=None, pk=None):
        from procurement.services.requisition_service import put_item_on_hold

        item = get_object_or_404(
            RequisitionItem,
            id=pk,
            header__project_id=project_pk,
            is_deleted=False,
        )
        item = put_item_on_hold(item, request.user)
        return Response(RequisitionItemSerializer(item).data)

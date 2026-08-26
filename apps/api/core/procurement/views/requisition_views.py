"""Requisition CRUD views."""
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from procurement.models import (
    Block,
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


class BlockViewSet(viewsets.ModelViewSet):
    """CRUD for project blocks (virtual warehouses)."""
    serializer_class = BlockSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        qs = Block.objects.filter(is_deleted=False)
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.select_related('project', 'wbs').order_by('block_code')

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


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

        # Optional query filters
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

        return qs.select_related('project', 'block', 'requested_by').prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save()  # create handled inside serializer

    def perform_update(self, serializer):
        # Only allow editing in DRAFT
        instance = self.get_object()
        if instance.status != RequisitionStatus.DRAFT:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                {'detail': 'Requisition can only be edited in DRAFT status.'}
            )
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != RequisitionStatus.DRAFT:
            from rest_framework.exceptions import ValidationError
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

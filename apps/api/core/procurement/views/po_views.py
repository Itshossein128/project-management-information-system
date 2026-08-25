"""Procurement operations: assign items, partial approval, GRN, issue stock, transfers."""
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from procurement.models import (
    Block,
    InventoryAllocation,
    InternalTransfer,
    RequisitionHeader,
    RequisitionItem,
)
from procurement.serializers import (
    AssignItemsSerializer,
    GRNSerializer,
    InventoryAllocationSerializer,
    InternalTransferSerializer,
    IssueStockSerializer,
    PartialApproveSerializer,
    RequisitionItemSerializer,
)


class AssignItemsView(APIView):
    """Line-item splitting: assign requisition items to procurement officers."""

    def post(self, request, project_pk=None, pk=None):
        from procurement.services.requisition_service import assign_items

        requisition = get_object_or_404(
            RequisitionHeader,
            id=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        serializer = AssignItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_items = assign_items(
            requisition,
            assignments=serializer.validated_data['assignments'],
            user=request.user,
        )
        return Response(RequisitionItemSerializer(updated_items, many=True).data)


class PartialApproveView(APIView):
    """Partially approve requisition items (sets approved_qty or ON_HOLD)."""

    def post(self, request, project_pk=None, pk=None):
        from procurement.services.requisition_service import partial_approve_items

        requisition = get_object_or_404(
            RequisitionHeader,
            id=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        serializer = PartialApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_items = partial_approve_items(
            requisition,
            approvals=serializer.validated_data['approvals'],
            user=request.user,
        )
        return Response(RequisitionItemSerializer(updated_items, many=True).data)


class GRNView(APIView):
    """Record goods receipt (GRN) and tag to block allocation."""

    def post(self, request, project_pk=None, block_pk=None):
        from procurement.services.inventory_lock_service import record_grn

        block = get_object_or_404(Block, id=block_pk, project_id=project_pk, is_deleted=False)
        serializer = GRNSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = get_object_or_404(
            RequisitionItem,
            id=serializer.validated_data['requisition_item_id'],
            header__block=block,
            is_deleted=False,
        )
        allocation = record_grn(item, serializer.validated_data['received_qty'], request.user)
        return Response(InventoryAllocationSerializer(allocation).data, status=status.HTTP_201_CREATED)


class IssueStockView(APIView):
    """Issue stock from a block allocation (Hard Stop enforced)."""

    def post(self, request, project_pk=None, block_pk=None):
        from procurement.services.inventory_lock_service import issue_stock

        block = get_object_or_404(Block, id=block_pk, project_id=project_pk, is_deleted=False)
        serializer = IssueStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        allocation = get_object_or_404(
            InventoryAllocation,
            id=serializer.validated_data['allocation_id'],
            block=block,
            is_deleted=False,
        )
        allocation = issue_stock(allocation, serializer.validated_data['issue_qty'], request.user)
        return Response(InventoryAllocationSerializer(allocation).data)


class BlockStockView(APIView):
    """Get reserved/received/issued stock summary for a block."""

    def get(self, request, project_pk=None, block_pk=None):
        from procurement.services.inventory_lock_service import get_block_stock

        block = get_object_or_404(Block, id=block_pk, project_id=project_pk, is_deleted=False)
        stock_data = get_block_stock(block)
        return Response(stock_data)


class InternalTransferViewSet(viewsets.ModelViewSet):
    """CRUD for inter-block material transfers."""
    serializer_class = InternalTransferSerializer
    http_method_names = ['get', 'post', 'head', 'options']  # read + create only

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        qs = InternalTransfer.objects.filter(is_deleted=False)
        if project_id:
            qs = qs.filter(
                source_block__project_id=project_id,
            )
        return qs.select_related('source_block', 'target_block', 'material', 'approved_by')

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class TransferApproveView(APIView):
    """Approve an inter-block transfer (PM only)."""

    def post(self, request, project_pk=None, pk=None):
        from procurement.services.transfer_service import approve_transfer

        transfer = get_object_or_404(
            InternalTransfer,
            id=pk,
            source_block__project_id=project_pk,
            is_deleted=False,
        )
        transfer = approve_transfer(transfer, request.user)
        return Response(InternalTransferSerializer(transfer).data)


class TransferRejectView(APIView):
    """Reject an inter-block transfer."""

    def post(self, request, project_pk=None, pk=None):
        from procurement.services.transfer_service import reject_transfer

        transfer = get_object_or_404(
            InternalTransfer,
            id=pk,
            source_block__project_id=project_pk,
            is_deleted=False,
        )
        reason = request.data.get('reason', '')
        transfer = reject_transfer(transfer, request.user, reason=reason)
        return Response(InternalTransferSerializer(transfer).data)

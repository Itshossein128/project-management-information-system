from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from contracts.collection_service import add_collection, collections_total, remaining_receivable
from contracts.models import IPC, IPCCollection
from contracts.serializers import IPCCollectionSerializer
from permissions.project import HasProjectPermission, IsProjectMember


class IPCCollectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.request.method == 'GET':
            return 'view_contracts'
        return 'edit_contracts'

    @extend_schema(summary='List IPC collections', tags=['Central Data'])
    def get(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        rows = IPCCollection.objects.filter(ipc=ipc, is_deleted=False)
        return Response(
            {
                'results': IPCCollectionSerializer(rows, many=True).data,
                'collections_total': str(collections_total(ipc)),
                'remaining_receivable': str(remaining_receivable(ipc)),
                'gross_amount': str(ipc.gross_amount),
                'net_amount': str(ipc.net_amount) if ipc.net_amount is not None else None,
            }
        )

    @extend_schema(summary='Add IPC collection', tags=['Central Data'])
    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        before_gross = ipc.gross_amount
        before_net = ipc.net_amount
        serializer = IPCCollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        row = add_collection(
            ipc=ipc,
            amount=data['amount'],
            collected_at=data['collected_at'],
            user=request.user,
            currency=data.get('currency', 'IRR'),
            fx_rate=data.get('fx_rate'),
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
        )
        ipc.refresh_from_db()
        assert ipc.gross_amount == before_gross
        assert ipc.net_amount == before_net
        return Response(IPCCollectionSerializer(row).data, status=status.HTTP_201_CREATED)


class IPCCollectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Soft-delete IPC collection', tags=['Central Data'])
    def delete(self, request, project_pk=None, pk=None, collection_id=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        row = get_object_or_404(IPCCollection, pk=collection_id, ipc=ipc, is_deleted=False)
        row.soft_delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

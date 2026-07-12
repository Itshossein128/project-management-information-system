"""Material balance and inventory API."""

from django.db.models import Max
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.viewsets import ProjectScopedViewSet
from permissions.project import HasProjectPermission, IsProjectMember
from resources.models import InventoryTransaction, Material, MaterialRequest
from resources.serializers import (
    InventoryTransactionSerializer,
    MaterialRequestSerializer,
    MaterialSerializer,
)
from resources.services.balance_service import compute_material_balance, material_balance_list, running_balance


class MaterialViewSet(ProjectScopedViewSet):
    queryset = Material.objects.select_related('unit')
    serializer_class = MaterialSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def perform_create(self, serializer):
        serializer.save(project_id=self.get_project_id())


class MaterialRequestViewSet(ProjectScopedViewSet):
    queryset = MaterialRequest.objects.select_related('material')
    serializer_class = MaterialRequestSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def perform_create(self, serializer):
        material = serializer.validated_data['material']
        max_num = (
            MaterialRequest.objects.filter(project_id=self.get_project_id(), material=material).aggregate(
                m=Max('request_number')
            )['m']
            or 0
        )
        serializer.save(
            project_id=self.get_project_id(),
            request_number=max_num + 1,
        )


class InventoryTransactionViewSet(ProjectScopedViewSet):
    queryset = InventoryTransaction.objects.select_related('material', 'supplier')
    serializer_class = InventoryTransactionSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    AUTO_MSG = 'این تراکنش از گزارش روزانه ایجاد شده و قابل ویرایش مستقیم نیست'

    def perform_create(self, serializer):
        serializer.save(project_id=self.get_project_id())

    def update(self, request, *args, **kwargs):
        if self.get_object().daily_report_id:
            return Response({'detail': self.AUTO_MSG}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().daily_report_id:
            return Response({'detail': self.AUTO_MSG}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class MaterialBalanceListView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Material balance list', tags=['Materials'])
    def get(self, request, project_pk=None):
        data = material_balance_list(
            project_pk,
            discipline=request.query_params.get('discipline'),
            location=request.query_params.get('location'),
            block_type=request.query_params.get('block_type'),
            low_stock=request.query_params.get('low_stock', '').lower() == 'true',
        )
        return Response(data)


class MaterialBalanceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Material balance detail', tags=['Materials'])
    def get(self, request, project_pk=None, mid=None):
        material = Material.objects.get(pk=mid, project_id=project_pk)
        balance = compute_material_balance(material)
        requests = MaterialRequestSerializer(
            MaterialRequest.objects.filter(material=material, is_deleted=False),
            many=True,
        ).data
        transactions = InventoryTransactionSerializer(
            InventoryTransaction.objects.filter(material=material, is_deleted=False).order_by('-tx_date')[:100],
            many=True,
        ).data
        return Response({**balance, 'requests': requests, 'transactions': transactions})


class InventoryRunningBalanceView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Running balance by date', tags=['Materials'])
    def get(self, request, project_pk=None):
        material_id = request.query_params.get('material_id')
        if not material_id:
            return Response({'detail': 'material_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(running_balance(material_id))

"""Material balance and inventory API."""

from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from common.viewsets import ProjectScopedViewSet
from permissions.project import HasProjectPermission, IsProjectMember
from resources.models import InventoryTransaction, Material, MaterialRequest, PurchaseOrder
from resources.serializers import (
    InventoryTransactionSerializer,
    MaterialRequestSerializer,
    MaterialSerializer,
    PurchaseOrderSerializer,
)
from resources.services.balance_service import compute_material_balance, material_balance_list, running_balance
from resources.services.consumption_service import material_consumption_report
from resources.services.procurement_service import (
    approve_material_request,
    cancel_material_request,
    deliver_purchase_order,
    place_purchase_order,
)


class MaterialViewSet(ProjectScopedViewSet):
    queryset = Material.objects.select_related('unit')
    serializer_class = MaterialSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'



@extend_schema_view(
    list=extend_schema(summary='List material requests', tags=['Procurement']),
    create=extend_schema(summary='Create material request', tags=['Procurement']),
    retrieve=extend_schema(summary='Material request detail', tags=['Procurement']),
    partial_update=extend_schema(summary='Update material request', tags=['Procurement']),
    destroy=extend_schema(summary='Delete material request', tags=['Procurement']),
)
class MaterialRequestViewSet(ProjectScopedViewSet):
    queryset = MaterialRequest.objects.select_related('material', 'activity').prefetch_related(
        Prefetch('purchase_order', queryset=PurchaseOrder.objects.select_related('supplier')),
    )
    serializer_class = MaterialRequestSerializer
    view_permission = 'view_procurement'
    edit_permission = 'edit_reports'

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return 'view_procurement'
        if self.action == 'approve':
            return 'approve_procurement'
        if self.action in ('place_order', 'deliver', 'cancel'):
            return 'edit_procurement'
        return self.edit_permission

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-request_date', '-request_number')

    def perform_create(self, serializer):
        material = serializer.validated_data['material']
        unit = serializer.validated_data.get('unit') or (
            material.unit.symbol if getattr(material, 'unit_id', None) else ''
        )
        max_num = (
            MaterialRequest.objects.filter(project_id=self.get_project_id(), material=material).aggregate(
                m=Max('request_number')
            )['m']
            or 0
        )
        super().perform_create(
            serializer,
            request_number=max_num + 1,
            unit=unit or '—',
            request_date=serializer.validated_data.get('request_date') or timezone.localdate(),
        )

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != 'pending':
            return Response({'detail': 'Only pending requests can be edited'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='Approve material request', tags=['Procurement'])
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, project_pk=None, pk=None):
        obj = approve_material_request(self.get_object(), request.user)
        return Response(self.get_serializer(obj).data)

    @extend_schema(summary='Place purchase order', tags=['Procurement'])
    @action(detail=True, methods=['post'], url_path='place-order')
    def place_order(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        po = place_purchase_order(
            obj,
            request.user,
            supplier_id=request.data.get('supplier'),
            order_date=request.data.get('order_date') or timezone.localdate(),
            expected_delivery_date=request.data.get('expected_delivery_date'),
            unit_price=request.data.get('unit_price'),
            notes=request.data.get('notes', ''),
        )
        data = self.get_serializer(obj).data
        data['purchase_order'] = PurchaseOrderSerializer(po).data
        return Response(data)

    @extend_schema(summary='Mark purchase order delivered', tags=['Procurement'])
    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, project_pk=None, pk=None):
        obj = deliver_purchase_order(
            self.get_object(),
            request.user,
            actual_delivery_date=request.data.get('actual_delivery_date') or timezone.localdate(),
            document_ref=request.data.get('document_ref', ''),
        )
        return Response(self.get_serializer(obj).data)

    @extend_schema(summary='Cancel material request', tags=['Procurement'])
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, project_pk=None, pk=None):
        obj = cancel_material_request(self.get_object(), request.user)
        return Response(self.get_serializer(obj).data)


class InventoryTransactionViewSet(ProjectScopedViewSet):
    queryset = InventoryTransaction.objects.select_related('material', 'supplier')
    serializer_class = InventoryTransactionSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    AUTO_MSG = 'این تراکنش از گزارش روزانه ایجاد شده و قابل ویرایش مستقیم نیست'


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
        material = get_object_or_404(Material, pk=mid, project_id=project_pk)
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


class MaterialConsumptionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Material consumption vs planned', tags=['Materials'])
    def get(self, request, project_pk=None):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = material_consumption_report(
            project_pk,
            material_id=request.query_params.get('material_id'),
            activity_id=request.query_params.get('activity_id'),
            date_from=parse_jalali_or_gregorian(date_from) if date_from else None,
            date_to=parse_jalali_or_gregorian(date_to) if date_to else None,
        )
        return Response(data)


class InventoryRunningBalanceView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Running balance by date', tags=['Materials'])
    def get(self, request, project_pk=None):
        material_id = request.query_params.get('material_id')
        if not material_id:
            return Response({'detail': 'material_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Material, pk=material_id, project_id=project_pk)
        return Response(running_balance(material_id, project_id=project_pk))

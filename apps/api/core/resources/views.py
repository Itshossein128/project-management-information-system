"""Material balance and inventory API."""

from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from common.viewsets import ProjectScopedViewSet
from permissions.project import HasProjectPermission, IsProjectMember
from resources.models import InventoryTransaction, Material, MaterialRequest, PurchaseOrder
from resources.serializers import (
    InventoryTransactionSerializer,
    MaterialRequestDeliverSerializer,
    MaterialRequestPlaceOrderSerializer,
    MaterialRequestSerializer,
    MaterialSerializer,
    PurchaseOrderSerializer,
)
from resources.services.balance_service import compute_material_balance, material_balance_list, running_balance
from resources.services.consumption_service import material_consumption_report
from resources.services.procurement_service import (
    approve_material_request,
    cancel_material_request,
    compute_material_request_create_kwargs,
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


    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-request_date', '-request_number')

    def perform_create(self, serializer):
        kwargs = compute_material_request_create_kwargs(
            project_id=self.get_project_id(),
            material=serializer.validated_data['material'],
            provided_unit=serializer.validated_data.get('unit'),
            provided_date=serializer.validated_data.get('request_date'),
        )
        super().perform_create(serializer, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != 'pending':
            return Response({'detail': 'Only pending requests can be edited'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

class MaterialRequestApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_procurement'

    @extend_schema(summary='Approve material request', tags=['Procurement'], responses={200: MaterialRequestSerializer})
    def post(self, request, project_pk=None, pk=None):
        req = get_object_or_404(MaterialRequest, pk=pk, project_id=project_pk)
        obj = approve_material_request(req, request.user)
        return Response(MaterialRequestSerializer(obj).data)


class MaterialRequestPlaceOrderView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_procurement'

    @extend_schema(summary='Place purchase order', tags=['Procurement'], request=MaterialRequestPlaceOrderSerializer, responses={200: MaterialRequestSerializer})
    def post(self, request, project_pk=None, pk=None):
        req = get_object_or_404(MaterialRequest, pk=pk, project_id=project_pk)
        ser = MaterialRequestPlaceOrderSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        po = place_purchase_order(
            req,
            request.user,
            supplier_id=ser.validated_data['supplier'],
            order_date=ser.validated_data.get('order_date') or timezone.localdate(),
            expected_delivery_date=ser.validated_data.get('expected_delivery_date'),
            unit_price=ser.validated_data.get('unit_price'),
            notes=ser.validated_data.get('notes', ''),
        )
        data = MaterialRequestSerializer(req).data
        data['purchase_order'] = PurchaseOrderSerializer(po).data
        return Response(data)


class MaterialRequestDeliverView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_procurement'

    @extend_schema(summary='Mark purchase order delivered', tags=['Procurement'], request=MaterialRequestDeliverSerializer, responses={200: MaterialRequestSerializer})
    def post(self, request, project_pk=None, pk=None):
        req = get_object_or_404(MaterialRequest, pk=pk, project_id=project_pk)
        ser = MaterialRequestDeliverSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = deliver_purchase_order(
            req,
            request.user,
            actual_delivery_date=ser.validated_data.get('actual_delivery_date') or timezone.localdate(),
            document_ref=ser.validated_data.get('document_ref', ''),
        )
        return Response(MaterialRequestSerializer(obj).data)


class MaterialRequestCancelView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_procurement'

    @extend_schema(summary='Cancel material request', tags=['Procurement'], responses={200: MaterialRequestSerializer})
    def post(self, request, project_pk=None, pk=None):
        req = get_object_or_404(MaterialRequest, pk=pk, project_id=project_pk)
        obj = cancel_material_request(req, request.user)
        return Response(MaterialRequestSerializer(obj).data)


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

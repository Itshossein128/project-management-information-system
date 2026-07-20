"""Contract and IPC API views."""

import logging
from datetime import date, timedelta

from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.jalali import parse_jalali_or_gregorian
from contracts.models import ChangeOrder, ChangeOrderStatus, Contract, ContractItem, IPC, IPCDeduction, IPCItem, IPCStatus
from contracts.serializers import (
    ChangeOrderSerializer,
    ContractDetailSerializer,
    ContractItemSerializer,
    ContractListSerializer,
    ContractWriteSerializer,
    IPCCreateSerializer,
    IPCDeductionSerializer,
    IPCDetailSerializer,
    IPCItemSerializer,
    IPCListSerializer,
)
from contracts.services.contract_service import bulk_upsert_contract_items, approve_change_order, reject_change_order
from contracts.services.ipc_service import (
    apply_deductions,
    auto_populate_ipc,
    next_change_number,
    next_ipc_number,
    submit_ipc,
    approve_ipc,
    pay_ipc,
    reject_ipc,
    update_ipc_item,
    add_manual_deduction,
    update_manual_deduction,
    delete_manual_deduction,
    MANUAL_DEDUCTION_TYPES
)
from permissions.project import HasProjectPermission, IsProjectMember

logger = logging.getLogger(__name__)


class ContractScopedViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'pk'
    view_permission = 'view_contracts'
    edit_permission = 'edit_contracts'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def get_project_id(self):
        return self.kwargs['project_pk']

    def get_queryset(self):
        return Contract.objects.filter(project_id=self.get_project_id(), is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.updated_by = request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractViewSet(ContractScopedViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContractDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ContractWriteSerializer
        return ContractListSerializer

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        for param in ('contract_type', 'status', 'counterparty'):
            val = request.query_params.get(param)
            if val:
                qs = qs.filter(**{f'{param}__icontains' if param == 'counterparty' else param: val})

        ipc_agg = IPC.objects.filter(is_deleted=False).values('contract_id').annotate(
            total=Count('id'),
            paid=Count('id', filter=models.Q(status=IPCStatus.PAID)),
            billed=Sum('gross_amount', filter=models.Q(status__in=[IPCStatus.APPROVED, IPCStatus.PAID])),
            paid_amount=Sum('net_amount', filter=models.Q(status=IPCStatus.PAID)),
        )
        stats_map = {
            row['contract_id']: {
                'total': row['total'],
                'paid': row['paid'],
                'billed': float(row['billed'] or 0),
                'paid_amount': float(row['paid_amount'] or 0),
            }
            for row in ipc_agg
        }
        contracts = list(qs)
        for c in contracts:
            c._ipc_stats = stats_map.get(c.id)

        serializer = ContractListSerializer(contracts, many=True)
        return Response({'results': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(ContractDetailSerializer(instance).data)

    def create(self, request, *args, **kwargs):
        serializer = ContractWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contract = serializer.save(
            project_id=self.get_project_id(),
            created_by=request.user,
            updated_by=request.user,
        )
        if contract.adjusted_amount is None:
            contract.adjusted_amount = contract.original_amount
            contract.save(update_fields=['adjusted_amount'])
        return Response(ContractDetailSerializer(contract).data, status=201)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContractWriteSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(ContractDetailSerializer(instance).data)


class ContractItemsBulkView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Bulk upsert contract BoQ items', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None):
        contract = get_object_or_404(Contract, pk=pk, project_id=project_pk, is_deleted=False)
        rows = request.data if isinstance(request.data, list) else request.data.get('items', [])
        saved = bulk_upsert_contract_items(contract, rows, request.user)
        return Response(ContractItemSerializer(saved, many=True).data)


class ChangeOrderView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Create change order', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None):
        contract = get_object_or_404(Contract, pk=pk, project_id=project_pk, is_deleted=False)
        co = ChangeOrder.objects.create(
            contract=contract,
            change_number=next_change_number(contract.id),
            description=request.data.get('description', ''),
            amount_change=request.data.get('amount_change', 0),
            status=ChangeOrderStatus.DRAFT,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(ChangeOrderSerializer(co).data, status=201)


class ChangeOrderDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def patch(self, request, project_pk=None, pk=None, chid=None):
        co = get_object_or_404(
            ChangeOrder, pk=chid, contract_id=pk, contract__project_id=project_pk, is_deleted=False
        )
        serializer = ChangeOrderSerializer(co, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class ChangeOrderApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Approve change order', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None, chid=None):
        co = get_object_or_404(
            ChangeOrder, pk=chid, contract_id=pk, contract__project_id=project_pk, is_deleted=False
        )
        try:
            co = approve_change_order(co, request.user)
            return Response(ChangeOrderSerializer(co).data)
        except ValueError:
            logger.exception('Failed to reject change order')
            return Response(
                {'detail': 'Failed to reject change order.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangeOrderRejectView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Reject change order', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None, chid=None):
        co = get_object_or_404(
            ChangeOrder, pk=chid, contract_id=pk, contract__project_id=project_pk, is_deleted=False
        )
        co = reject_change_order(co, request.user)
        return Response(ChangeOrderSerializer(co).data)


class IPCViewSet(viewsets.ViewSet):
    view_permission = 'view_ipcs'
    edit_permission = 'edit_ipcs'
    approve_permission = 'approve_ipcs'

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        action = getattr(self, 'action', None)
        if action in ('approve', 'pay', 'reject'):
            return self.approve_permission
        if action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def list(self, request, project_pk=None):
        self.action = 'list'
        qs = IPC.objects.filter(project_id=project_pk, is_deleted=False).select_related('contract')
        if request.query_params.get('contract_id'):
            qs = qs.filter(contract_id=request.query_params['contract_id'])
        if request.query_params.get('status'):
            qs = qs.filter(status=request.query_params['status'])
        if request.query_params.get('overdue') == 'true':
            qs = qs.filter(
                status=IPCStatus.APPROVED,
                planned_payment_date__lt=date.today(),
                actual_payment_date__isnull=True,
            )
        return Response({'results': IPCListSerializer(qs.order_by('-ipc_number'), many=True).data})

    def retrieve(self, request, project_pk=None, pk=None):
        self.action = 'retrieve'
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        return Response(IPCDetailSerializer(ipc).data)

    def create(self, request, project_pk=None):
        self.action = 'create'
        ser = IPCCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        contract = get_object_or_404(
            Contract, pk=ser.validated_data['contract_id'], project_id=project_pk, is_deleted=False
        )
        ipc = IPC.objects.create(
            project_id=project_pk,
            contract=contract,
            ipc_number=next_ipc_number(contract.id),
            period_start=ser.validated_data.get('period_start'),
            period_end=ser.validated_data.get('period_end'),
            prepared_date=ser.validated_data.get('prepared_date') or date.today(),
            notes=ser.validated_data.get('notes', ''),
            created_by=request.user,
            updated_by=request.user,
        )
        try:
            from contracts.tasks import populate_ipc_async
            populate_ipc_async.delay(str(ipc.id))
        except Exception:
            auto_populate_ipc(ipc.id)
            apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data, status=201)

    def partial_update(self, request, project_pk=None, pk=None):
        self.action = 'partial_update'
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        if ipc.status != IPCStatus.DRAFT:
            return Response({'detail': 'Only draft IPCs can be edited.'}, status=400)
        ser = IPCDetailSerializer(ipc, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for field in ('period_start', 'period_end', 'prepared_date', 'notes'):
            if field in ser.validated_data:
                setattr(ipc, field, ser.validated_data[field])
        ipc.updated_by = request.user
        ipc.save()
        return Response(IPCDetailSerializer(ipc).data)


class IPCPopulateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    @extend_schema(summary='Auto-populate IPC items', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        auto_populate_ipc(ipc.id)
        apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data)


class IPCItemUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    def patch(self, request, project_pk=None, pk=None, itemid=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        item = get_object_or_404(IPCItem, pk=itemid, ipc=ipc, is_deleted=False)
        qty_current = request.data.get('qty_current', item.qty_current)
        ipc = update_ipc_item(ipc, item, qty_current, request.user)
        return Response(IPCDetailSerializer(ipc).data)


class IPCSubmitView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        try:
            ipc = submit_ipc(ipc, request.user)
            return Response(IPCDetailSerializer(ipc).data)
        except ValueError:
            logger.exception('Failed to submit IPC')
            return Response({'detail': 'Failed to submit IPC.'}, status=400)


class IPCDeductionListView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    @extend_schema(summary='Add manual IPC deduction', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        deduction_type = request.data.get('deduction_type', '')
        amount = request.data.get('amount')
        if amount is None:
            return Response({'detail': 'amount is required.'}, status=400)
        try:
            ipc = add_manual_deduction(
                ipc,
                deduction_type,
                amount,
                request.data.get('description', ''),
                request.user
            )
            return Response(IPCDetailSerializer(ipc).data, status=201)
        except ValueError:
            logger.exception('Failed to add deduction to IPC')
            return Response({'detail': 'Failed to add deduction.'}, status=400)


class IPCDeductionDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    def patch(self, request, project_pk=None, pk=None, did=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        deduction = get_object_or_404(
            IPCDeduction, pk=did, ipc=ipc, is_deleted=False, deduction_type__in=MANUAL_DEDUCTION_TYPES
        )
        try:
            ipc = update_manual_deduction(
                ipc,
                deduction,
                request.data.get('amount'),
                request.data.get('description'),
                request.user
            )
            return Response(IPCDetailSerializer(ipc).data)
        except ValueError:
            logger.exception('Failed to update deduction for IPC')
            return Response({'detail': 'Failed to update deduction.'}, status=400)

    def delete(self, request, project_pk=None, pk=None, did=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        deduction = get_object_or_404(
            IPCDeduction, pk=did, ipc=ipc, is_deleted=False, deduction_type__in=MANUAL_DEDUCTION_TYPES
        )
        try:
            ipc = delete_manual_deduction(ipc, deduction, request.user)
            return Response(IPCDetailSerializer(ipc).data)
        except ValueError:
            logger.exception('Failed to delete deduction for IPC')
            return Response({'detail': 'Failed to delete deduction.'}, status=400)


class IPCApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        ipc = approve_ipc(ipc, request.user)
        return Response(IPCDetailSerializer(ipc).data)


class IPCPayView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        from datetime import date
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        payment_date_raw = request.data.get('actual_payment_date')
        payment_date = parse_jalali_or_gregorian(payment_date_raw) if payment_date_raw else date.today()
        ipc = pay_ipc(ipc, request.user, payment_date)
        return Response(IPCDetailSerializer(ipc).data)


class IPCRejectView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        ipc = reject_ipc(ipc, request.user, request.data.get('reason', ''))
        return Response(IPCDetailSerializer(ipc).data)


class IPCPdfView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_ipcs'

    @extend_schema(summary='Export IPC as PDF', tags=['Contracts'])
    def get(self, request, project_pk=None, pk=None):
        from contracts.pdf import render_ipc_pdf
        from django.http import HttpResponse

        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        pdf_bytes = render_ipc_pdf(ipc)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f"attachment; filename=\"ipc-{ipc.ipc_number}.pdf\""
        return response

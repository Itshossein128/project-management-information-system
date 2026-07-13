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

from cash_flow.models import CashTransaction, CashTransactionType, InflowCategory, OutflowCategory
from common.jalali import parse_jalali_or_gregorian
from contracts.models import ChangeOrder, ChangeOrderStatus, Contract, ContractItem, ContractType, IPC, IPCDeduction, IPCItem, IPCStatus
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
from contracts.services.ipc_service import apply_deductions, auto_populate_ipc, next_change_number, next_ipc_number
from permissions.project import HasProjectPermission, IsProjectMember

logger = logging.getLogger(__name__)

MANUAL_DEDUCTION_TYPES = frozenset({'material_price_diff', 'other'})

FK_ITEM_FIELDS = {
    'activity': 'projects.Activity',
    'unit': 'master_data.Unit',
}


def _resolve_fk_fields(payload: dict) -> dict:
    """Convert UUID strings in FK fields to model instances for ORM create/update."""
    from decimal import Decimal
    from django.apps import apps

    resolved = dict(payload)
    for field in ('unit_price', 'quantity'):
        if field in resolved and resolved[field] is not None and resolved[field] != '':
            resolved[field] = Decimal(str(resolved[field]))
    for field, model_label in FK_ITEM_FIELDS.items():
        if field not in resolved:
            continue
        raw = resolved.pop(field)
        if raw in (None, ''):
            resolved[f'{field}_id'] = None
            continue
        model = apps.get_model(model_label)
        resolved[f'{field}_id'] = raw if hasattr(raw, 'pk') else raw
    return resolved


def _invalidate(project_id):
    try:
        from common.cache_utils import invalidate_project_caches
        invalidate_project_caches(project_id)
    except Exception:
        pass


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
        saved = []
        for row in rows:
            item_id = row.get('id')
            payload = _resolve_fk_fields({k: v for k, v in row.items() if k != 'id'})
            if item_id:
                item = get_object_or_404(ContractItem, pk=item_id, contract=contract)
                for k, v in payload.items():
                    setattr(item, k, v)
                item.updated_by = request.user
                item.save()
            else:
                item = ContractItem.objects.create(
                    contract=contract,
                    created_by=request.user,
                    updated_by=request.user,
                    **payload,
                )
            saved.append(item)
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


def _contract_adjusted_base(contract):
    return contract.adjusted_amount if contract.adjusted_amount is not None else (contract.original_amount or 0)


class ChangeOrderApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Approve change order', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None, chid=None):
        co = get_object_or_404(
            ChangeOrder, pk=chid, contract_id=pk, contract__project_id=project_pk, is_deleted=False
        )
        if co.status == ChangeOrderStatus.APPROVED:
            return Response(ChangeOrderSerializer(co).data)
        contract = co.contract
        new_adjusted = _contract_adjusted_base(contract) + co.amount_change
        if new_adjusted < 0:
            return Response(
                {'detail': 'مبلغ تعدیل‌شده قرارداد نمی‌تواند منفی باشد'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        co.status = ChangeOrderStatus.APPROVED
        co.approved_date = date.today()
        co.updated_by = request.user
        co.save()
        contract.adjusted_amount = new_adjusted
        contract.updated_by = request.user
        contract.save(update_fields=['adjusted_amount', 'updated_by', 'updated_at'])
        return Response(ChangeOrderSerializer(co).data)


class ChangeOrderRejectView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    @extend_schema(summary='Reject change order', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None, chid=None):
        co = get_object_or_404(
            ChangeOrder, pk=chid, contract_id=pk, contract__project_id=project_pk, is_deleted=False
        )
        was_approved = co.status == ChangeOrderStatus.APPROVED
        co.status = ChangeOrderStatus.REJECTED
        co.approved_date = None
        co.updated_by = request.user
        co.save()
        if was_approved:
            contract = co.contract
            contract.adjusted_amount = _contract_adjusted_base(contract) - co.amount_change
            if contract.adjusted_amount < 0:
                contract.adjusted_amount = 0
            contract.updated_by = request.user
            contract.save(update_fields=['adjusted_amount', 'updated_by', 'updated_at'])
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
        from decimal import Decimal

        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        item = get_object_or_404(IPCItem, pk=itemid, ipc=ipc, is_deleted=False)
        qty_current = request.data.get('qty_current', item.qty_current)
        qty_current = Decimal(str(qty_current))
        item.qty_current = qty_current
        item.qty_cumulative = Decimal(str(item.qty_previous or 0)) + qty_current
        unit_price = Decimal(str(item.unit_price or 0))
        item.amount_current = unit_price * qty_current
        item.amount_cumulative = unit_price * item.qty_cumulative
        item.updated_by = request.user
        item.save()
        gross = IPCItem.objects.filter(ipc=ipc, is_deleted=False).aggregate(
            total=Sum('amount_current')
        )['total'] or 0
        ipc.gross_amount = gross
        ipc.save(update_fields=['gross_amount', 'updated_at'])
        apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data)


def _publish_ipc_submitted(ipc):
    try:
        from events.publisher import EventPublisher

        EventPublisher().publish(
            'ipc.submitted',
            {
                'ipc_id': str(ipc.id),
                'ipc_number': ipc.ipc_number,
                'contract_id': str(ipc.contract_id),
                'gross_amount': str(ipc.gross_amount or 0),
            },
            project_id=str(ipc.project_id),
        )
    except Exception:  # noqa: BLE001 - event bus optional in dev/tests
        logger.warning('Could not publish ipc.submitted for %s', ipc.id, exc_info=True)


class IPCSubmitView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        if ipc.status != IPCStatus.DRAFT:
            return Response({'detail': 'Only draft IPCs can be submitted.'}, status=400)
        ipc.status = IPCStatus.SUBMITTED
        ipc.submitted_date = date.today()
        ipc.rejection_reason = ''
        ipc.updated_by = request.user
        ipc.save()
        _publish_ipc_submitted(ipc)
        return Response(IPCDetailSerializer(ipc).data)


class IPCDeductionListView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    @extend_schema(summary='Add manual IPC deduction', tags=['Contracts'])
    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        if ipc.status != IPCStatus.DRAFT:
            return Response({'detail': 'Deductions can only be edited on draft IPCs.'}, status=400)
        deduction_type = request.data.get('deduction_type', '')
        if deduction_type not in MANUAL_DEDUCTION_TYPES:
            return Response(
                {'detail': 'Only material_price_diff and other deductions can be added manually.'},
                status=400,
            )
        amount = request.data.get('amount')
        if amount is None:
            return Response({'detail': 'amount is required.'}, status=400)
        deduction = IPCDeduction.objects.create(
            ipc=ipc,
            deduction_type=deduction_type,
            amount=amount,
            description=request.data.get('description', ''),
            created_by=request.user,
            updated_by=request.user,
        )
        apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data, status=201)


class IPCDeductionDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_ipcs'

    def patch(self, request, project_pk=None, pk=None, did=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        if ipc.status != IPCStatus.DRAFT:
            return Response({'detail': 'Deductions can only be edited on draft IPCs.'}, status=400)
        deduction = get_object_or_404(
            IPCDeduction, pk=did, ipc=ipc, is_deleted=False, deduction_type__in=MANUAL_DEDUCTION_TYPES
        )
        if 'amount' in request.data:
            deduction.amount = request.data['amount']
        if 'description' in request.data:
            deduction.description = request.data['description']
        deduction.updated_by = request.user
        deduction.save()
        apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data)

    def delete(self, request, project_pk=None, pk=None, did=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        if ipc.status != IPCStatus.DRAFT:
            return Response({'detail': 'Deductions can only be edited on draft IPCs.'}, status=400)
        deduction = get_object_or_404(
            IPCDeduction, pk=did, ipc=ipc, is_deleted=False, deduction_type__in=MANUAL_DEDUCTION_TYPES
        )
        deduction.is_deleted = True
        deduction.deleted_at = timezone.now()
        deduction.updated_by = request.user
        deduction.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        apply_deductions(ipc.id)
        ipc.refresh_from_db()
        return Response(IPCDetailSerializer(ipc).data)


class IPCApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        ipc.status = IPCStatus.APPROVED
        ipc.approval_date = date.today()
        if not ipc.planned_payment_date:
            ipc.planned_payment_date = date.today() + timedelta(days=30)
        ipc.updated_by = request.user
        ipc.save()
        return Response(IPCDetailSerializer(ipc).data)


def _ipc_cash_transaction_defaults(ipc, user, payment_date):
    contract = ipc.contract
    if contract.contract_type == ContractType.MAIN:
        tx_type = CashTransactionType.IN
        category = InflowCategory.IPC_RECEIPT
    elif contract.contract_type == ContractType.SUBCONTRACT:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.SUBCONTRACTOR_PAYMENT
    elif contract.contract_type == ContractType.PURCHASE:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.SUPPLIER_PAYMENT
    elif contract.contract_type == ContractType.EQUIPMENT_RENTAL:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.EQUIPMENT_RENTAL
    else:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.OTHER_EXPENSE

    return {
        'project_id': ipc.project_id,
        'tx_date': payment_date,
        'tx_type': tx_type,
        'category': category,
        'amount': ipc.net_amount or ipc.gross_amount,
        'description': (
            f'صدور موقت شماره {ipc.ipc_number} — '
            f'قرارداد {contract.contract_number or contract.counterparty}'
        ),
        'contract': contract,
        'counterparty': contract.counterparty,
        'is_forecast': False,
        'actual_date': payment_date,
        'updated_by': user,
        'is_deleted': False,
        'deleted_at': None,
    }


def _upsert_ipc_cash_transaction(ipc, user, payment_date=None):
    payment_date = payment_date or date.today()
    defaults = _ipc_cash_transaction_defaults(ipc, user, payment_date)
    existing = CashTransaction.objects.filter(ipc=ipc, is_deleted=False).first()
    if existing:
        for field, value in defaults.items():
            setattr(existing, field, value)
        existing.save()
    else:
        CashTransaction.objects.create(
            ipc=ipc,
            created_by=user,
            **defaults,
        )
    _invalidate(ipc.project_id)


class IPCPayView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        payment_date_raw = request.data.get('actual_payment_date')
        payment_date = parse_jalali_or_gregorian(payment_date_raw) if payment_date_raw else date.today()
        ipc.status = IPCStatus.PAID
        ipc.actual_payment_date = payment_date
        ipc.updated_by = request.user
        ipc.save()
        _upsert_ipc_cash_transaction(ipc, request.user, payment_date)
        return Response(IPCDetailSerializer(ipc).data)


class IPCRejectView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'approve_ipcs'

    def post(self, request, project_pk=None, pk=None):
        ipc = get_object_or_404(IPC, pk=pk, project_id=project_pk, is_deleted=False)
        ipc.status = IPCStatus.DRAFT
        ipc.rejection_reason = request.data.get('reason', '')
        ipc.updated_by = request.user
        ipc.save()
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
        response['Content-Disposition'] = f'attachment; filename="ipc-{ipc.ipc_number}.pdf"'
        return response

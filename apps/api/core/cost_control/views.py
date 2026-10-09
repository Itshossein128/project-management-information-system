"""Cost control API views."""

from datetime import date

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.jalali import parse_jalali_or_gregorian
from common.serializers import JalaliDateField
from common.viewsets import ProjectScopedViewSet
from cost_control.models import ActualCost, Budget, CostPool
from cost_control.serializers import (
    ActualCostSerializer,
    BudgetBulkItemSerializer,
    BudgetSerializer,
    CostPoolAllocationItemSerializer,
    CostPoolSerializer,
    SupplierSerializer,
)
from cost_control.services.budget_service import (
    assert_line_mutable,
    bulk_upsert_budgets,
    budget_summary,
    check_wbs_overrun,
)
from cost_control.services.budget_version_service import ensure_working_draft
from cost_control.services.cost_pool_service import (
    AllocationExceededError,
    allocate_cost_pool,
    auto_allocate_cost_pool,
)
from cost_control.services.cost_summary_service import cost_summary
from cost_control.services.variance_service import get_budget_vs_actual
from permissions.project import HasProjectPermission, IsProjectMember
from resources.models import Supplier


def _invalidate_cost_caches(project_id):
    try:
        from common.cache_utils import invalidate_project_caches

        invalidate_project_caches(project_id)
    except Exception:
        pass


class CostScopedViewSet(ProjectScopedViewSet):
    view_permission = 'view_costs'
    edit_permission = 'edit_costs'

    def post_save(self, instance):
        _invalidate_cost_caches(self.kwargs['project_pk'])

    def post_delete(self, instance):
        _invalidate_cost_caches(self.kwargs['project_pk'])


class BudgetViewSet(CostScopedViewSet):
    queryset = Budget.objects.select_related('wbs', 'activity', 'version')
    serializer_class = BudgetSerializer

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        version_id = request.query_params.get('version_id')
        if version_id:
            qs = qs.filter(version_id=version_id)
        else:
            from cost_control.services.budget_version_service import get_control_version

            control = get_control_version(self.get_project_id())
            if control:
                qs = qs.filter(version_id=control.id)
        for param, field in (
            ('wbs_id', 'wbs_id'),
            ('activity_id', 'activity_id'),
            ('cost_category', 'cost_category'),
        ):
            val = request.query_params.get(param)
            if val:
                qs = qs.filter(**{field: val})
        serializer = self.get_serializer(qs, many=True)
        summary = budget_summary(self.get_project_id(), version_id=version_id)
        warning = check_wbs_overrun(self.get_project_id(), version_id=version_id)
        payload = {'results': serializer.data, 'summary': summary}
        if warning:
            payload['warning'] = warning
        return Response(payload)

    def perform_create(self, serializer, **kwargs):
        version_id = self.request.data.get('version') or self.request.data.get('version_id')
        if version_id:
            from cost_control.models import BudgetVersion

            version = BudgetVersion.objects.get(
                pk=version_id, project_id=self.get_project_id(), is_deleted=False
            )
            from cost_control.services.budget_version_service import assert_version_editable

            assert_version_editable(version)
        else:
            version = ensure_working_draft(self.get_project_id(), self.request.user)
        serializer.save(
            project_id=self.get_project_id(),
            version=version,
            created_by=self.request.user,
            updated_by=self.request.user,
            **kwargs,
        )
        self.post_save(serializer.instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        warning = check_wbs_overrun(self.get_project_id())
        data = serializer.data
        if warning:
            return Response({**data, 'warning': warning}, status=status.HTTP_201_CREATED)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        assert_line_mutable(serializer.instance)
        serializer.save(updated_by=self.request.user)
        self.post_save(serializer.instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        assert_line_mutable(instance)
        instance.soft_delete(user=request.user)
        self.post_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BudgetBulkView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Bulk upsert budgets', tags=['Cost control'])
    def post(self, request, project_pk=None):
        payload = request.data
        version_id = None
        if isinstance(payload, dict) and not isinstance(payload, list):
            version_id = payload.get('version_id') or payload.get('version')
            items_data = payload.get('items') or payload.get('lines') or []
        else:
            items_data = payload
        items = BudgetBulkItemSerializer(data=items_data, many=True)
        items.is_valid(raise_exception=True)
        entries = [
            {
                'wbs_id': row.get('wbs'),
                'activity_id': row.get('activity'),
                'cbs_id': row.get('cbs'),
                'contract_id': row.get('contract'),
                'level': row.get('level'),
                'cost_category': row['cost_category'],
                'budget_amount': row['budget_amount'],
                'notes': row.get('notes', ''),
                'period_start': row.get('period_start'),
                'period_end': row.get('period_end'),
            }
            for row in items.validated_data
        ]
        saved, warning = bulk_upsert_budgets(
            project_pk, entries, request.user, version_id=version_id
        )
        _invalidate_cost_caches(project_pk)
        vid = saved[0].version_id if saved else version_id
        return Response(
            {
                'saved': len(saved),
                'version_id': str(vid) if vid else None,
                'summary': budget_summary(project_pk, version_id=vid),
                **({'warning': warning} if warning else {}),
            }
        )


class ActualCostViewSet(CostScopedViewSet):
    queryset = ActualCost.objects.select_related('wbs', 'activity', 'supplier', 'daily_report')
    serializer_class = ActualCostSerializer

    AUTO_COST_MSG = 'این هزینه به صورت خودکار از گزارش روزانه ایجاد شده و قابل ویرایش مستقیم نیست'

    def perform_create(self, serializer, **kwargs):
        from projects.fiscal_service import (
            assert_fiscal_writable,
            duplicate_document_warnings,
            require_warning_ack,
        )
        from projects.models import Project

        project = Project.objects.get(pk=self.get_project_id())
        cost_date = serializer.validated_data.get('cost_date')
        assert_fiscal_writable(
            project,
            cost_date,
            corrective=bool(self.request.data.get('corrective')),
            correction_reason=self.request.data.get('correction_reason', ''),
        )
        warnings = duplicate_document_warnings(
            ActualCost,
            project,
            'invoice_number',
            serializer.validated_data.get('invoice_number', ''),
        )
        require_warning_ack(warnings, bool(self.request.data.get('acknowledge_warnings')))
        super().perform_create(serializer, **kwargs)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        for param in ('activity_id', 'wbs_id', 'cost_category', 'cost_type', 'supplier_id'):
            val = request.query_params.get(param)
            if val:
                qs = qs.filter(**{param: val})
        if request.query_params.get('date_from'):
            qs = qs.filter(cost_date__gte=parse_jalali_or_gregorian(request.query_params['date_from']))
        if request.query_params.get('date_to'):
            qs = qs.filter(cost_date__lte=parse_jalali_or_gregorian(request.query_params['date_to']))

        page = self.paginate_queryset(qs.order_by('-cost_date'))
        serializer = self.get_serializer(page, many=True)
        total_actual = float(qs.aggregate(total=models.Sum('amount'))['total'] or 0)
        by_category = {}
        for row in qs.values('cost_category').annotate(total=models.Sum('amount')):
            by_category[row['cost_category'] or 'other'] = float(row['total'] or 0)
        meta = {'total_actual': total_actual, 'by_category': by_category}
        if page is not None:
            response = self.get_paginated_response(serializer.data)
            response.data['meta'] = meta
            return response
        return Response({'results': serializer.data, 'meta': meta})

    def update(self, request, *args, **kwargs):
        if self.get_object().daily_report_id:
            return Response({'detail': self.AUTO_COST_MSG}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().daily_report_id:
            return Response({'detail': self.AUTO_COST_MSG}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class VarianceView(APIView):
    # Queries: before optimization=8, after=2 (aggregated in variance_service + cache)
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Budget vs actual variance', tags=['Cost control'])
    def get(self, request, project_pk=None):
        from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint

        group_by = request.query_params.get('group_by', 'wbs')
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else date.today()
        fp = params_fingerprint({'group_by': group_by, 'as_of': as_of.isoformat()})
        key = cache_key('variance', project_pk, fp)
        if request.query_params.get('force_refresh', '').lower() in ('1', 'true', 'yes'):
            from django.core.cache import cache

            cache.delete(key)
        data = get_cached_or_compute(
            key,
            1800,
            lambda: get_budget_vs_actual(project_pk, group_by=group_by, as_of_date=as_of),
        )
        return Response({'group_by': group_by, 'as_of': JalaliDateField().to_representation(as_of), 'results': data})


class CostSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Cost summary for EVM', tags=['Cost control'])
    def get(self, request, project_pk=None):
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else date.today()
        return Response(cost_summary(project_pk, as_of_date=as_of))


class CostPoolViewSet(CostScopedViewSet):
    queryset = CostPool.objects.all()
    serializer_class = CostPoolSerializer


class CostPoolAllocateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Allocate cost pool to activities', tags=['Cost control'])
    def post(self, request, project_pk=None, pk=None):
        pool = get_object_or_404(CostPool, pk=pk, project_id=project_pk, is_deleted=False)
        items = CostPoolAllocationItemSerializer(data=request.data, many=True)
        items.is_valid(raise_exception=True)
        try:
            pool = allocate_cost_pool(pool, items.validated_data, request.user)
        except AllocationExceededError as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        return Response(CostPoolSerializer(pool).data)


class CostPoolAutoAllocateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Auto-allocate cost pool by method', tags=['Cost control'])
    def post(self, request, project_pk=None, pk=None):
        pool = get_object_or_404(CostPool, pk=pk, project_id=project_pk, is_deleted=False)
        method = request.data.get('method', 'by_budget_weight')
        activity_ids = request.data.get('activity_ids')
        try:
            pool, allocations = auto_allocate_cost_pool(pool, method, request.user, activity_ids=activity_ids)
        except ValueError as exc:
            raise ValidationError({'method': str(exc)}) from exc
        except AllocationExceededError as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        _invalidate_cost_caches(project_pk)
        return Response({'pool': CostPoolSerializer(pool).data, 'allocations': allocations})


class SupplierViewSet(CostScopedViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    view_permission = 'view_suppliers'
    edit_permission = 'edit_suppliers'


class GlobalSupplierListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Global supplier list', tags=['Cost control'])
    def get(self, request):
        qs = Supplier.objects.filter(project__isnull=True, is_deleted=False)
        q = request.query_params.get('q')
        if q:
            qs = qs.filter(supplier_name__icontains=q)
        return Response(SupplierSerializer(qs[:50], many=True).data)

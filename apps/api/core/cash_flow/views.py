"""Cash flow API views."""

from datetime import date

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from cash_flow.models import CashFlowForecast, CashTransaction
from cash_flow.serializers import CashFlowForecastSerializer, CashTransactionSerializer
from cash_flow.services.cashflow_service import (
    get_cash_flow_summary,
    get_forecast_with_actuals,
    get_gap_analysis,
    get_receivables_payables,
    get_transaction_summary,
)
from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint
from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember
from common.viewsets import ProjectScopedViewSet


def _invalidate_cashflow_caches(project_id):
    try:
        from common.cache_utils import invalidate_project_caches

        invalidate_project_caches(project_id)
    except Exception:
        pass


class CashFlowPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class CashFlowScopedViewSet(ProjectScopedViewSet):
    view_permission = 'view_cashflow'
    edit_permission = 'edit_cashflow'
    pagination_class = CashFlowPagination

    def perform_create(self, serializer):
        super().perform_create(serializer)
        _invalidate_cashflow_caches(self.get_project_id())

    def perform_update(self, serializer):
        super().perform_update(serializer)
        _invalidate_cashflow_caches(self.get_project_id())

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        _invalidate_cashflow_caches(self.get_project_id())
        return response


class CashFlowListView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'
    pagination_class = CashFlowPagination

    @extend_schema(summary='List cash flow transactions with summary', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        qs = CashTransaction.objects.filter(project_id=project_pk, is_deleted=False)
        if request.query_params.get('date_from'):
            qs = qs.filter(tx_date__gte=parse_jalali_or_gregorian(request.query_params['date_from']))
        if request.query_params.get('date_to'):
            qs = qs.filter(tx_date__lte=parse_jalali_or_gregorian(request.query_params['date_to']))
        if request.query_params.get('tx_type'):
            qs = qs.filter(tx_type=request.query_params['tx_type'])
        if request.query_params.get('category'):
            qs = qs.filter(category=request.query_params['category'])
        if request.query_params.get('is_forecast') is not None:
            val = request.query_params['is_forecast'].lower()
            qs = qs.filter(is_forecast=val in ('1', 'true', 'yes'))
        if request.query_params.get('counterparty'):
            qs = qs.filter(counterparty__icontains=request.query_params['counterparty'])

        summary_qs = qs
        summary = get_transaction_summary(summary_qs)

        paginator = CashFlowPagination()
        page = paginator.paginate_queryset(qs.order_by('-tx_date', '-created_at'), request)
        serializer = CashTransactionSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        response.data['summary'] = summary
        return response


class CashTransactionViewSet(CashFlowScopedViewSet):
    queryset = CashTransaction.objects.all()
    serializer_class = CashTransactionSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


class CashFlowMonthlyView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Monthly cash flow summary', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        date_from = None
        date_to = None
        if request.query_params.get('date_from'):
            date_from = parse_jalali_or_gregorian(request.query_params['date_from'])
        if request.query_params.get('date_to'):
            date_to = parse_jalali_or_gregorian(request.query_params['date_to'])

        fp = params_fingerprint({
            'from': date_from.isoformat() if date_from else '',
            'to': date_to.isoformat() if date_to else '',
        })
        key = cache_key('cashflow_monthly', project_pk, fp)
        data = get_cached_or_compute(
            key,
            1800,
            lambda: get_cash_flow_summary(project_pk, date_from, date_to),
        )
        return Response({'results': data})


class CashFlowForecastListView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Forecast vs actual comparison', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        return Response({'results': get_forecast_with_actuals(project_pk)})


class CashFlowForecastUpsertView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_cashflow'

    @extend_schema(summary='Upsert monthly forecast', tags=['Cash flow'])
    def put(self, request, project_pk=None, month=None):
        try:
            parts = month.split('-')
            month_date = date(int(parts[0]), int(parts[1]), 1)
        except (ValueError, IndexError):
            return Response({'detail': 'Invalid month format. Use YYYY-MM.'}, status=400)

        forecast, _ = CashFlowForecast.objects.get_or_create(
            project_id=project_pk,
            month=month_date,
            defaults={'created_by': request.user, 'updated_by': request.user},
        )
        serializer = CashFlowForecastSerializer(forecast, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        if not forecast.created_by_id:
            forecast.created_by = request.user
            forecast.save(update_fields=['created_by'])
        _invalidate_cashflow_caches(project_pk)
        return Response(serializer.data)


class GapAnalysisView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Cash gap analysis', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        return Response({'results': get_gap_analysis(project_pk)})


class ReceivablesView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Receivables and payables summary', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        return Response(get_receivables_payables(project_pk))

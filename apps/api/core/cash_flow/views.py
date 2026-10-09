"""Cash flow API views."""

from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from cash_flow.models import (
    AllocationSimulation,
    CashFlowForecast,
    CashTransaction,
    LiquidityAllocationCycle,
)
from cash_flow.serializers import (
    CashFlowForecastSerializer,
    CashTransactionSerializer,
    LiquidityCycleSerializer,
    PriorityScoreSerializer,
)
from cash_flow.services.allocation_service import (
    compare_simulation,
    create_cycle,
    create_decision,
    decision_to_dict,
    generate_proposal,
    get_priority_score,
    save_simulation,
    score_to_dict,
    upsert_priority_score,
)
from cash_flow.services.cashflow_service import (
    get_cash_flow_summary,
    get_forecast_with_actuals,
    get_gap_analysis,
    get_receivables_payables,
    get_transaction_summary,
)
from cash_flow.services.net_need_service import suggested_net_need
from cash_flow.services.portfolio_report_service import build_portfolio_report
from cash_flow.services.projection_service import build_projected_series
from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint
from common.jalali import parse_jalali_or_gregorian
from common.viewsets import ProjectScopedViewSet
from config.exceptions import CodedValidationError
from permissions.project import HasProjectPermission, IsProjectMember


# Helper function to invalidate cache entries related to cash flow calculations when a transaction or forecast changes.
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

    def post_save(self, instance):
        _invalidate_cashflow_caches(self.kwargs['project_pk'])

    def post_delete(self, instance):
        _invalidate_cashflow_caches(self.kwargs['project_pk'])


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


class ProjectionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Domain-fed projected cash series', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        from_m = request.query_params.get('from') or date.today().strftime('%Y-%m')
        to_m = request.query_params.get('to') or from_m
        return Response(build_projected_series(project_pk, from_m, to_m))


class SuggestedNeedView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_cashflow'

    @extend_schema(summary='Suggested net cash need (FR-CASH-004)', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        from_m = request.query_params.get('from') or date.today().strftime('%Y-%m')
        to_m = request.query_params.get('to') or from_m
        return Response(suggested_net_need(project_pk, from_m, to_m))


class PriorityScoreView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_permissions(self):
        if self.request.method == 'PUT':
            self.required_permission = 'edit_cashflow'
        else:
            self.required_permission = 'view_cashflow'
        return super().get_permissions()

    @extend_schema(summary='Get project priority score', tags=['Cash flow'])
    def get(self, request, project_pk=None):
        score = get_priority_score(project_pk)
        if score is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(score_to_dict(score))

    @extend_schema(summary='Upsert project priority score', tags=['Cash flow'])
    def put(self, request, project_pk=None):
        ser = PriorityScoreSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            score = upsert_priority_score(project_pk, ser.validated_data, request.user)
        except CodedValidationError as exc:
            return Response({'detail': str(exc.detail), 'code': exc.default_code}, status=400)
        return Response(score_to_dict(score))


class PortfolioCycleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List liquidity allocation cycles', tags=['Cash flow portfolio'])
    def get(self, request):
        qs = LiquidityAllocationCycle.objects.filter(is_deleted=False).order_by('-created_at')
        return Response({'results': LiquidityCycleSerializer(qs, many=True).data})

    @extend_schema(summary='Create liquidity allocation cycle', tags=['Cash flow portfolio'])
    def post(self, request):
        ser = LiquidityCycleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cycle = create_cycle(request.user, ser.validated_data)
        return Response(LiquidityCycleSerializer(cycle).data, status=status.HTTP_201_CREATED)


class PortfolioProposeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Generate allocation proposal', tags=['Cash flow portfolio'])
    def post(self, request, cycle_id=None):
        cycle = get_object_or_404(LiquidityAllocationCycle, pk=cycle_id, is_deleted=False)
        return Response(generate_proposal(cycle, request.user))


class PortfolioDecisionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Record allocation decision', tags=['Cash flow portfolio'])
    def post(self, request, cycle_id=None):
        cycle = get_object_or_404(LiquidityAllocationCycle, pk=cycle_id, is_deleted=False)
        try:
            decision = create_decision(cycle, request.user, request.data)
        except CodedValidationError as exc:
            return Response(
                {'detail': exc.detail, 'code': exc.default_code},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(decision_to_dict(decision), status=status.HTTP_201_CREATED)


class PortfolioSimulationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Save allocation simulation', tags=['Cash flow portfolio'])
    def post(self, request, cycle_id=None):
        cycle = get_object_or_404(LiquidityAllocationCycle, pk=cycle_id, is_deleted=False)
        name = request.data.get('name') or 'simulation'
        lines = request.data.get('lines') or []
        sim = save_simulation(cycle, request.user, name, lines)
        return Response(
            {'id': str(sim.id), 'name': sim.name, 'payload': sim.payload},
            status=status.HTTP_201_CREATED,
        )


class PortfolioSimulationCompareView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Compare simulation to latest proposal', tags=['Cash flow portfolio'])
    def get(self, request, cycle_id=None, sim_id=None):
        sim = get_object_or_404(
            AllocationSimulation,
            pk=sim_id,
            cycle_id=cycle_id,
            is_deleted=False,
        )
        return Response(compare_simulation(sim))


class PortfolioReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Portfolio cash / need / allocation report', tags=['Cash flow portfolio'])
    def get(self, request):
        from_m = request.query_params.get('from') or date.today().strftime('%Y-%m')
        to_m = request.query_params.get('to') or from_m
        cycle_id = request.query_params.get('cycle_id')
        return Response(
            build_portfolio_report(request.user, from_m, to_m, cycle_id=cycle_id)
        )

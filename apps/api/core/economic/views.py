from datetime import date

from celery.result import AsyncResult
from django.db import models
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from economic.models import CostCategoryInflationMapping, EconomicSnapshot, InflationIndex, SimulationResult
from economic.serializers import (
    CostCategoryInflationMappingSerializer,
    EconomicSnapshotSerializer,
    SimulationResultSerializer,
)
from economic.services.cash_flow_real_service import compute_cash_flow_real
from economic.services.financing_service import compute_financing_cost
from economic.services.forecast_service import compute_economic_forecast
from economic.services.inflation_service import inflation_detail_by_category
from economic.services.snapshot_service import generate_snapshot
from economic.services.working_capital_service import compute_working_capital_curve
from economic.tasks import run_monte_carlo_task
from permissions.project import HasProjectPermission, IsProjectMember


class EconomicSnapshotView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Latest economic snapshot', tags=['Economic'])
    def get(self, request, project_pk=None):
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else date.today()
        snapshot = EconomicSnapshot.objects.filter(project_id=project_pk, snapshot_date=as_of).first()
        if not snapshot:
            snapshot = generate_snapshot(project_pk, as_of)
        inflation_detail = inflation_detail_by_category(project_pk, as_of)
        return Response({
            **EconomicSnapshotSerializer(snapshot).data,
            'inflation_detail': inflation_detail,
        })


class EconomicHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def get(self, request, project_pk=None):
        qs = EconomicSnapshot.objects.filter(project_id=project_pk).order_by('snapshot_date')
        return Response({'results': EconomicSnapshotSerializer(qs, many=True).data})


class FinancingCostView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def get(self, request, project_pk=None):
        return Response(compute_financing_cost(project_pk))


class InflationIndicesView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def get(self, request, project_pk=None):
        names = InflationIndex.objects.values_list('index_name', flat=True).distinct()
        results = []
        for name in names:
            latest = InflationIndex.objects.filter(index_name=name).order_by('-index_date').first()
            if latest:
                results.append({
                    'index_name': name,
                    'index_date': latest.index_date.isoformat(),
                    'index_value': float(latest.index_value),
                    'source': latest.source,
                })
        return Response({'results': results})


class EconomicForecastView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Inflation-adjusted EAC forecast', tags=['Economic'])
    def get(self, request, project_pk=None):
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else date.today()
        return Response(compute_economic_forecast(project_pk, as_of))


class WorkingCapitalView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Working capital forecast curve', tags=['Economic'])
    def get(self, request, project_pk=None):
        return Response(compute_working_capital_curve(project_pk))


class CashFlowRealView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Inflation-adjusted cash flow curve', tags=['Economic'])
    def get(self, request, project_pk=None):
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else date.today()
        return Response(compute_cash_flow_real(project_pk, as_of))


class SensitivityView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Latest Monte Carlo sensitivity tornado', tags=['Economic'])
    def get(self, request, project_pk=None):
        sim = SimulationResult.objects.filter(project_id=project_pk).order_by('-run_at').first()
        sensitivity = sim.sensitivity_json if sim else []
        if isinstance(sensitivity, dict):
            sensitivity = sensitivity.get('items', [])
        return Response({'sensitivity': sensitivity})


class InflationMappingListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.request.method == 'GET':
            return 'view_dashboard'
        return 'edit_cashflow'

    @extend_schema(summary='List inflation mappings (global + project)', tags=['Economic'])
    def get(self, request, project_pk=None):
        qs = CostCategoryInflationMapping.objects.filter(
            models.Q(project_id=project_pk) | models.Q(project__isnull=True)
        ).order_by('cost_category', 'index_name')
        return Response({'results': CostCategoryInflationMappingSerializer(qs, many=True).data})

    @extend_schema(summary='Create project inflation mapping', tags=['Economic'])
    def post(self, request, project_pk=None):
        ser = CostCategoryInflationMappingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        mapping = CostCategoryInflationMapping.objects.create(
            project_id=project_pk,
            **ser.validated_data,
        )
        return Response(
            CostCategoryInflationMappingSerializer(mapping).data,
            status=status.HTTP_201_CREATED,
        )


class InflationMappingDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_cashflow'

    @extend_schema(summary='Delete project inflation mapping', tags=['Economic'])
    def delete(self, request, project_pk=None, mapping_id=None):
        deleted, _ = CostCategoryInflationMapping.objects.filter(
            id=mapping_id,
            project_id=project_pk,
        ).delete()
        if not deleted:
            return Response({'detail': 'Not found or global mapping'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SimulateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def post(self, request, project_pk=None):
        iterations = int(request.data.get('iterations', 5000))
        scenario_params = request.data.get('scenario_params') or {}
        task = run_monte_carlo_task.delay(str(project_pk), iterations, scenario_params)
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)


class SimulateStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def get(self, request, project_pk=None, task_id=None):
        result = AsyncResult(task_id)
        if result.ready():
            return Response({'status': 'done', 'result': result.result})
        return Response({'status': result.status})


class LatestSimulationView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def get(self, request, project_pk=None):
        sim = SimulationResult.objects.filter(project_id=project_pk).order_by('-run_at').first()
        if not sim:
            return Response({'result': None})
        return Response({'result': SimulationResultSerializer(sim).data})


class InflationIndexUpsertView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = 'edit_project'

    def put(self, request, name=None, index_date=None):
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({'detail': 'Admin only'}, status=403)
        parsed_date = parse_jalali_or_gregorian(index_date)
        obj, _ = InflationIndex.objects.update_or_create(
            index_name=name,
            index_date=parsed_date,
            defaults={
                'index_value': request.data.get('index_value', 100),
                'source': request.data.get('source', ''),
            },
        )
        return Response({'index_name': obj.index_name, 'index_date': obj.index_date.isoformat(), 'index_value': float(obj.index_value)})

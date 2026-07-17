from datetime import date

from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from economic.models import EconomicSnapshot, InflationIndex, SimulationResult
from economic.serializers import EconomicSnapshotSerializer, SimulationResultSerializer
from economic.services.financing_service import compute_financing_cost
from economic.services.inflation_service import inflation_detail_by_category
from economic.services.snapshot_service import generate_snapshot
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


class SimulateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    def post(self, request, project_pk=None):
        from economic.tasks import run_monte_carlo_task

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

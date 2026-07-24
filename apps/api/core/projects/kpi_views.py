"""Unified project KPI / health dashboard views (blueprint K-02)."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember
from projects.kpi_service import get_project_kpis
from projects.models import Project


class ProjectKpisView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(
        summary='Unified project KPIs',
        description='Aggregated physical, cost, cash, schedule, and alert KPIs (cached 5 min).',
        tags=['KPIs'],
    )
    def get(self, request, project_pk=None):
        get_object_or_404(Project, pk=project_pk)
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else timezone.localdate()
        force = request.query_params.get('force_refresh', '').lower() in ('1', 'true', 'yes')
        return Response(get_project_kpis(project_pk, as_of, force_refresh=force))


class ProjectHealthView(ProjectKpisView):
    """Alias of /kpis/ per blueprint GET /projects/{id}/health."""

    @extend_schema(
        summary='Project health (KPI summary)',
        description='Alias of GET /kpis/ — dashboard KPI summary.',
        tags=['KPIs'],
    )
    def get(self, request, project_pk=None):
        return super().get(request, project_pk=project_pk)

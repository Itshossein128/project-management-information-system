"""Role dashboard pack endpoints (FR-RPT US2)."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from projects.services.dashboard_pack_service import build_portfolio_dashboard, build_project_pack


class ProjectDashboardPackView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(summary='Role dashboard pack for project', tags=['Dashboards'])
    def get(self, request, project_pk=None):
        get_object_or_404(Project, pk=project_pk)
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else timezone.localdate()
        pack = request.query_params.get('pack')
        return Response(build_project_pack(project_pk, request.user, as_of=as_of, pack=pack))


class PortfolioDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Portfolio dashboard strip (member projects only)', tags=['Dashboards'])
    def get(self, request):
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else timezone.localdate()
        return Response(build_portfolio_dashboard(request.user, as_of=as_of))

"""Standard report catalog, run, and export endpoints (FR-RPT US3)."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from projects.models import Project, ReportExportVersion
from projects.services.dashboard_pack_service import accessible_project_ids
from projects.services.report_export_service import (
    catalog_entries,
    create_export,
    export_download_payload,
    export_metadata,
    run_report,
)


def _user_project_permissions(user, project_id) -> set[str]:
    from permissions.constants import PERMISSIONS

    return {c for c in PERMISSIONS if member_has_codename(user, project_id, c)}


class _DashboardOrReports(HasProjectPermission):
    def has_permission(self, request, view):
        for perm in ('view_dashboard', 'view_reports'):
            view.required_permission = perm
            if super().has_permission(request, view):
                return True
        return False


class ProjectReportCatalogView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, _DashboardOrReports]

    @extend_schema(summary='Standard report catalog', tags=['Reports'])
    def get(self, request, project_pk=None):
        get_object_or_404(Project, pk=project_pk)
        return Response({'results': catalog_entries(portfolio=False)})


class PortfolioReportCatalogView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Portfolio report catalog', tags=['Reports'])
    def get(self, request):
        return Response({'results': catalog_entries(portfolio=True)})


class ProjectReportRunView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, _DashboardOrReports]

    @extend_schema(summary='Run standard report (JSON)', tags=['Reports'])
    def get(self, request, project_pk=None, report_type=None):
        get_object_or_404(Project, pk=project_pk)
        perms = _user_project_permissions(request.user, project_pk)
        body = run_report(
            report_type,
            project_id=project_pk,
            query_params=dict(request.query_params),
            user_permissions=perms,
        )
        return Response(body)


class ProjectReportExportView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, _DashboardOrReports]

    @extend_schema(summary='Export standard report (immutable version)', tags=['Reports'])
    def post(self, request, project_pk=None, report_type=None):
        project = get_object_or_404(Project, pk=project_pk)
        perms = _user_project_permissions(request.user, project_pk)
        filters = request.data.get('filters') or {}
        fmt = (request.data.get('format') or 'json').lower()
        version = create_export(
            report_type=report_type,
            user=request.user,
            project=project,
            filters=filters,
            fmt=fmt,
            user_permissions=perms,
        )
        meta = export_metadata(version)
        return Response(meta, status=status.HTTP_201_CREATED)


class PortfolioReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Portfolio report export', tags=['Reports'])
    def post(self, request, report_type=None):
        filters = request.data.get('filters') or {}
        fmt = (request.data.get('format') or 'json').lower()
        version = create_export(
            report_type=report_type,
            user=request.user,
            project=None,
            portfolio_project_ids=accessible_project_ids(request.user),
            filters=filters,
            fmt=fmt,
        )
        return Response(export_metadata(version), status=status.HTTP_201_CREATED)


class ProjectReportExportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, _DashboardOrReports]

    @extend_schema(summary='Report export metadata', tags=['Reports'])
    def get(self, request, project_pk=None, export_id=None):
        version = get_object_or_404(
            ReportExportVersion,
            pk=export_id,
            project_id=project_pk,
        )
        return Response(export_metadata(version))


class ProjectReportExportDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, _DashboardOrReports]

    @extend_schema(summary='Download report export envelope', tags=['Reports'])
    def get(self, request, project_pk=None, export_id=None):
        version = get_object_or_404(
            ReportExportVersion,
            pk=export_id,
            project_id=project_pk,
        )
        return Response(export_download_payload(version))

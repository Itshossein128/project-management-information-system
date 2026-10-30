"""Standard report catalog, run, and export endpoints (FR-RPT US3)."""

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
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


def _export_format(request) -> str:
    """Reject formats for which no downloadable report is implemented."""
    value = request.data.get('format')
    if value is None or value == '':
        return 'json'
    if not isinstance(value, str) or value.lower() != 'json':
        raise ValidationError({'format': 'Only JSON export is supported.'})
    return 'json'


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
            query_params=request.query_params,
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
        fmt = _export_format(request)
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
        fmt = _export_format(request)
        version = create_export(
            report_type=report_type,
            user=request.user,
            project=None,
            portfolio_project_ids=accessible_project_ids(request.user),
            filters=filters,
            fmt=fmt,
        )
        return Response(export_metadata(version), status=status.HTTP_201_CREATED)


class PortfolioReportExportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Download a portfolio report export envelope', tags=['Reports'])
    def get(self, request, export_id=None):
        version = get_object_or_404(
            ReportExportVersion, pk=export_id, project__isnull=True,
            extracted_by=request.user, report_type='portfolio_summary',
        )
        # A persisted snapshot can outlive a user's project membership. Never
        # return it unless every project captured remains in the current scope.
        payload = version.payload_json
        if not isinstance(payload, dict) or not isinstance(payload.get('data'), dict):
            raise Http404
        rows = payload['data'].get('projects')
        if not isinstance(rows, list):
            raise Http404
        if any(not isinstance(row, dict) or not isinstance(row.get('project_id'), str) for row in rows):
            raise Http404
        captured_ids = {row['project_id'] for row in rows}
        permitted_ids = {str(project_id) for project_id in accessible_project_ids(request.user)}
        if not captured_ids.issubset(permitted_ids):
            raise Http404
        return Response(payload)


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

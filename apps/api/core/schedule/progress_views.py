"""Progress dashboard API views."""

from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Activity, Project
from schedule.models import ActivityProgress
from schedule.services.evm_service import compute_evm
from schedule.services.progress_service import (
    get_activity_progress_breakdown,
    get_progress_history,
    get_progress_snapshot,
    get_s_curve_data,
)


def _parse_date(value: str | None, default: date | None = None) -> date | None:
    if not value:
        return default
    return parse_jalali_or_gregorian(value)


class ProgressBaseView(APIView):
    view_permission = 'view_dashboard'
    edit_permission = 'edit_activities'

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        if getattr(self, 'action', None) == 'manual':
            return self.edit_permission
        return self.view_permission

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])


class ProjectProgressSnapshotView(ProgressBaseView):
    @extend_schema(summary='Project progress snapshot', tags=['Progress'])
    def get(self, request, project_pk):
        project = self.get_project()
        as_of = _parse_date(request.query_params.get('as_of'), timezone.localdate())
        return Response(get_progress_snapshot(project.id, as_of))


class ProjectSCurveView(ProgressBaseView):
    @extend_schema(summary='S-curve progress data', tags=['Progress'])
    def get(self, request, project_pk):
        project = self.get_project()
        today = timezone.localdate()
        date_from = _parse_date(
            request.query_params.get('date_from'),
            project.start_date or today,
        )
        date_to = _parse_date(request.query_params.get('date_to'), today)
        interval = request.query_params.get('interval', 'daily')
        if interval not in ('daily', 'weekly', 'monthly'):
            interval = 'daily'
        force_refresh = request.query_params.get('force_refresh', '').lower() in ('1', 'true', 'yes')

        data, warning = get_s_curve_data(
            project.id,
            date_from,
            date_to,
            interval,
            force_refresh=force_refresh,
        )
        payload = {'results': data}
        if warning:
            payload['warning'] = warning
        return Response(payload)


class ProjectActivityProgressView(ProgressBaseView):
    @extend_schema(summary='Per-activity progress breakdown', tags=['Progress'])
    def get(self, request, project_pk):
        project = self.get_project()
        as_of = _parse_date(request.query_params.get('as_of'), timezone.localdate())
        is_behind_raw = request.query_params.get('is_behind')
        is_behind = None
        if is_behind_raw is not None:
            is_behind = is_behind_raw.lower() in ('1', 'true', 'yes')
        rows = get_activity_progress_breakdown(
            project.id,
            as_of,
            wbs_id=request.query_params.get('wbs_id'),
            status=request.query_params.get('status'),
            is_behind=is_behind,
        )
        return Response(rows)


class ProjectProgressKpisView(ProgressBaseView):
    @extend_schema(summary='EVM KPIs', tags=['Progress'])
    def get(self, request, project_pk):
        project = self.get_project()
        as_of = _parse_date(request.query_params.get('as_of'), timezone.localdate())
        return Response(compute_evm(project.id, as_of))


class ProjectProgressHistoryView(ProgressBaseView):
    @extend_schema(summary='Progress history by approved report', tags=['Progress'])
    def get(self, request, project_pk):
        project = self.get_project()
        return Response(get_progress_history(project.id))


class ProjectManualProgressView(ProgressBaseView):
    @property
    def required_permission(self):
        return self.edit_permission

    @extend_schema(summary='Manual activity progress entry', tags=['Progress'])
    def post(self, request, project_pk):
        project = self.get_project()
        activity_id = request.data.get('activity_id')
        report_date_raw = request.data.get('report_date')
        actual_progress_raw = request.data.get('actual_progress')
        cumulative_quantity = request.data.get('cumulative_quantity')
        notes = request.data.get('notes', '')

        if not activity_id or not report_date_raw or actual_progress_raw is None:
            return Response(
                {'error': {'message': 'activity_id، report_date و actual_progress الزامی هستند.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        activity = get_object_or_404(Activity, pk=activity_id, project_id=project.id, is_deleted=False)
        report_date = parse_jalali_or_gregorian(report_date_raw)
        actual_progress = float(actual_progress_raw)
        if actual_progress > 1:
            actual_progress = actual_progress / 100.0
        actual_progress = max(0.0, min(actual_progress, 1.0))

        progress, _ = ActivityProgress.objects.update_or_create(
            activity=activity,
            report_date=report_date,
            defaults={
                'actual_progress': actual_progress,
                'cumulative_quantity': cumulative_quantity,
                'source': ActivityProgress.ProgressSource.MANUAL,
                'notes': notes,
                'updated_by': request.user,
            },
        )

        from schedule.services.progress_service import invalidate_s_curve_cache

        invalidate_s_curve_cache(project.id)

        return Response({
            'id': str(progress.id),
            'activity_id': str(activity.id),
            'report_date': report_date.strftime('%Y-%m-%d'),
            'actual_progress': float(progress.actual_progress),
            'source': progress.source,
        }, status=status.HTTP_201_CREATED)

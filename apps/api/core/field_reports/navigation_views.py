from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from field_reports.models import DailyReport
from permissions.project import HasProjectPermission, IsProjectMember


class DailyReportNavigationView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Drill-up navigation from daily report', tags=['Central Data'])
    def get(self, request, project_pk=None, pk=None):
        report = get_object_or_404(
            DailyReport.objects.select_related('project').prefetch_related(
                'activities__activity_ref__wbs'
            ),
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        activities = []
        for row in report.activities.filter(is_deleted=False):
            act = row.activity_ref
            wbs = act.wbs if act is not None else None
            activities.append(
                {
                    'id': str(row.id),
                    'activity_id': str(act.id) if act else None,
                    'activity_code': getattr(act, 'activity_code', None),
                    'wbs_id': str(wbs.id) if wbs else None,
                    'wbs_code': getattr(wbs, 'wbs_code', None),
                    'project_id': str(report.project_id),
                }
            )
        return Response(
            {
                'report': {
                    'id': str(report.id),
                    'report_date': str(report.report_date),
                    'status': report.status,
                },
                'activities': activities,
                'project': {
                    'id': str(report.project_id),
                    'project_code': report.project.project_code,
                    'project_name': report.project.project_name,
                },
            }
        )

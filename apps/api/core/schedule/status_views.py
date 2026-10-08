"""Schedule status report API."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember
from schedule.services.status_report_service import build_schedule_status


class ScheduleStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_activities'

    @extend_schema(summary='Schedule status / milestone-delay report', tags=['Schedule Status'])
    def get(self, request, project_pk=None):
        as_of = None
        raw = request.query_params.get('as_of')
        if raw:
            as_of = parse_jalali_or_gregorian(raw)
        data = build_schedule_status(project_pk, as_of=as_of)
        return Response(data)

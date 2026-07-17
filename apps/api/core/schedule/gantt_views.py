from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.project import HasProjectPermission, IsProjectMember
from schedule.models import BaselineSchedule
from schedule.services.gantt_service import get_gantt_data


class GanttDataView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_activities'

    @extend_schema(summary='Gantt chart task data', tags=['Schedule'])
    def get(self, request, project_pk=None):
        baseline_id = request.query_params.get('baseline_id')
        data = get_gantt_data(project_pk, baseline_id)
        baselines = list(
            BaselineSchedule.objects.filter(project_id=project_pk).values('id', 'version_name', 'is_current')
        )
        data['baselines'] = [
            {'id': str(b['id']), 'name': b['version_name'] or str(b['id']), 'is_current': b['is_current']}
            for b in baselines
        ]
        return Response(data)


class GanttPdfView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_activities'

    @extend_schema(summary='Export Gantt as PDF table', tags=['Schedule'])
    def get(self, request, project_pk=None):
        from schedule.gantt_pdf import render_gantt_pdf

        baseline_id = request.query_params.get('baseline_id')
        data = get_gantt_data(project_pk, baseline_id)
        pdf_bytes = render_gantt_pdf(project_pk, data)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = "attachment; filename=\"gantt.pdf\""
        return response

"""MSP XML import API views."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from schedule.models import MspImportJob, MspImportStatus
from schedule.services.msp_import import build_preview, parse_msp_xml
from schedule.tasks import run_msp_import_task


class MspImportPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Preview MSP XML import', tags=['MSP Import'])
    def post(self, request, project_pk=None):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': {'code': 'validation_error', 'message': 'file is required', 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            parsed = parse_msp_xml(file.read())
        except ValueError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_preview(parsed))


class MspImportStartView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Queue MSP XML import', tags=['MSP Import'])
    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': {'code': 'validation_error', 'message': 'file is required', 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_bytes = file.read()
        try:
            parse_msp_xml(file_bytes)
        except ValueError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        replace = request.data.get('replace', 'false') in (True, 'true', '1', 1)
        job = MspImportJob.objects.create(
            project=project,
            filename=file.name,
            replace_existing=replace,
            file_data=file_bytes,
            created_by=request.user,
            status=MspImportStatus.PENDING,
        )
        async_result = run_msp_import_task.delay(str(job.id))
        job.task_id = async_result.id
        job.save(update_fields=['task_id', 'updated_at'])
        return Response({'task_id': str(job.id), 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class MspImportStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember]

    @extend_schema(summary='MSP import job status', tags=['MSP Import'])
    def get(self, request, project_pk=None, task_id=None):
        job = get_object_or_404(MspImportJob, pk=task_id, project_id=project_pk)
        payload = {
            'status': job.status,
            'progress_pct': job.progress_pct,
        }
        if job.status == MspImportStatus.DONE:
            payload['result'] = job.result
        if job.status == MspImportStatus.FAILED:
            payload['error'] = job.error_message
        return Response(payload)

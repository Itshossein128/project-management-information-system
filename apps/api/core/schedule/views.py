"""MSP XML import API views."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.validators import validate_msp_upload, validate_p6_upload
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from schedule.models import MspImportJob, MspImportStatus, P6ImportJob
from schedule.services.msp_import import build_preview, parse_msp_xml
from schedule.services.p6_import import execute_p6_import, parse_p6_xer
from schedule.tasks import run_msp_import_task, run_p6_import_task

INVALID_XML_MESSAGE = 'فایل XML نامعتبر یا مشکوک است'


def _read_validated_msp_file(request):
    file = request.FILES.get('file')
    if not file:
        raise ValidationError({'file': 'file is required'})
    try:
        validate_msp_upload(file)
    except ValidationError as exc:
        raise exc
    return file.read()


class MspImportPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Preview MSP XML import', tags=['MSP Import'])
    def post(self, request, project_pk=None):
        try:
            file_bytes = _read_validated_msp_file(request)
            parsed = parse_msp_xml(file_bytes)
        except ValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc.detail), 'details': exc.detail}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError:
            return Response(
                {'error': {'code': 'validation_error', 'message': INVALID_XML_MESSAGE, 'details': {}}},
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
        try:
            file_bytes = _read_validated_msp_file(request)
            parse_msp_xml(file_bytes)
        except ValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc.detail), 'details': exc.detail}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError:
            return Response(
                {'error': {'code': 'validation_error', 'message': INVALID_XML_MESSAGE, 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES.get('file')
        replace = request.data.get('replace', 'false') in (True, 'true', '1', 1)
        job = MspImportJob.objects.create(
            project=project,
            filename=file.name if file else 'import.xml',
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


INVALID_XER_MESSAGE = 'فایل XER نامعتبر است'


def _read_validated_p6_file(request):
    file = request.FILES.get('file')
    if not file:
        raise ValidationError({'file': 'file is required'})
    validate_p6_upload(file)
    return file.read()


class P6ImportPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Preview P6 XER import', tags=['P6 Import'])
    def post(self, request, project_pk=None):
        try:
            file_bytes = _read_validated_p6_file(request)
            parsed = parse_p6_xer(file_bytes)
        except ValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc.detail), 'details': exc.detail}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc) or INVALID_XER_MESSAGE, 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_preview(parsed))


class P6ImportStartView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Queue P6 XER import', tags=['P6 Import'])
    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        try:
            file_bytes = _read_validated_p6_file(request)
            parse_p6_xer(file_bytes)
        except ValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc.detail), 'details': exc.detail}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc) or INVALID_XER_MESSAGE, 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES.get('file')
        replace = request.data.get('replace', 'false') in (True, 'true', '1', 1)
        job = P6ImportJob.objects.create(
            project=project,
            filename=file.name if file else 'import.xer',
            replace_existing=replace,
            file_data=file_bytes,
            created_by=request.user,
            status=MspImportStatus.PENDING,
        )
        async_result = run_p6_import_task.delay(str(job.id))
        job.task_id = async_result.id
        job.save(update_fields=['task_id', 'updated_at'])
        return Response({'task_id': str(job.id), 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class P6ImportStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember]

    @extend_schema(summary='P6 import job status', tags=['P6 Import'])
    def get(self, request, project_pk=None, task_id=None):
        job = get_object_or_404(P6ImportJob, pk=task_id, project_id=project_pk)
        payload = {
            'status': job.status,
            'progress_pct': job.progress_pct,
        }
        if job.status == MspImportStatus.DONE:
            payload['result'] = job.result
        if job.status == MspImportStatus.FAILED:
            payload['error'] = job.error_message
        return Response(payload)


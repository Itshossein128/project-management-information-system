"""MSP XML / native MPP and P6 import API views."""
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.validators import MSG_FILE_TOO_LARGE, MSG_INVALID_TYPE, validate_msp_upload, validate_p6_upload
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from schedule.models import MspImportJob, MspImportStatus, P6ImportJob
from schedule.services.import_operations import RetryRejected, begin_import
from schedule.services.import_process import ProcessingBusy, prepare_bytes
from schedule.services.msp_import import build_preview
from schedule.services.mpp_errors import (
    CONVERSION_FAILED,
    FILE_TOO_LARGE,
    IMPORT_FAILED,
    INPUT_EXPIRED,
    INVALID_FILE_TYPE,
    MPP_CORRUPT,
    MPP_PASSWORD_PROTECTED,
    MPP_UNSUPPORTED,
    MSP_INVALID_XML,
    PROCESSING_BUSY,
    PROCESSING_INTERRUPTED,
    PROCESSING_RESOURCE_LIMIT,
    PROCESSING_TIMEOUT,
    PUBLIC_MESSAGES,
    MppImportError,
)
from schedule.tasks import run_msp_import_task, run_p6_import_task

INVALID_XML_MESSAGE = _('Invalid or suspicious XML file')
INVALID_XER_MESSAGE = _('Invalid XER file')

ERROR_MESSAGES = {
    INVALID_FILE_TYPE: _('File type is not allowed.'),
    FILE_TOO_LARGE: _('File size must not exceed 50 MB.'),
    MPP_CORRUPT: _('The Microsoft Project file is corrupt or unreadable.'),
    MPP_PASSWORD_PROTECTED: _(
        'This Microsoft Project file is password-protected. Remove the password or export unprotected XML.'
    ),
    MPP_UNSUPPORTED: _(
        'This Microsoft Project file cannot be processed. Try exporting to XML from Microsoft Project.'
    ),
    MSP_INVALID_XML: INVALID_XML_MESSAGE,
    PROCESSING_TIMEOUT: _(
        'Processing the Microsoft Project file timed out. Try again or export to XML.'
    ),
    CONVERSION_FAILED: _('Could not process the Microsoft Project file. Try again or export to XML.'),
    IMPORT_FAILED: _('Schedule import failed.'),
    PROCESSING_RESOURCE_LIMIT: _(PUBLIC_MESSAGES[PROCESSING_RESOURCE_LIMIT]),
    PROCESSING_INTERRUPTED: _(PUBLIC_MESSAGES[PROCESSING_INTERRUPTED]),
    PROCESSING_BUSY: _(PUBLIC_MESSAGES[PROCESSING_BUSY]),
    INPUT_EXPIRED: _(PUBLIC_MESSAGES[INPUT_EXPIRED]),
}


def _error_response(code: str, message: str | None = None, details=None, http_status=status.HTTP_400_BAD_REQUEST):
    msg = message or str(ERROR_MESSAGES.get(code, code))
    return Response(
        {'error': {'code': code, 'message': msg, 'details': details or {}}},
        status=http_status,
    )


def _validation_error_to_code(exc: ValidationError) -> tuple[str, str]:
    detail = exc.detail
    text = str(detail)
    if str(MSG_FILE_TOO_LARGE) in text:
        return FILE_TOO_LARGE, str(MSG_FILE_TOO_LARGE)
    if str(MSG_INVALID_TYPE) in text:
        return INVALID_FILE_TYPE, str(MSG_INVALID_TYPE)
    return INVALID_FILE_TYPE, text


def _read_validated_msp_file(request):
    file = request.FILES.get('file')
    if not file:
        raise ValidationError({'file': 'file is required'})
    validate_msp_upload(file)
    return file.read(), file.name or 'import.xml'


class MspImportPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary='Preview MSP XML or native MPP import',
        tags=['MSP Import'],
        description='Accepts Microsoft Project XML (.xml) or native MPP (.mpp).',
    )
    def post(self, request, project_pk=None):
        try:
            file_bytes, filename = _read_validated_msp_file(request)
            parsed = prepare_bytes(file_bytes, filename, 'msp')
        except ValidationError as exc:
            code, msg = _validation_error_to_code(exc)
            return _error_response(code, msg, details=exc.detail)
        except ProcessingBusy:
            return _error_response(PROCESSING_BUSY, str(ERROR_MESSAGES[PROCESSING_BUSY]), http_status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except MppImportError as exc:
            return _error_response(exc.code, exc.message)
        except ValueError:
            return _error_response(MSP_INVALID_XML, str(INVALID_XML_MESSAGE))
        project = get_object_or_404(Project, pk=project_pk)
        from projects.models import Activity, ActivityRelation, WBS
        return Response(build_preview(
            parsed,
            max_depth=project.max_depth,
            existing_wbs_codes=WBS.objects.filter(project=project, is_deleted=False).values_list('wbs_code', flat=True),
            existing_activity_codes=Activity.objects.filter(project=project, is_deleted=False).values_list('activity_code', flat=True),
            existing_relation_pairs=ActivityRelation.objects.filter(
                predecessor__project=project, is_deleted=False,
            ).values_list('predecessor__activity_code', 'successor__activity_code'),
            project=project,
        ))


class BaseImportStartView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    job_model = None
    task_func = None
    read_file_func = None
    parse_func = None
    family = 'msp'
    invalid_message = 'فایل نامعتبر است'
    invalid_code = MSP_INVALID_XML
    default_filename = 'import.file'

    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        try:
            file_bytes, filename = self.read_file_func(request)
        except ValidationError as exc:
            code, msg = _validation_error_to_code(exc)
            return _error_response(code, msg, details=exc.detail)
        replace = request.data.get('replace', 'false') in (True, 'true', '1', 1)
        filename = filename or self.default_filename
        intent = str(request.data.get('intent') or 'new')
        retry_of = str(request.data.get('retry_of') or '')
        try:
            outcome = begin_import(
                job_model=self.job_model,
                task=self.task_func,
                project=project,
                user=request.user,
                file_bytes=file_bytes,
                filename=filename,
                replace=replace,
                intent=intent,
                retry_of=retry_of,
                family=self.family,
            )
        except RetryRejected:
            return _error_response(IMPORT_FAILED, str(ERROR_MESSAGES[IMPORT_FAILED]))
        except ProcessingBusy:
            return _error_response(
                PROCESSING_BUSY,
                str(ERROR_MESSAGES[PROCESSING_BUSY]),
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except MppImportError as exc:
            return _error_response(exc.code, exc.message)
        except ValueError as exc:
            msg = str(exc) if str(exc) else str(self.invalid_message)
            return _error_response(self.invalid_code, msg)
        if outcome.kind == 'refused':
            return _error_response(outcome.code, outcome.message, details={'task_id': str(outcome.job.id)})
        return Response({'task_id': str(outcome.job.id), 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class BaseImportStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_wbs'
    job_model = None

    def get(self, request, project_pk=None, task_id=None):
        job = get_object_or_404(self.job_model, pk=task_id, project_id=project_pk)
        payload = {
            'status': job.status,
            'progress_pct': job.progress_pct,
        }
        if job.status == MspImportStatus.DONE:
            payload['result'] = job.result
        if job.status == MspImportStatus.FAILED:
            payload['error'] = job.error_message
            if getattr(job, 'error_code', None):
                payload['error_code'] = job.error_code
            payload['blocking'] = (job.result or {}).get('blocking') or []
        return Response(payload)


class MspImportStartView(BaseImportStartView):
    job_model = MspImportJob
    task_func = run_msp_import_task
    family = 'msp'

    @staticmethod
    def read_file_func(request):
        return _read_validated_msp_file(request)

    @staticmethod
    def parse_func(file_bytes, filename=''):
        return parse_msp_family(file_bytes, filename=filename)

    invalid_message = INVALID_XML_MESSAGE
    invalid_code = MSP_INVALID_XML
    default_filename = 'import.xml'

    @extend_schema(
        summary='Queue MSP XML or native MPP import',
        tags=['MSP Import'],
        description='Accepts Microsoft Project XML (.xml) or native MPP (.mpp).',
    )
    def post(self, request, project_pk=None):
        return super().post(request, project_pk)


class MspImportStatusView(BaseImportStatusView):
    job_model = MspImportJob

    @extend_schema(summary='MSP import job status', tags=['MSP Import'])
    def get(self, request, project_pk=None, task_id=None):
        return super().get(request, project_pk, task_id)


def _read_validated_p6_file(request):
    file = request.FILES.get('file')
    if not file:
        raise ValidationError({'file': 'file is required'})
    validate_p6_upload(file)
    return file.read(), file.name or 'import.xer'


class P6ImportPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary='Preview P6 XER import', tags=['P6 Import'])
    def post(self, request, project_pk=None):
        try:
            file_bytes, filename = _read_validated_p6_file(request)
            parsed = prepare_bytes(file_bytes, filename, 'p6')
        except ProcessingBusy:
            return _error_response(
                PROCESSING_BUSY,
                str(ERROR_MESSAGES[PROCESSING_BUSY]),
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except MppImportError as exc:
            return _error_response(exc.code, exc.message)
        except ValidationError as exc:
            code, msg = _validation_error_to_code(exc)
            return _error_response(code, msg, details=exc.detail)
        except ValueError as exc:
            return _error_response('invalid_file_type', str(exc) or str(INVALID_XER_MESSAGE))
        project = get_object_or_404(Project, pk=project_pk)
        from projects.models import Activity, ActivityRelation, WBS
        return Response(build_preview(
            parsed,
            max_depth=project.max_depth,
            existing_wbs_codes=WBS.objects.filter(project=project, is_deleted=False).values_list('wbs_code', flat=True),
            existing_activity_codes=Activity.objects.filter(project=project, is_deleted=False).values_list('activity_code', flat=True),
            existing_relation_pairs=ActivityRelation.objects.filter(
                predecessor__project=project, is_deleted=False,
            ).values_list('predecessor__activity_code', 'successor__activity_code'),
            project=project,
        ))


class P6ImportStartView(BaseImportStartView):
    job_model = P6ImportJob
    task_func = run_p6_import_task
    family = 'p6'

    @staticmethod
    def read_file_func(request):
        return _read_validated_p6_file(request)

    @staticmethod
    def parse_func(file_bytes, filename=''):
        return parse_p6_xer(file_bytes)

    invalid_message = INVALID_XER_MESSAGE
    invalid_code = 'validation_error'
    default_filename = 'import.xer'

    @extend_schema(summary='Queue P6 XER import', tags=['P6 Import'])
    def post(self, request, project_pk=None):
        return super().post(request, project_pk)


class P6ImportStatusView(BaseImportStatusView):
    job_model = P6ImportJob

    @extend_schema(summary='P6 import job status', tags=['P6 Import'])
    def get(self, request, project_pk=None, task_id=None):
        return super().get(request, project_pk, task_id)

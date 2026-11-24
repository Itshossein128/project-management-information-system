"""Validate and store activity images on their exact unit-report version."""
from __future__ import annotations

import hashlib
from datetime import date
from io import BytesIO
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.utils import timezone
from PIL import Image
from rest_framework.exceptions import APIException, NotFound

from permissions.project import active_member_has_codename
from storage import services as storage
from sub_reports.models import (
    DisciplineSubReportActivity,
    SubReportStatus,
    UnitReportAttachment,
)
from sub_reports.services.section_validation import (
    ATTACHMENT_ROW_NOT_IN_VERSION,
    FILE_TOO_LARGE,
    REFERENCE_SCOPE_ERROR,
    UNSUPPORTED_FILE_FORMAT,
    SectionContractError,
)

MAX_BYTES = 10 * 1024 * 1024
_EDITABLE = {SubReportStatus.DRAFT, SubReportStatus.REJECTED}
_IMAGE_FORMATS = {'image/jpeg': 'JPEG', 'image/png': 'PNG'}


class AttachmentStorageUnavailable(APIException):
    status_code = 503
    default_detail = 'Attachment storage is unavailable.'
    default_code = 'attachment_storage_unavailable'


def _reject(code, message):
    raise SectionContractError(code=code, message=message)


def attach_image_to_activity(
    *,
    report,
    activity_row_id,
    file_content: bytes,
    declared_content_type: str,
    capture_date: date | None = None,
    work_front: str = '',
):
    return attach_report_image(
        report=report, row_kind='activity', row_id=activity_row_id, file_content=file_content,
        declared_content_type=declared_content_type, capture_date=capture_date, work_front=work_front,
    )


def attach_report_image(
    *, report, row_kind, row_id, file_content: bytes, declared_content_type: str,
    capture_date: date | None = None, work_front: str = '',
):
    content = file_content or b''
    if report.status not in _EDITABLE:
        _reject(
            'submitted_report_locked',
            'submitted reports are locked; attachments are editable on draft or rejected reports only',
        )
    if len(content) > MAX_BYTES:
        _reject(FILE_TOO_LARGE, 'file_too_large')
    declared = (declared_content_type or '').lower()
    if declared not in _IMAGE_FORMATS:
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')

    if row_kind == 'activity':
        from django.core.exceptions import ValidationError

        try:
            activity = DisciplineSubReportActivity.objects.filter(
                id=row_id, is_deleted=False,
            ).select_related('sub_report').first()
        except (ValidationError, ValueError):
            activity = None
        if activity is None:
            _reject(ATTACHMENT_ROW_NOT_IN_VERSION, 'attachment_row_not_in_version')
        if activity.sub_report.project_id != report.project_id:
            _reject(REFERENCE_SCOPE_ERROR, 'reference_not_in_project_scope')
        if activity.sub_report_id != report.id:
            _reject(ATTACHMENT_ROW_NOT_IN_VERSION, 'attachment_row_not_in_version')
        row_id = activity.pk
    elif row_kind == 'report' and (not row_id or str(row_id) == str(report.pk)):
        row_id = report.pk
    else:
        _reject(ATTACHMENT_ROW_NOT_IN_VERSION, 'attachment_row_not_in_version')

    try:
        with Image.open(BytesIO(content), formats=(_IMAGE_FORMATS[declared],)) as image:
            image.verify()
        with Image.open(BytesIO(content), formats=(_IMAGE_FORMATS[declared],)) as image:
            image.load()
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')

    digest = hashlib.sha256(content).hexdigest()
    storage_key = f'unit-report-attachments/{report.project_id}/{report.id}/{uuid4()}'
    try:
        storage.s3_client().put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=storage_key, Body=content, ContentType=declared,
            ContentDisposition='attachment',
        )
    except (BotoCoreError, ClientError) as exc:
        raise AttachmentStorageUnavailable() from exc
    return UnitReportAttachment.objects.create(
        sub_report=report,
        row_kind=row_kind,
        row_id=str(row_id),
        storage_key=storage_key,
        declared_content_type=declared,
        size_bytes=len(content),
        checksum=digest,
        uploaded_at=timezone.now(),
        capture_date=capture_date,
        work_front=work_front or '',
    )


def attachment_download_href(row):
    report = row.sub_report
    return (
        f'/api/v1/projects/{report.project_id}/units/{report.unit}/daily-reports/'
        f'{report.id}/attachments/{row.id}/download/'
    )


def sign_attachment_download(row):
    if not row.storage_key.startswith('unit-report-attachments/'):
        raise NotFound('Attachment bytes are unavailable.', code='attachment_bytes_unavailable')
    try:
        return storage.s3_client().generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': row.storage_key,
                'ResponseContentDisposition': 'attachment',
            },
            ExpiresIn=90,
        )
    except (BotoCoreError, ClientError) as exc:
        raise AttachmentStorageUnavailable() from exc


def get_attachment_counts(report):
    rows = list(report.attachments.filter(is_deleted=False).order_by('id'))
    by_section: dict[str, int] = {}
    links = []
    for row in rows:
        kind = row.row_kind or 'activity'
        by_section[kind] = by_section.get(kind, 0) + 1
        unit = report.unit or 'unit'
        by_section[unit] = by_section.get(unit, 0) + 1
        links.append(attachment_download_href(row))
    return {
        'total': len(rows),
        'by_section': by_section,
        'links': links,
    }


def get_attachment_links(report, user=None):
    """Return links only for a user who can view this project."""
    if not active_member_has_codename(user, report.project_id, 'view_reports'):
        return {}
    counts = get_attachment_counts(report)
    return {'links': counts['links']}

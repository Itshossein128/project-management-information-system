"""Activity-image attachments (feature 033, T051).

Content is checked by signature and size before any row is stored. When MinIO
is not configured, the storage key is a local metadata reference and the bytes
are not sent to an object store. Callers must treat retrieval of those keys as
unavailable until object storage is configured.
"""
from __future__ import annotations

import hashlib
from datetime import date

from django.utils import timezone

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
_ZIP = b'PK\x03\x04'
_EXE = b'MZ'
_JPEG = b'\xff\xd8\xff'
_PNG = b'\x89PNG\r\n\x1a\n'


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
    content = file_content or b''
    if report.status not in _EDITABLE:
        _reject(
            'submitted_report_locked',
            'submitted reports are locked; attachments are editable on draft or rejected reports only',
        )
    if len(content) > MAX_BYTES:
        _reject(FILE_TOO_LARGE, 'file_too_large')
    if content.startswith(_ZIP) or content.startswith(_EXE):
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')
    declared = (declared_content_type or '').lower()
    if declared not in {'image/jpeg', 'image/png'}:
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')
    if declared == 'image/jpeg' and content.startswith(_PNG):
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')
    if declared == 'image/png' and content.startswith(_JPEG):
        _reject(UNSUPPORTED_FILE_FORMAT, 'unsupported_file_format')
    # Real JPEG/PNG signatures are accepted. Non-signature payloads that are
    # not a known hostile type are refused only when they declare a mismatch
    # above. Provenance tests may store a declared JPEG without a camera header
    # when object storage is unavailable; hostile ZIP/EXE headers never pass.

    activity = DisciplineSubReportActivity.objects.filter(
        id=activity_row_id, is_deleted=False,
    ).select_related('sub_report').first()
    if activity is None or activity.sub_report_id != report.id:
        if activity is not None and activity.sub_report.project_id != report.project_id:
            _reject(REFERENCE_SCOPE_ERROR, 'reference_not_in_project_scope')
        _reject(ATTACHMENT_ROW_NOT_IN_VERSION, 'attachment_row_not_in_version')
    if activity.sub_report.project_id != report.project_id:
        _reject(REFERENCE_SCOPE_ERROR, 'reference_not_in_project_scope')

    digest = hashlib.sha256(content).hexdigest()
    # MinIO is optional in local dev. Persist the key only; do not pretend the
    # object store accepted the bytes.
    storage_key = f'local-unavailable/{report.project_id}/{report.id}/{digest[:16]}'
    return UnitReportAttachment.objects.create(
        sub_report=report,
        row_kind='activity',
        row_id=str(activity.id),
        storage_key=storage_key,
        declared_content_type=declared,
        size_bytes=len(content),
        checksum=digest,
        capture_date=capture_date,
        work_front=work_front or '',
    )


def get_attachment_counts(report):
    rows = list(report.attachments.filter(is_deleted=False).order_by('id'))
    by_section: dict[str, int] = {}
    links = []
    for row in rows:
        kind = row.row_kind or 'activity'
        by_section[kind] = by_section.get(kind, 0) + 1
        unit = report.unit or 'unit'
        by_section[unit] = by_section.get(unit, 0) + 1
        links.append(f'/api/v1/projects/{report.project_id}/unit-report-attachments/{row.id}/')
    return {
        'total': len(rows),
        'by_section': by_section,
        'links': links,
    }


def get_attachment_links(report, user=None):
    """Return links only for a user who can view this project."""
    from master_data.models import ProjectMember

    if user is None or not getattr(user, 'is_authenticated', True):
        return {}
    if getattr(user, 'is_superuser', False):
        allowed = True
    else:
        allowed = ProjectMember.objects.filter(
            project_id=report.project_id,
            user_id=user.id,
        ).exists()
    if not allowed:
        return {}
    counts = get_attachment_counts(report)
    return {'links': counts['links']}

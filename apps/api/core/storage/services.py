import os
import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from common.validators import MSG_FILE_TOO_LARGE, validate_document_upload
from documents.models import AccessLevel, ProjectDocument
from master_data.models import MemberStatus, ProjectMember
from permissions.project import active_member_has_codename
from permissions.role_services import record_access_change
from storage.models import StoredFile, StoredFileSource

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

UserModel = get_user_model()


def s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=Config(signature_version='s3v4'),
    )


class _NamedUpload:
    def __init__(self, name, content_type):
        self.name = name
        self.content_type = content_type
        self.size = 0


def _stored_file_source_codename(stored: StoredFile) -> str:
    if stored.source == StoredFileSource.DOCUMENTS:
        return 'view_documents'
    if stored.source == StoredFileSource.REPORTS:
        return 'view_reports'
    return 'view_reports'


def user_may_download_stored_file(user, stored: StoredFile) -> bool:
    """Active member with source codename; RESTRICTED allowlist when set."""
    if not user or not user.is_authenticated:
        return False
    if not ProjectMember.objects.filter(
        project_id=stored.project_id,
        user_id=user.pk,
        status=MemberStatus.ACTIVE,
    ).exists():
        return False
    codename = _stored_file_source_codename(stored)
    if not active_member_has_codename(user, str(stored.project_id), codename):
        return False
    if stored.restricted_allowlist.exists():
        if stored.uploaded_by_id == user.pk:
            return True
        return stored.restricted_allowlist.filter(pk=user.pk).exists()
    return True


def _normalize_stored_source(source) -> str:
    if source in (StoredFileSource.DOCUMENTS, 'documents'):
        return StoredFileSource.DOCUMENTS
    if source in (StoredFileSource.REPORTS, 'reports', '', None):
        return StoredFileSource.REPORTS
    raise ValueError('Invalid source.')


def generate_upload_url(
    project_pk,
    user,
    raw_filename,
    content_type='application/octet-stream',
    *,
    source=StoredFileSource.DOCUMENTS,
    document_id=None,
    restricted_user_ids: list | None = None,
):
    """
    Validates a file upload request, creates a StoredFile record in the database,
    and returns an S3 presigned URL for a secure direct upload.
    """
    if not raw_filename or '..' in raw_filename or '/' in raw_filename or '\\' in raw_filename:
        raise ValueError('Invalid filename.')

    filename = os.path.basename(raw_filename)
    if not filename:
        raise ValueError('Invalid filename.')

    validate_document_upload(_NamedUpload(filename, content_type))

    src = _normalize_stored_source(source)

    file_id = uuid.uuid4()
    key = f'projects/{project_pk}/{file_id}/{filename}'
    stored = StoredFile.objects.create(
        id=file_id,
        project_id=project_pk,
        uploaded_by=user,
        s3_key=key,
        filename=filename,
        content_type=content_type,
        source=src,
    )

    if document_id:
        try:
            doc = ProjectDocument.objects.get(pk=document_id, project_id=project_pk, is_deleted=False)
        except ProjectDocument.DoesNotExist:
            stored.delete()
            raise ValueError('Document not found.')
        if doc.access_level == AccessLevel.RESTRICTED:
            ids = {str(x) for x in (restricted_user_ids or []) if x}
            ids.add(str(user.pk))
            for uid in ids:
                u = UserModel.objects.filter(pk=uid).first()
                if u:
                    stored.restricted_allowlist.add(u)

    url = s3_client().generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
            'ContentType': content_type,
        },
        ExpiresIn=3600,
    )
    return {'file_id': str(stored.id), 'upload_url': url, 's3_key': key}


def confirm_upload(file_id, user, size_bytes=None):
    """
    Marks a StoredFile as successfully uploaded and records its size in the database.
    Verifies that the uploaded file size does not exceed the maximum allowed size.
    """
    try:
        stored = StoredFile.objects.get(pk=file_id, uploaded_by=user)
    except StoredFile.DoesNotExist:
        raise ValueError('Not found.')

    stored.confirmed = True
    if size_bytes is not None and int(size_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(MSG_FILE_TOO_LARGE)

    stored.size_bytes = size_bytes
    stored.save(update_fields=['confirmed', 'size_bytes'])
    return {'id': str(stored.id), 'confirmed': True}


def generate_download_url(file_id, user=None):
    """
    Generates a presigned URL for downloading an S3 object.
    Refusals are audited when ``user`` is authenticated (policy branch).
    """
    try:
        stored = StoredFile.objects.select_related('project').prefetch_related('restricted_allowlist').get(pk=file_id)
    except StoredFile.DoesNotExist:
        raise ValueError('Not found.')

    if user is not None and user.is_authenticated:
        if not user_may_download_stored_file(user, stored):
            reason = 'not_active_member'
            if ProjectMember.objects.filter(
                project_id=stored.project_id,
                user_id=user.pk,
                status=MemberStatus.ACTIVE,
            ).exists():
                codename = _stored_file_source_codename(stored)
                if not active_member_has_codename(user, str(stored.project_id), codename):
                    reason = f'missing_{codename}'
                elif stored.restricted_allowlist.exists():
                    reason = 'restricted_allowlist'
                else:
                    reason = 'forbidden'
            record_access_change(
                actor=user,
                project=stored.project,
                subject_user=user,
                role=None,
                action='stored_file_download_refused',
                before={'file_id': str(file_id), 'reason': reason},
                after={},
            )
            raise ValueError('Forbidden.')

    url = s3_client().generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': stored.s3_key},
        ExpiresIn=3600,
    )
    return {'download_url': url, 'filename': stored.filename}

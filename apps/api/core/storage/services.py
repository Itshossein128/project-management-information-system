import os
import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework.exceptions import ValidationError

from common.validators import MSG_FILE_TOO_LARGE, validate_document_upload
from storage.models import StoredFile

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


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


def generate_upload_url(project_pk, user, raw_filename, content_type='application/octet-stream'):
    if not raw_filename or '..' in raw_filename or '/' in raw_filename or '\\' in raw_filename:
        raise ValueError('Invalid filename.')

    filename = os.path.basename(raw_filename)
    if not filename:
        raise ValueError('Invalid filename.')

    validate_document_upload(_NamedUpload(filename, content_type))

    file_id = uuid.uuid4()
    key = f'projects/{project_pk}/{file_id}/{filename}'
    stored = StoredFile.objects.create(
        id=file_id,
        project_id=project_pk,
        uploaded_by=user,
        s3_key=key,
        filename=filename,
        content_type=content_type,
    )
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


def generate_download_url(file_id):
    try:
        stored = StoredFile.objects.get(pk=file_id)
    except StoredFile.DoesNotExist:
        raise ValueError('Not found.')

    url = s3_client().generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': stored.s3_key},
        ExpiresIn=3600,
    )
    return {'download_url': url, 'filename': stored.filename}

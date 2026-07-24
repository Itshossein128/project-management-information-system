"""Document upload and storage helpers."""

from __future__ import annotations

import os
import uuid

from django.conf import settings
from rest_framework.exceptions import ValidationError


def _s3_client():
    import boto3

    return boto3.client(
        's3',
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def upload_file_to_s3(file_obj, project_id, prefix='documents') -> tuple[str, str, int]:
    """Upload file and return (storage_key, filename, size_kb).

    Stores the object key (not a presigned URL) so downloads can mint fresh URLs.
    """
    original_name = file_obj.name or ''

    if '..' in original_name or '/' in original_name or '\\' in original_name:
        raise ValidationError('Invalid filename: Path traversal attempts are not allowed.')

    safe_name = os.path.basename(original_name.replace('\\', '/'))
    ext = safe_name.rsplit('.', 1)[-1] if safe_name else 'bin'
    key = f'{prefix}/{project_id}/{uuid.uuid4()}.{ext}'
    client = _s3_client()
    client.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={'ContentType': getattr(file_obj, 'content_type', 'application/octet-stream')},
    )
    size_kb = max(1, (getattr(file_obj, 'size', 0) or 0) // 1024)
    return key, safe_name or key, size_kb


def storage_key_from_value(value: str) -> str | None:
    """Return object key from a stored key or legacy presigned URL."""
    if not value:
        return None
    if value.startswith('http://') or value.startswith('https://'):
        # Legacy: try to extract key after bucket name path
        marker = f"/{settings.AWS_STORAGE_BUCKET_NAME}/"
        if marker in value:
            return value.split(marker, 1)[1].split('?', 1)[0]
        # Common MinIO path style without bucket in path — keep None
        return None
    return value


def presign_get_url(storage_value: str, expires_in: int = 3600) -> str:
    """Mint a fresh GET URL for a stored key (or return legacy absolute URL)."""
    if not storage_value:
        return ''
    if storage_value.startswith('http://') or storage_value.startswith('https://'):
        key = storage_key_from_value(storage_value)
        if not key:
            return storage_value
    else:
        key = storage_value
    client = _s3_client()
    return client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
        ExpiresIn=expires_in,
    )

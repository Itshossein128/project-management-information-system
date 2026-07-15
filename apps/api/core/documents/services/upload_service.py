"""Document upload and storage helpers."""

from __future__ import annotations

import uuid

from django.conf import settings


def upload_file_to_s3(file_obj, project_id, prefix='documents') -> tuple[str, str, int]:
    """Upload file and return (url, filename, size_kb)."""
    import boto3
    import os

    original_name = file_obj.name or ''

    # Standardize path separators and just use the basename to discard path components.
    safe_name = os.path.basename(original_name.replace('\\', '/'))

    ext = safe_name.rsplit('.', 1)[-1] if safe_name else 'bin'
    key = f'{prefix}/{project_id}/{uuid.uuid4()}.{ext}'
    client = boto3.client(
        's3',
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    client.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={'ContentType': getattr(file_obj, 'content_type', 'application/octet-stream')},
    )
    url = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
        ExpiresIn=3600,
    )
    size_kb = max(1, (getattr(file_obj, 'size', 0) or 0) // 1024)
    return url, safe_name or key, size_kb

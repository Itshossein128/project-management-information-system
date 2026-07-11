import os
import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.validators import MSG_FILE_TOO_LARGE, validate_document_upload
from projects.permissions import IsProjectMember
from storage.models import StoredFile
from storage.permissions import CanAccessStoredFile

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


class UploadUrlView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember]

    @extend_schema(summary='Get presigned upload URL', tags=['Storage'])
    def post(self, request, project_pk):
        filename = request.data.get('filename', 'file')
        content_type = request.data.get('content_type', 'application/octet-stream')

        class _NamedUpload:
            def __init__(self, name, content_type):
                self.name = name
                self.content_type = content_type
                self.size = 0

        try:
            validate_document_upload(_NamedUpload(filename, content_type))
        except ValidationError as exc:
            return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)

        file_id = uuid.uuid4()
        key = f'projects/{project_pk}/{file_id}/{filename}'
        stored = StoredFile.objects.create(
            id=file_id,
            project_id=project_pk,
            uploaded_by=request.user,
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
        return Response({'file_id': str(stored.id), 'upload_url': url, 's3_key': key})


class ConfirmUploadView(APIView):
    require_uploader = True
    permission_classes = [IsAuthenticated, CanAccessStoredFile]

    @extend_schema(summary='Confirm file upload', tags=['Storage'])
    def post(self, request, file_id):
        try:
            stored = StoredFile.objects.get(pk=file_id, uploaded_by=request.user)
        except StoredFile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        stored.confirmed = True
        size_bytes = request.data.get('size_bytes')
        if size_bytes is not None and int(size_bytes) > MAX_UPLOAD_BYTES:
            return Response({'detail': MSG_FILE_TOO_LARGE}, status=status.HTTP_400_BAD_REQUEST)
        stored.size_bytes = size_bytes
        stored.save(update_fields=['confirmed', 'size_bytes'])
        return Response({'id': str(stored.id), 'confirmed': True})


class DownloadUrlView(APIView):
    permission_classes = [IsAuthenticated, CanAccessStoredFile]

    @extend_schema(summary='Get presigned download URL', tags=['Storage'])
    def get(self, request, file_id):
        try:
            stored = StoredFile.objects.get(pk=file_id)
        except StoredFile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        url = s3_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': stored.s3_key},
            ExpiresIn=3600,
        )
        return Response({'download_url': url, 'filename': stored.filename})

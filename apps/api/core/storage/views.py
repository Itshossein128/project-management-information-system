import os
import uuid
import logging

import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from projects.permissions import IsProjectMember
from storage.permissions import CanAccessStoredFile
from storage.services import generate_upload_url, confirm_upload, generate_download_url

logger = logging.getLogger(__name__)


class UploadUrlView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember]

    @extend_schema(summary='Get presigned upload URL', tags=['Storage'])
    def post(self, request, project_pk):
        raw_filename = request.data.get('filename', 'file')
        content_type = request.data.get('content_type', 'application/octet-stream')

        try:
            result = generate_upload_url(project_pk, request.user, raw_filename, content_type)
            return Response(result)
        except ValueError as exc:
            logger.exception('Failed to generate upload URL')
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as exc:
            return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmUploadView(APIView):
    require_uploader = True
    permission_classes = [IsAuthenticated, CanAccessStoredFile]

    @extend_schema(summary='Confirm file upload', tags=['Storage'])
    def post(self, request, file_id):
        size_bytes = request.data.get('size_bytes')
        try:
            result = confirm_upload(file_id, request.user, size_bytes)
            return Response(result)
        except ValueError as exc:
            if str(exc) == 'Not found.':
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            logger.exception('Failed to confirm file upload')
            return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)


class DownloadUrlView(APIView):
    permission_classes = [IsAuthenticated, CanAccessStoredFile]

    @extend_schema(summary='Get presigned download URL', tags=['Storage'])
    def get(self, request, file_id):
        try:
            result = generate_download_url(file_id)
            return Response(result)
        except ValueError as exc:
            if str(exc) == 'Not found.':
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            logger.exception('Failed to generate download URL')
            return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

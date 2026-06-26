import os
import unittest
import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from master_data.models import ProjectMember
from projects.models import Project

User = get_user_model()

MINIO_CONFIGURED = bool(os.environ.get('AWS_S3_ENDPOINT_URL'))


def minio_available() -> bool:
    if not MINIO_CONFIGURED:
        return False
    try:
        client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4'),
        )
        client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        return True
    except Exception:
        return False


@unittest.skipUnless(minio_available(), 'MinIO/S3 is not available')
class StorageIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='uploader',
            password='secure-pass-123',
            mobile='09333333333',
            full_name='Uploader',
        )
        self.project = Project.objects.create(project_code='stor-001', project_name='Storage Test')
        ProjectMember.objects.create(project=self.project, user=self.user, status='active')
        login = self.client.post(
            reverse('authentication:login'),
            {'username': 'uploader', 'password': 'secure-pass-123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')

    def test_presigned_upload_round_trip(self):
        upload_response = self.client.post(
            reverse('file-upload-url', kwargs={'project_pk': self.project.id}),
            {'filename': 'test.txt', 'content_type': 'text/plain'},
            format='json',
        )
        self.assertEqual(upload_response.status_code, status.HTTP_200_OK)
        file_id = upload_response.data['file_id']
        upload_url = upload_response.data['upload_url']

        import urllib.request

        request = urllib.request.Request(
            upload_url,
            data=b'hello storage',
            method='PUT',
            headers={'Content-Type': 'text/plain'},
        )
        with urllib.request.urlopen(request) as response:
            self.assertIn(response.status, (200, 204))

        confirm = self.client.post(
            reverse('file-confirm', kwargs={'file_id': file_id}),
            {'size_bytes': 13},
            format='json',
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        self.assertTrue(confirm.data['confirmed'])

        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4'),
        )
        key = upload_response.data['s3_key']
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        self.assertEqual(obj['Body'].read(), b'hello storage')

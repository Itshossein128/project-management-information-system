import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from projects.models import Project
from master_data.models import ProjectMember
from storage.models import StoredFile
from storage.permissions import CanAccessStoredFile
from storage.services import s3_client

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='tester', password='pwd')

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='other', password='pwd')

@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(username='admin_tester', password='pwd', is_superuser=True)
    return user

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def project(db, user):
    proj = Project.objects.create(project_code="P01", project_name="Test Project")
    ProjectMember.objects.create(project=proj, user=user, status='active')
    return proj

@pytest.fixture
def stored_file(db, project, user):
    return StoredFile.objects.create(
        project=project,
        uploaded_by=user,
        s3_key="test/key",
        filename="test.txt",
        content_type="text/plain",
    )

@pytest.mark.django_db
class TestCanAccessStoredFile:
    def test_unauthenticated(self):
        permission = CanAccessStoredFile()
        request = MagicMock(user=MagicMock(is_authenticated=False))
        assert not permission.has_permission(request, MagicMock())

    def test_superuser(self, admin_user):
        permission = CanAccessStoredFile()
        request = MagicMock(user=admin_user)
        assert permission.has_permission(request, MagicMock())

    def test_admin_group(self, user):
        from django.contrib.auth.models import Group
        admin_group, _ = Group.objects.get_or_create(name='admin')
        user.groups.add(admin_group)
        permission = CanAccessStoredFile()
        request = MagicMock(user=user)
        assert permission.has_permission(request, MagicMock())

    def test_missing_file_id(self, user):
        permission = CanAccessStoredFile()
        request = MagicMock(user=user)
        view = MagicMock(kwargs={})
        assert not permission.has_permission(request, view)

    def test_file_not_found_allows_through_to_404(self, user):
        permission = CanAccessStoredFile()
        request = MagicMock(user=user)
        view = MagicMock(kwargs={'file_id': '00000000-0000-0000-0000-000000000000'})
        assert permission.has_permission(request, view)

    def test_require_uploader_rejected(self, other_user, stored_file):
        permission = CanAccessStoredFile()
        request = MagicMock(user=other_user)
        view = MagicMock(kwargs={'file_id': stored_file.pk}, require_uploader=True)
        assert not permission.has_permission(request, view)

    def test_require_uploader_accepted(self, user, stored_file):
        permission = CanAccessStoredFile()
        request = MagicMock(user=user)
        view = MagicMock(kwargs={'file_id': stored_file.pk}, require_uploader=True)
        assert permission.has_permission(request, view)

    def test_project_member_active_accepted(self, user, stored_file):
        permission = CanAccessStoredFile()
        request = MagicMock(user=user)
        view = MagicMock(kwargs={'file_id': stored_file.pk}, require_uploader=False)
        assert permission.has_permission(request, view)

    def test_not_project_member_rejected(self, other_user, stored_file):
        permission = CanAccessStoredFile()
        request = MagicMock(user=other_user)
        view = MagicMock(kwargs={'file_id': stored_file.pk}, require_uploader=False)
        assert not permission.has_permission(request, view)


@pytest.mark.django_db
class TestStorageViews:

    @patch('storage.services.boto3')
    def test_s3_client(self, mock_boto3):
        # Coverage for line 19 (s3_client)
        s3_client()
        assert mock_boto3.client.called
        assert mock_boto3.client.call_args[0][0] == 's3'

    @patch('storage.services.s3_client')
    def test_upload_url_view(self, mock_s3_client, auth_client, project):
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://fake-s3.url/upload"
        mock_s3_client.return_value = mock_s3

        url = reverse('file-upload-url', kwargs={'project_pk': project.pk})
        response = auth_client.post(url, {
            'filename': 'document.pdf',
            'content_type': 'application/pdf'
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'file_id' in response.data
        assert response.data['upload_url'] == "https://fake-s3.url/upload"

        stored = StoredFile.objects.get(pk=response.data['file_id'])
        assert stored.filename == 'document.pdf'
        assert stored.content_type == 'application/pdf'
        assert stored.uploaded_by == auth_client.handler._force_user

    def test_upload_url_view_directory_traversal(self, auth_client, project):
        url = reverse('file-upload-url', kwargs={'project_pk': project.pk})

        # Test path traversal with ..
        response = auth_client.post(url, {
            'filename': '../../../etc/passwd',
            'content_type': 'text/plain'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid filename.'

        # Test path traversal with slash
        response = auth_client.post(url, {
            'filename': '/etc/passwd',
            'content_type': 'text/plain'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid filename.'

        # Test backslash
        response = auth_client.post(url, {
            'filename': '..\\windows\\system32\\cmd.exe',
            'content_type': 'application/x-msdownload'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid filename.'

    def test_confirm_upload_view(self, auth_client, stored_file):
        url = reverse('file-confirm', kwargs={'file_id': stored_file.pk})
        response = auth_client.post(url, {'size_bytes': 1024})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['confirmed'] is True

        stored_file.refresh_from_db()
        assert stored_file.confirmed is True
        assert stored_file.size_bytes == 1024


    def test_confirm_upload_view_not_found_view_level(self, auth_client, stored_file, other_user):
        stored_file.uploaded_by = other_user
        stored_file.save()

        url = reverse('file-confirm', kwargs={'file_id': stored_file.pk})
        # This will actually fail at permission level because `CanAccessStoredFile` checks `require_uploader`
        response = auth_client.post(url, {'size_bytes': 1024})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_confirm_upload_view_not_found_in_db(self, auth_client):
        # Coverage for line 66-67
        url = reverse('file-confirm', kwargs={'file_id': '00000000-0000-0000-0000-000000000000'})
        response = auth_client.post(url, {'size_bytes': 1024})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('storage.services.s3_client')
    def test_download_url_view(self, mock_s3_client, auth_client, stored_file):
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://fake-s3.url/download"
        mock_s3_client.return_value = mock_s3

        url = reverse('file-download-url', kwargs={'file_id': stored_file.pk})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['download_url'] == "https://fake-s3.url/download"
        assert response.data['filename'] == stored_file.filename

    def test_download_url_not_found(self, auth_client):
        url = reverse('file-download-url', kwargs={'file_id': '00000000-0000-0000-0000-000000000000'})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

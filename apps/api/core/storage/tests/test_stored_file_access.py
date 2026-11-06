"""A6-P4 stored file access requires active project membership.

Presigned URL minting in ``storage.services`` calls boto3/MinIO when allowed.
Tests that hit ``generate_download_url`` mock the client so CI exercises policy
branches without requiring a live object store.
"""

from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride
from storage.models import StoredFile, StoredFileSource
from storage.permissions import CanAccessStoredFile
from storage.services import generate_download_url

User = get_user_model()


class _View:
    kwargs = {}
    require_uploader = False


def _file(project, user, name='a.txt', *, source=StoredFileSource.REPORTS):
    return StoredFile.objects.create(
        project=project,
        uploaded_by=user,
        filename=name,
        content_type='text/plain',
        size_bytes=1,
        s3_key=f'projects/{project.id}/{name}',
        confirmed=True,
        source=source,
    )


@pytest.mark.django_db
def test_admin_without_membership_cannot_access_file(project, user):
    admin = User.objects.create_user(
        username='file_admin',
        mobile='+989120000501',
        password='x',
    )
    group, _ = Group.objects.get_or_create(name='admin')
    admin.groups.add(group)
    stored = _file(project, user)
    factory = APIRequestFactory()
    request = factory.get('/x')
    request.user = admin
    view = _View()
    view.kwargs = {'file_id': str(stored.id)}
    assert CanAccessStoredFile().has_permission(request, view) is False


@pytest.mark.django_db
def test_active_member_can_access_file(project, user):
    stored = _file(project, user, 'b.txt')
    factory = APIRequestFactory()
    request = factory.get('/x')
    request.user = user
    view = _View()
    view.kwargs = {'file_id': str(stored.id)}
    assert CanAccessStoredFile().has_permission(request, view) is True


@pytest.mark.django_db
def test_inactive_member_cannot_access_file(project, user):
    member = ProjectMember.objects.get(project=project, user=user)
    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    stored = _file(project, user, 'c.txt')
    factory = APIRequestFactory()
    request = factory.get('/x')
    request.user = user
    view = _View()
    view.kwargs = {'file_id': str(stored.id)}
    assert CanAccessStoredFile().has_permission(request, view) is False


@pytest.mark.django_db
def test_download_url_refuses_without_view_documents(project, user, monkeypatch):
    """Active member without ``view_documents``: no presign (policy branch; MinIO not called)."""
    stored = _file(project, user, 'no-doc.txt', source=StoredFileSource.DOCUMENTS)
    ProjectMemberPermissionOverride.objects.filter(member__project=project, member__user=user).delete()
    membership = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberPermissionOverride.objects.create(
        member=membership,
        permission_codename='view_documents',
        is_granted=False,
    )
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = 'https://example/signed'
    monkeypatch.setattr('storage.services.s3_client', lambda: mock_client)
    with pytest.raises(ValueError, match='Forbidden'):
        generate_download_url(stored.id, user=user)
    mock_client.generate_presigned_url.assert_not_called()


@pytest.mark.django_db
def test_download_url_allows_with_view_documents(project, user, monkeypatch):
    stored = _file(project, user, 'ok.txt', source=StoredFileSource.DOCUMENTS)
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = 'https://example/signed'
    monkeypatch.setattr('storage.services.s3_client', lambda: mock_client)
    out = generate_download_url(stored.id, user=user)
    assert out['download_url'] == 'https://example/signed'
    mock_client.generate_presigned_url.assert_called_once()

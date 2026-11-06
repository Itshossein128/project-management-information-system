from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from documents.models import AccessLevel, Correspondence, MeetingMinutes, ProjectDocument
from documents.serializers import (
    CorrespondenceSerializer,
    DocumentRevisionSerializer,
    MeetingMinutesSerializer,
    ProjectDocumentSerializer,
)
from documents.services.correspondence_service import respond_to_correspondence
from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride


@pytest.mark.parametrize('serializer_class', [CorrespondenceSerializer, MeetingMinutesSerializer])
@pytest.mark.parametrize('value', ['documents/another-project/private.pdf', 'javascript:alert(1)', '//storage.test/private'])
def test_attachment_cannot_accept_private_storage_key(serializer_class, value):
    serializer = serializer_class(data={'file_url': value}, partial=True)
    assert not serializer.is_valid()
    assert 'file_url' in serializer.errors


@pytest.mark.django_db
@pytest.mark.parametrize('model,serializer_class', [
    (Correspondence, CorrespondenceSerializer), (MeetingMinutes, MeetingMinutesSerializer),
])
@pytest.mark.parametrize('value', [
    'documents/another-project/private.pdf',
    'https://storage.example.test/bucket/documents/private.pdf?old-signature=expired',
])
def test_untrusted_persisted_attachment_is_never_signed(model, serializer_class, value, settings):
    settings.AWS_STORAGE_BUCKET_NAME = 'bucket'
    instance = model(file_url=value)
    with patch('documents.services.upload_service._s3_client') as client:
        result = serializer_class(instance).data
    client.assert_not_called()
    assert result['file_url'] == (value if value.startswith('https://') else '')


@pytest.mark.django_db
def test_correspondence_response_rejects_private_key_before_mutation(project, user):
    corr = Correspondence.objects.create(
        project=project, corr_number='SEC-1', corr_type='incoming', subject='Test',
        from_party='A', to_party='B', corr_date=date.today(),
        created_by=user, updated_by=user,
    )
    with pytest.raises(ValidationError):
        respond_to_correspondence(corr, {'file_url': 'documents/other/secret.pdf'}, user)
    corr.refresh_from_db()
    assert corr.status == 'open'
    assert corr.file_url == ''


def _drf_request(user):
    factory = RequestFactory()
    req = factory.get('/')
    req.user = user
    return Request(req)


@pytest.mark.django_db
def test_project_document_no_presign_without_view_documents(project, user, monkeypatch):
    """Policy-only: without ``view_documents``, do not call MinIO presign."""
    doc = ProjectDocument.objects.create(
        project=project,
        title='T',
        file_url='documents/x/y.pdf',
        uploaded_by=user,
        created_by=user,
        updated_by=user,
    )
    membership = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberPermissionOverride.objects.update_or_create(
        member=membership,
        permission_codename='view_documents',
        defaults={'is_granted': False},
    )
    mock_presign = MagicMock(return_value='https://signed.example/o')
    monkeypatch.setattr('documents.file_access.presign_get_url', mock_presign)
    data = ProjectDocumentSerializer(doc, context={'request': _drf_request(user)}).data
    assert data['file_url'] == ''
    mock_presign.assert_not_called()


@pytest.mark.django_db
def test_revision_no_presign_for_restricted_without_allowlist(project, user, other_user):
    """RESTRICTED doc: non-uploader not on allowlist gets empty URL (no presign)."""
    from documents.models import DocumentRevision

    doc = ProjectDocument.objects.create(
        project=project,
        title='R',
        access_level=AccessLevel.RESTRICTED,
        file_url='documents/r/1.pdf',
        uploaded_by=user,
        created_by=user,
        updated_by=user,
    )
    rev = DocumentRevision.objects.create(
        document=doc,
        revision_label='A',
        revision_date=date.today(),
        file_url='documents/r/1.pdf',
        uploaded_by=user,
    )
    ProjectMember.objects.get_or_create(
        project=project,
        user=other_user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    data = DocumentRevisionSerializer(rev, context={'request': _drf_request(other_user)}).data
    assert data['file_url'] == ''


@pytest.mark.django_db
def test_cross_project_document_no_presign(user, other_user, monkeypatch):
    """Serializer redacts when user is not an active member of the document's project."""
    from projects.services import create_project_with_creator

    p_b = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-B',
        project_name='Project B',
        employer='X',
        start_date='2024-01-01',
    )
    doc = ProjectDocument.objects.create(
        project=p_b,
        title='B-only',
        file_url='documents/b/only.pdf',
        uploaded_by=other_user,
        created_by=other_user,
        updated_by=other_user,
    )
    mock_presign = MagicMock(return_value='https://signed.example/o')
    monkeypatch.setattr('documents.file_access.presign_get_url', mock_presign)
    data = ProjectDocumentSerializer(doc, context={'request': _drf_request(user)}).data
    assert data['file_url'] == ''
    mock_presign.assert_not_called()


@pytest.mark.parametrize('serializer_class', [CorrespondenceSerializer, MeetingMinutesSerializer])
def test_external_attachment_url_remains_supported(serializer_class):
    value = 'https://example.com/attachment.pdf'
    serializer = serializer_class(data={'file_url': value}, partial=True)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['file_url'] == value


@pytest.mark.django_db
@pytest.mark.parametrize('resource,payload', [
    ('correspondence', {'corr_type': 'incoming', 'subject': 'Test', 'from_party': 'A',
                        'to_party': 'B', 'corr_date': '2026-10-22'}),
    ('meetings', {'meeting_type': 'other', 'meeting_date': '2026-10-22', 'topic': 'Test'}),
])
def test_attachment_create_endpoint_rejects_key(auth_client, project, resource, payload):
    with patch('documents.services.upload_service._s3_client') as client:
        response = auth_client.post(f'/api/v1/projects/{project.pk}/{resource}/', {
            **payload, 'file_url': 'documents/other-project/private.pdf',
        }, format='json')
    assert response.status_code == 400, response.data
    client.assert_not_called()


@pytest.mark.django_db
def test_response_endpoint_rejects_key(auth_client, project, user):
    corr = Correspondence.objects.create(
        project=project, corr_number='SEC-2', corr_type='incoming', subject='Test',
        from_party='A', to_party='B', corr_date=date.today(), created_by=user, updated_by=user,
    )
    with patch('documents.services.upload_service._s3_client') as client:
        response = auth_client.post(
            f'/api/v1/projects/{project.pk}/correspondence/{corr.pk}/respond/',
            {'file_url': 'documents/other-project/private.pdf'}, format='json',
        )
    assert response.status_code == 400, response.data
    client.assert_not_called()
    corr.refresh_from_db()
    assert corr.status == 'open'

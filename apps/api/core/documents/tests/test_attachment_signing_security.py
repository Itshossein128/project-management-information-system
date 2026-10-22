from datetime import date
from unittest.mock import patch

import pytest
from rest_framework.exceptions import ValidationError

from documents.models import Correspondence, MeetingMinutes
from documents.serializers import CorrespondenceSerializer, MeetingMinutesSerializer
from documents.services.correspondence_service import respond_to_correspondence


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

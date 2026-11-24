from datetime import date
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, UnitReportAttachment
from sub_reports.services.attachments import MAX_BYTES


@pytest.fixture
def activity_attachment_url(project, user):
    report = DisciplineSubReport.objects.create(
        project=project, unit='buildings', discipline='civil', report_date=date(2026, 8, 3), created_by=user,
    )
    activity = DisciplineSubReportActivity.objects.create(
        sub_report=report, row_number=1, shift='shift_1', activity_description='Attachment evidence',
    )
    return activity, f'/api/v1/projects/{project.pk}/units/buildings/daily-reports/{report.pk}/attachments/'


@pytest.mark.django_db
@pytest.mark.parametrize('image_format,mime_type', [('PNG', 'image/png'), ('JPEG', 'image/jpeg')])
def test_b03_attachment_validates_stores_and_authorizes_download(
    auth_client, api_client, other_user, activity_attachment_url, image_format, mime_type, monkeypatch,
):
    from storage import services

    class TestStorage:
        def put_object(self, **kwargs):
            assert kwargs['Body'] == contents
            assert kwargs['ContentType'] == mime_type

        def generate_presigned_url(self, operation, **kwargs):
            assert operation == 'get_object'
            return 'https://example.test/temporary-download'

    monkeypatch.setattr(services, 's3_client', TestStorage)
    activity, url = activity_attachment_url
    output = BytesIO()
    Image.new('RGB', (2, 2)).save(output, format=image_format)
    contents = output.getvalue()
    result = auth_client.post(url, {
        'row_id': activity.pk, 'file': SimpleUploadedFile('photo', contents, content_type=mime_type),
    }, format='multipart')
    assert result.status_code == 201
    attachment = UnitReportAttachment.objects.get(pk=result.data['id'])
    assert attachment.uploaded_at is not None
    items = auth_client.get(url).data
    assert items[0]['uploaded_at']
    download = items[0]['download_href']
    assert auth_client.get(download).data['download_url'] == 'https://example.test/temporary-download'
    api_client.force_authenticate(other_user)
    assert api_client.get(download).status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize('content,mime_type', [
    pytest.param(b'spoofed', 'image/jpeg', id='spoofed'),
    pytest.param(b'\x89PNG\r\n\x1a\ntruncated', 'image/png', id='corrupt-png'),
    pytest.param(b'PK\x03\x04ZIP', 'image/png', id='zip'),
    pytest.param(b'MZexe', 'image/jpeg', id='exe'),
    pytest.param(b'x', 'application/json', id='unsupported-mime'),
    pytest.param(b'x' * (MAX_BYTES + 1), 'image/png', id='oversized'),
])
def test_b03_rejects_spoofed_corrupt_and_oversized_files(auth_client, activity_attachment_url, content, mime_type):
    activity, url = activity_attachment_url
    response = auth_client.post(url, {
        'row_id': activity.pk, 'file': SimpleUploadedFile('photo', content, content_type=mime_type),
    }, format='multipart')
    assert response.status_code == 422
    assert not UnitReportAttachment.objects.exists()


@pytest.mark.django_db
def test_b03_accepts_exact_limit_report_attachment(auth_client, activity_attachment_url, monkeypatch):
    from unittest.mock import Mock

    from PIL.PngImagePlugin import PngInfo
    from storage import services

    image = Image.new('RGB', (2, 2))
    metadata = PngInfo()
    metadata.add_text('test', '')
    overhead = BytesIO()
    image.save(overhead, format='PNG', pnginfo=metadata)
    metadata = PngInfo()
    metadata.add_text('test', 'x' * (MAX_BYTES - overhead.tell()))
    data = BytesIO()
    image.save(data, format='PNG', pnginfo=metadata)
    assert data.tell() == MAX_BYTES
    monkeypatch.setattr(services, 's3_client', Mock())

    activity, url = activity_attachment_url
    response = auth_client.post(url, {
        'row_kind': 'report', 'file': SimpleUploadedFile('photo.png', data.getvalue(), content_type='image/png'),
    }, format='multipart')
    assert response.status_code == 201
    stored = UnitReportAttachment.objects.get(pk=response.data['id'])
    assert stored.row_kind == 'report' and stored.row_id == str(activity.sub_report_id)
    assert stored.size_bytes == MAX_BYTES

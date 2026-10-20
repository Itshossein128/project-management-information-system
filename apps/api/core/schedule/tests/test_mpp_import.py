"""Native MPP import API and integration tests."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from schedule.tests.test_msp_import import SAMPLE_MSP_XML

FIXTURES = Path(__file__).parent / 'fixtures' / 'mpp'
OLE = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'


@pytest.fixture
def mpp_bytes():
    path = FIXTURES / 'duration-test9.mpp'
    if not path.is_file():
        pytest.skip('mpp fixture missing')
    return path.read_bytes()


@pytest.mark.django_db
class TestMppImportApi:
    def test_preview_mpp_success(self, auth_client, project, mpp_bytes):
        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        upload = SimpleUploadedFile('schedule.mpp', mpp_bytes, content_type='application/octet-stream')
        response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 200, response.data
        assert 'wbs_tree' in response.data
        assert 'activities' in response.data
        assert 'warnings' in response.data

    def test_preview_mocked_convert(self, auth_client, project):
        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        fake = OLE + b'fake-mpp-body'
        upload = SimpleUploadedFile('fake.mpp', fake, content_type='application/octet-stream')
        with patch(
            'schedule.services.mpp_convert.convert_mpp_to_mspdi',
            return_value=SAMPLE_MSP_XML,
        ):
            response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 200
        assert len(response.data['activities']) >= 1

    def test_start_and_status_mpp(self, auth_client, project, mpp_bytes, settings):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        url = f'/api/v1/projects/{project.id}/import/msp/'
        upload = SimpleUploadedFile('schedule.mpp', mpp_bytes, content_type='application/octet-stream')
        response = auth_client.post(url, {'file': upload, 'replace': 'true'}, format='multipart')
        assert response.status_code == 202, response.data
        task_id = response.data['task_id']
        status_url = f'/api/v1/projects/{project.id}/import/msp/status/{task_id}/'
        status_resp = auth_client.get(status_url)
        assert status_resp.status_code == 200
        assert status_resp.data['status'] in ('done', 'failed', 'running', 'pending')
        if status_resp.data['status'] == 'done':
            assert 'wbs_nodes_created' in status_resp.data['result']
            assert 'activities_created' in status_resp.data['result']
            assert 'relations_created' in status_resp.data['result']

    def test_reject_renamed_non_mpp(self, auth_client, project):
        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        data = (FIXTURES / 'renamed-not-mpp.mpp').read_bytes()
        upload = SimpleUploadedFile('bad.mpp', data, content_type='application/octet-stream')
        response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'invalid_file_type'

    def test_reject_password_protected(self, auth_client, project):
        path = FIXTURES / 'password-protected.mpp'
        if not path.is_file():
            pytest.skip('fixture missing')
        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        upload = SimpleUploadedFile('pw.mpp', path.read_bytes(), content_type='application/octet-stream')
        response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'mpp_password_protected'

    def test_reject_oversized_maps_error_code(self, auth_client, project):
        """Size enforcement is unit-tested on validators; here we assert API maps ValidationError."""
        from rest_framework.exceptions import ValidationError
        from common.validators import MSG_FILE_TOO_LARGE

        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        upload = SimpleUploadedFile('big.mpp', OLE + b'x', content_type='application/octet-stream')
        with patch(
            'schedule.views.validate_msp_upload',
            side_effect=ValidationError({'file': MSG_FILE_TOO_LARGE}),
        ):
            response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'file_too_large'

    def test_without_edit_wbs_forbidden(self, auth_client, project, user, mpp_bytes):
        from permissions.services import set_permission_override

        member = project.members.get(user=user)
        set_permission_override(member, 'edit_wbs', False)
        url = f'/api/v1/projects/{project.id}/import/msp/preview/'
        upload = SimpleUploadedFile('schedule.mpp', mpp_bytes, content_type='application/octet-stream')
        response = auth_client.post(url, {'file': upload}, format='multipart')
        assert response.status_code == 403

    def test_cross_project_status_denied(self, auth_client, project, user, mpp_bytes, other_user):
        from projects.services import create_project_with_creator
        from schedule.models import MspImportJob

        other = create_project_with_creator(
            creator=other_user,
            project_code='OTH-MPP',
            project_name='Other Project',
            employer='Other Co',
            start_date='2024-01-01',
        )
        job = MspImportJob.objects.create(
            project=project,
            filename='x.mpp',
            file_data=mpp_bytes,
            created_by=user,
        )
        # Authenticated as user (member of `project` only): poll job under other project
        status_url = f'/api/v1/projects/{other.id}/import/msp/status/{job.id}/'
        response = auth_client.get(status_url)
        assert response.status_code in (403, 404)

    def test_append_preserves_existing(self, auth_client, project, user, wbs, settings):
        from projects.models import Activity, WBS

        settings.CELERY_TASK_ALWAYS_EAGER = True
        Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='KEEP-1',
            activity_name='Keep me',
            created_by=user,
            updated_by=user,
        )
        before = WBS.objects.filter(project=project).count()
        fake = OLE + b'body'
        upload = SimpleUploadedFile('a.mpp', fake, content_type='application/octet-stream')
        with patch('schedule.services.mpp_convert.convert_mpp_to_mspdi', return_value=SAMPLE_MSP_XML):
            response = auth_client.post(
                f'/api/v1/projects/{project.id}/import/msp/',
                {'file': upload, 'replace': 'false'},
                format='multipart',
            )
        assert response.status_code == 202, response.data
        assert Activity.objects.filter(project=project, activity_code='KEEP-1').exists()
        assert WBS.objects.filter(project=project).count() >= before

    def test_failed_convert_no_partial_mutation(self, auth_client, project, wbs):
        from projects.models import Activity, WBS
        from schedule.services.mpp_errors import MPP_CORRUPT, MppImportError

        act_before = Activity.objects.filter(project=project).count()
        wbs_before = WBS.objects.filter(project=project).count()
        fake = OLE + b'body'
        upload = SimpleUploadedFile('bad.mpp', fake, content_type='application/octet-stream')
        with patch(
            'schedule.services.mpp_convert.convert_mpp_to_mspdi',
            side_effect=MppImportError(MPP_CORRUPT, 'corrupt'),
        ):
            response = auth_client.post(
                f'/api/v1/projects/{project.id}/import/msp/preview/',
                {'file': upload},
                format='multipart',
            )
        assert response.status_code == 400
        assert response.data['error']['code'] == MPP_CORRUPT
        assert Activity.objects.filter(project=project).count() == act_before
        assert WBS.objects.filter(project=project).count() == wbs_before

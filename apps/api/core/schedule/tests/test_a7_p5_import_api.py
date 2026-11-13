"""Existing import routes keep their admission and error behavior."""

from __future__ import annotations

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import MspImportJob, MspImportStatus
from schedule.services.import_process import acquire_slot, release_slot
from schedule.services.import_safety import file_sha256
from schedule.tests.test_msp_import import SAMPLE_MSP_XML


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P5-API-{suffix}',
        project_name=f'P5 api {suffix}',
        employer='P5',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


@pytest.fixture
def client(user):
    api = APIClient()
    api.force_authenticate(user=user)
    return api


@pytest.mark.django_db
def test_preview_writes_nothing_and_invalid_start_has_no_job(client, user):
    project = _project(user, 'PREVIEW')
    preview = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')},
        format='multipart',
    )
    assert preview.status_code == 200
    assert preview.data['recognized_kind'] == 'xml'
    assert MspImportJob.objects.filter(project=project).count() == 0
    rejected = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': SimpleUploadedFile('bad.xml', b'<not-project/>', content_type='application/xml'), 'replace': 'false'},
        format='multipart',
    )
    assert rejected.status_code == 400
    assert MspImportJob.objects.filter(project=project).count() == 0


@pytest.mark.django_db
def test_inflight_match_precedes_a_full_slot(client, user, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    project = _project(user, 'SLOT')
    digest = file_sha256(SAMPLE_MSP_XML)
    existing = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        replace_existing=False,
        created_by=user,
        status=MspImportStatus.PENDING,
        source_sha256=digest,
        source_size=len(SAMPLE_MSP_XML),
        dispatch_deadline_at=timezone.now() + timedelta(minutes=5),
    )
    token = acquire_slot(family='preview', subject_id=existing.id, deadline=timezone.now() + timedelta(minutes=1))
    try:
        matched = client.post(
            f'/api/v1/projects/{project.id}/import/msp/',
            {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'), 'replace': 'false'},
            format='multipart',
        )
        assert matched.status_code == 202
        assert matched.data['task_id'] == str(existing.id)
        other = client.post(
            f'/api/v1/projects/{project.id}/import/msp/',
            {'file': SimpleUploadedFile('other.xml', SAMPLE_MSP_XML.replace(b'Phase 1', b'Phase 9'), content_type='application/xml'), 'replace': 'false'},
            format='multipart',
        )
        assert other.status_code == 503
        assert other.data['error']['code'] == 'processing_busy'
        assert MspImportJob.objects.filter(project=project).count() == 1
    finally:
        release_slot(token)


@pytest.mark.django_db
def test_retry_requires_a_visible_failed_predecessor(client, user, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    project = _project(user, 'RETRY')
    missing = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {
            'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'),
            'replace': 'false',
            'intent': 'retry',
        },
        format='multipart',
    )
    assert missing.status_code == 400
    assert MspImportJob.objects.filter(project=project).count() == 0
    failed = MspImportJob.objects.create(
        project=project, filename='old.xml', file_data=b'old', status=MspImportStatus.FAILED,
        created_by=user, error_code='import_failed', error_message='failed',
    )
    started = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {
            'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'),
            'replace': 'false',
            'intent': 'retry',
            'retry_of': str(failed.id),
        },
        format='multipart',
    )
    assert started.status_code == 202
    retry = MspImportJob.objects.get(pk=started.data['task_id'])
    assert retry.retry_of_id == failed.id
    assert retry.id != failed.id
    fresh = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {
            'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'),
            'replace': 'false',
            'intent': 'new',
            'retry_of': str(failed.id),
        },
        format='multipart',
    )
    assert fresh.status_code == 400

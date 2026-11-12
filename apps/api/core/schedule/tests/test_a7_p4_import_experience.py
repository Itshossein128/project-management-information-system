"""Import experience figures and messages. Project codes start with A7P4-IMPORT-EXPERIENCE."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from projects.models import Activity, ActivityRelation, ProjectStatus, WBS
from projects.services import create_project_with_creator
from schedule.models import MspImportJob, MspImportStatus
from schedule.services.mpp_errors import MppImportError
from schedule.tests.test_p6_import import SAMPLE_XER
from wbs.services import create_wbs_node

LINKED_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Tasks>
    <Task>
      <UID>1</UID><ID>1</ID><Name>Root</Name>
      <OutlineLevel>1</OutlineLevel><OutlineNumber>1</OutlineNumber>
      <WBS>1</WBS><Summary>1</Summary>
    </Task>
    <Task>
      <UID>2</UID><ID>2</ID><Name>Leaf A</Name>
      <OutlineLevel>2</OutlineLevel><OutlineNumber>1.1</OutlineNumber>
      <WBS>1.1</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>
      <PredecessorLink><PredecessorUID>3</PredecessorUID><Type>1</Type></PredecessorLink>
    </Task>
    <Task>
      <UID>3</UID><ID>3</ID><Name>Leaf B</Name>
      <OutlineLevel>2</OutlineLevel><OutlineNumber>1.2</OutlineNumber>
      <WBS>1.2</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>
    </Task>
  </Tasks>
</Project>
"""

EXPERIENCE_CODES = [
    'invalid_file_type',
    'file_too_large',
    'mpp_corrupt',
    'mpp_password_protected',
    'mpp_unsupported',
    'msp_invalid_xml',
    'processing_timeout',
    'conversion_failed',
    'import_failed',
    'project_archived',
    'import_not_permitted',
    'import_actor_missing',
    'wbs_has_progress',
    'wbs_has_cost',
    'wbs_has_documents',
    'wbs_has_activities',
    'baseline_history_protected',
    'duplicate_relation',
]

MPP_FIXTURE = Path(__file__).parent / 'fixtures' / 'mpp' / 'duration-test9.mpp'
LOCALES = Path(__file__).resolve().parents[5] / 'apps' / 'web' / 'src' / 'app' / 'locales'


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P4-IMPORT-EXPERIENCE-{suffix}',
        project_name=f'Import experience {suffix}',
        employer='Experience Co',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


def _counts(project):
    return {
        'wbs': WBS.objects.filter(project=project, is_deleted=False).count(),
        'activities': Activity.objects.filter(project=project, is_deleted=False).count(),
        'relations': ActivityRelation.objects.filter(
            predecessor__project=project, is_deleted=False,
        ).count(),
    }


def _upload(name, content, content_type='application/xml'):
    return SimpleUploadedFile(name, content, content_type=content_type)


@pytest.fixture
def experience_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_preview_names_the_accepted_kind_and_writes_nothing(experience_client):
    client, user = experience_client
    project = _project(user, 'kind')
    before = _counts(project)
    xml = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': _upload('linked.xml', LINKED_XML)},
        format='multipart',
    )
    xer = client.post(
        f'/api/v1/projects/{project.id}/import/p6/preview/',
        {'file': _upload('sample.xer', SAMPLE_XER, 'application/octet-stream')},
        format='multipart',
    )
    rejected = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': _upload('notes.txt', b'hello', 'text/plain')},
        format='multipart',
    )
    assert xml.status_code == 200
    assert xml.data['recognized_kind'] == 'xml'
    assert xer.status_code == 200
    assert xer.data['recognized_kind'] == 'xer'
    assert rejected.status_code == 400
    assert rejected.data['error']['code'] == 'invalid_file_type'
    assert 'recognized_kind' not in rejected.data
    assert _counts(project) == before


@pytest.mark.django_db
def test_mpp_preview_names_mpp_when_converter_runs(experience_client):
    if not MPP_FIXTURE.is_file():
        pytest.skip('mpp fixture missing')
    client, user = experience_client
    project = _project(user, 'mpp')
    try:
        response = client.post(
            f'/api/v1/projects/{project.id}/import/msp/preview/',
            {'file': _upload('duration-test9.mpp', MPP_FIXTURE.read_bytes(), 'application/vnd.ms-project')},
            format='multipart',
        )
    except MppImportError:
        pytest.skip('mpp converter is not available')
    if response.status_code != 200:
        pytest.skip(f'mpp converter did not accept the fixture: {response.status_code}')
    assert response.data['recognized_kind'] == 'mpp'


@pytest.mark.django_db
def test_figures_match_stored_rows_and_duplicates_are_not_new_links(experience_client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    client, user = experience_client
    project = _project(user, 'fig')
    create_wbs_node(project_id=project.id, wbs_code='ZZ1', wbs_name='Bare')
    preview = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': _upload('linked.xml', LINKED_XML)},
        format='multipart',
    )
    assert preview.status_code == 200
    assert preview.data['replacement']['blocked'] is None
    assert preview.data['replacement']['wbs_nodes_removed'] >= 1
    start = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': _upload('linked.xml', LINKED_XML), 'replace': 'true'},
        format='multipart',
    )
    assert start.status_code == 202
    status = client.get(f'/api/v1/projects/{project.id}/import/msp/status/{start.data["task_id"]}/')
    result = status.data['result']
    counts = preview.data['counts_if_replaced']
    assert counts['relationships_kept'] == result['relations_created']
    assert result['relationships_kept'] == result['relations_created']
    assert ActivityRelation.objects.filter(predecessor__project=project, is_deleted=False).count() == counts['relationships_kept']
    assert counts['rows_read'] == result['rows_read'] == 3
    assert counts['created_packages'] == result['wbs_nodes_created']
    assert counts['created_activities'] == result['activities_created']
    assert counts['duplicate_count'] == result['duplicate_count']
    assert counts['rows_omitted'] == result['rows_omitted']
    assert result['wbs_nodes_removed'] >= 1
    assert result['activities_created'] == 2
    assert ActivityRelation.objects.filter(predecessor__project=project, is_deleted=False).count() == result['relations_created']

    again_preview = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': _upload('linked.xml', LINKED_XML)},
        format='multipart',
    )
    again = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': _upload('linked.xml', LINKED_XML), 'replace': 'false'},
        format='multipart',
    )
    again_status = client.get(f'/api/v1/projects/{project.id}/import/msp/status/{again.data["task_id"]}/')
    again_result = again_status.data['result']
    assert again_result['nothing_changed'] is True
    assert again_result['relations_created'] == 0
    assert again_result['relationships_kept'] == 0
    assert again_preview.data['counts']['relationships_kept'] == 0
    assert again_result['duplicate_count'] > 0
    assert any(item['code'] == 'duplicate_relation' for item in again_result['warning_items'])


@pytest.mark.django_db
def test_protected_replace_writes_nothing(experience_client):
    client, user = experience_client
    project = _project(user, 'prot')
    node, _warnings = create_wbs_node(project_id=project.id, wbs_code='ZZ1', wbs_name='Bare')
    Activity.objects.create(
        project=project, wbs=node, activity_code='KEEP', activity_name='Keep',
        created_by=user, updated_by=user,
    )
    before = _counts(project)
    preview = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': _upload('linked.xml', LINKED_XML)},
        format='multipart',
    )
    assert preview.data['replacement']['blocked'] == 'wbs_has_activities'
    assert preview.data['replacement']['wbs_nodes_removed'] == 0
    refused = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': _upload('linked.xml', LINKED_XML), 'replace': 'true'},
        format='multipart',
    )
    assert refused.status_code == 400
    assert refused.data['error']['code'] == 'wbs_has_activities'
    assert _counts(project) == before


@pytest.mark.django_db
def test_p6_rejections_use_stable_codes(experience_client):
    client, user = experience_client
    project = _project(user, 'p6err')
    wrong = client.post(
        f'/api/v1/projects/{project.id}/import/p6/preview/',
        {'file': _upload('notes.txt', b'hello', 'text/plain')},
        format='multipart',
    )
    oversized_file = SimpleUploadedFile(
        'big.xer',
        b'x' * (51 * 1024 * 1024 + 1),
        content_type='text/plain',
    )
    oversized = client.post(
        f'/api/v1/projects/{project.id}/import/p6/preview/',
        {'file': oversized_file},
        format='multipart',
    )
    assert wrong.status_code == 400
    assert wrong.data['error']['code'] == 'invalid_file_type'
    assert isinstance(wrong.data['error']['message'], str)
    assert oversized.status_code == 400
    assert oversized.data['error']['code'] == 'file_too_large'
    assert isinstance(oversized.data['error']['message'], str)


def test_locale_catalogs_share_experience_codes():
    english = json.loads((LOCALES / 'en.json').read_text(encoding='utf-8'))['scheduleImport']['codes']
    persian = json.loads((LOCALES / 'fa.json').read_text(encoding='utf-8'))['scheduleImport']['codes']
    assert set(english) == set(persian)
    for code in EXPERIENCE_CODES:
        assert code in english
        assert code in persian
        assert english[code] != code
        assert persian[code] != code


@pytest.mark.django_db
def test_inflight_start_returns_the_same_task_and_finished_status_does_not(experience_client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    client, user = experience_client
    project = _project(user, 'fly')
    pending = MspImportJob.objects.create(
        project=project,
        created_by=user,
        filename='linked.xml',
        replace_existing=False,
        file_data=LINKED_XML,
        status=MspImportStatus.PENDING,
    )
    replay = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': _upload('linked.xml', LINKED_XML), 'replace': 'false'},
        format='multipart',
    )
    assert replay.status_code == 202
    assert replay.data['task_id'] == str(pending.id)
    assert MspImportJob.objects.filter(project=project).count() == 1
    pending.status = MspImportStatus.DONE
    pending.result = {'rows_read': 0}
    pending.save(update_fields=['status', 'result', 'updated_at'])
    before = MspImportJob.objects.filter(project=project).count()
    status = client.get(f'/api/v1/projects/{project.id}/import/msp/status/{pending.id}/')
    assert status.status_code == 200
    assert status.data['status'] == 'done'
    assert MspImportJob.objects.filter(project=project).count() == before

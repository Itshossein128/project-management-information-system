"""NEG-01: duplicate codes are rejected without changing existing records."""
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from projects.models import Activity, ActivityRelation, Project, WBS
from schedule.models import BaselineSchedule
from schedule.services.import_fidelity import ImportFidelityError
from schedule.services.msp_import import execute_msp_import
from schedule.services.p6_import import execute_p6_import
from wbs.services import create_wbs_node

FIXTURES = Path(__file__).resolve().parents[5] / 'specs/051-a7-p1-project-reference/evidence/fixtures'


def snapshot(project):
    return {
        'wbs': list(WBS.objects.filter(project=project).order_by('pk').values()),
        'activities': list(Activity.objects.filter(project=project).order_by('pk').values()),
        'relations': list(ActivityRelation.objects.filter(successor__project=project).order_by('pk').values()),
        'baselines': list(BaselineSchedule.objects.filter(project=project).order_by('pk').values()),
    }


@pytest.mark.django_db
def test_manual_duplicate_codes_do_not_create_project_or_wbs(auth_client, project):
    before_projects = list(Project.objects.order_by('pk').values())
    response = auth_client.post('/api/v1/projects/', {
        'project_code': f'  {project.project_code}  ', 'project_name': 'Duplicate',
        'employer': 'Employer', 'start_date': '2026-01-01',
    }, format='json')
    assert response.status_code == 400
    assert response.data['error']['code'] == 'unique'
    assert 'project_code' in response.data['error']['details']
    assert list(Project.objects.order_by('pk').values()) == before_projects

    create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Existing')
    before = snapshot(project)
    response = auth_client.post(f'/api/v1/projects/{project.id}/wbs/',
        {'wbs_code': ' 1 ', 'wbs_name': 'Duplicate'}, format='json')
    assert response.status_code == 400
    assert response.data['error']['code'] == 'duplicate_wbs_code'
    assert snapshot(project) == before


@pytest.mark.django_db
@pytest.mark.parametrize('family,filename,payload,runner', [
    ('msp', 'duplicate.xml', (FIXTURES / 'branch.xml').read_bytes().replace(b'<WBS>1.2</WBS>', b'<WBS> 1.1 </WBS>'), execute_msp_import),
    ('p6', 'duplicate.xer', (FIXTURES / 'branch.xer').read_bytes().replace(b'%R\t3\t1\t1.2\tBranch B', b'%R\t3\t1\t 1.1 \tBranch B'), execute_p6_import),
    ('p6', 'duplicate.xer', (FIXTURES / 'branch.xer').read_bytes().replace(b'%R\t11\t3\tB\tBranch B work', b'%R\t11\t3\t A \tBranch B work'), execute_p6_import),
])
def test_import_duplicate_normalized_codes_blocks_preview_and_both_write_modes(auth_client, project, user, family, filename, payload, runner, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    create_wbs_node(project_id=project.id, wbs_code='KEEP', wbs_name='Existing')
    before = snapshot(project)
    response = auth_client.post(f'/api/v1/projects/{project.id}/import/{family}/preview/',
        {'file': SimpleUploadedFile(filename, payload)}, format='multipart')
    assert response.status_code == 200, response.data
    assert any(note['code'] == 'duplicate_in_file' and note['row'] for note in response.data['blocking'])
    assert snapshot(project) == before
    for replace in (False, True):
        with pytest.raises(ImportFidelityError) as exc:
            runner(project, payload, filename=filename, replace=replace, user=user)
        assert exc.value.code == 'duplicate_in_file'
        assert snapshot(project) == before
        start = auth_client.post(f'/api/v1/projects/{project.id}/import/{family}/',
            {'file': SimpleUploadedFile(filename, payload), 'replace': str(replace).lower()}, format='multipart')
        assert start.status_code == 202, start.data
        status = auth_client.get(f'/api/v1/projects/{project.id}/import/{family}/status/{start.data["task_id"]}/')
        assert status.status_code == 200, status.data
        assert status.data['status'] == 'failed'
        assert status.data['error_code'] == 'duplicate_in_file'
        assert any(note['code'] == 'duplicate_in_file' and note['row'] for note in status.data['blocking'])
        assert snapshot(project) == before


@pytest.mark.django_db
@pytest.mark.parametrize('filename,runner', [('branch.xml', execute_msp_import), ('branch.xer', execute_p6_import)])
def test_repeated_valid_append_does_not_create_duplicates(project, user, filename, runner):
    payload = (FIXTURES / filename).read_bytes()
    runner(project, payload, filename=filename, replace=False, user=user)
    before = snapshot(project)
    repeated = payload
    if filename.endswith('.xer'):
        repeated = payload.replace(b'%R\t2\t1\t1.1\tBranch A', b'%R\t2\t1\t 1.1 \tBranch A')
    result = runner(project, repeated, filename=filename, replace=False, user=user)
    assert result['nothing_changed'] is True
    assert snapshot(project) == before

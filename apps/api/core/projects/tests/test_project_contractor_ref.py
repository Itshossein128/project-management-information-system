"""TDD: project.contractor_ref snapshots name (027 US3)."""

import pytest

from projects.tests.contractor_select_helpers import make_active_contractor


@pytest.mark.django_db
def test_project_patch_contractor_ref_snapshots_name(auth_client, project, user):
    contractor = make_active_contractor(project, user, 'Main Co')
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/',
        {'contractor_ref': str(contractor.id)},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body.get('contractor') == 'Main Co' or body.get('contractor_ref') == str(
        contractor.id
    )
    project.refresh_from_db()
    assert project.contractor_ref_id == contractor.id
    assert project.contractor == 'Main Co'


@pytest.mark.django_db
def test_project_clear_contractor_ref(auth_client, project, user):
    contractor = make_active_contractor(project, user, 'Clear Co')
    project.contractor_ref = contractor
    project.contractor = contractor.name
    project.save(update_fields=['contractor_ref', 'contractor', 'updated_at'])
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/',
        {'contractor_ref': None},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    project.refresh_from_db()
    assert project.contractor_ref_id is None
    assert project.contractor == ''

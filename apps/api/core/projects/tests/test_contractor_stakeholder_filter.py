"""TDD: contractor role normalize + list filter (027-contractor-stakeholder-select)."""

import pytest

from projects.models import Stakeholder, StakeholderStatus
from projects.tests.contractor_select_helpers import (
    make_active_contractor,
    make_inactive_contractor,
    make_non_contractor,
    make_second_project,
    make_stakeholder,
)


def _results(resp):
    body = resp.json()
    if isinstance(body, dict):
        return body.get('results', body)
    return body


@pytest.mark.django_db
@pytest.mark.parametrize(
    'role_in',
    ['پیمانکار', 'Contractor', 'contractor'],
)
def test_role_aliases_normalize_to_contractor(auth_client, project, role_in):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'name': f'Party-{role_in}', 'role': role_in},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()['role'] == 'contractor'
    row = Stakeholder.objects.get(pk=resp.json()['id'])
    assert row.role == 'contractor'


@pytest.mark.django_db
def test_list_contractors_excludes_inactive_soft_deleted_and_other_roles(
    auth_client, project, user
):
    active = make_active_contractor(project, user, 'Active Co')
    make_inactive_contractor(project, user, 'Inactive Co')
    make_non_contractor(project, user, 'Owner Co')
    deleted = make_stakeholder(
        project,
        user=user,
        name='Deleted Co',
        role='contractor',
        status=StakeholderStatus.ACTIVE,
    )
    deleted.soft_delete(user=user)

    resp = auth_client.get(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'role': 'contractor', 'status': 'active'},
    )
    assert resp.status_code == 200, resp.content
    ids = {r['id'] for r in _results(resp)}
    assert str(active.id) in ids
    assert len(ids) == 1
    assert all(r['role'] == 'contractor' and r['status'] == 'active' for r in _results(resp))


@pytest.mark.django_db
def test_contractor_list_is_project_isolated(auth_client, project, user):
    local = make_active_contractor(project, user, 'Local Co')
    other = make_second_project(user)
    foreign = make_active_contractor(other, user, 'Foreign Co')

    resp = auth_client.get(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'role': 'contractor', 'status': 'active'},
    )
    assert resp.status_code == 200
    ids = {r['id'] for r in _results(resp)}
    assert str(local.id) in ids
    assert str(foreign.id) not in ids


@pytest.mark.django_db
def test_inactive_or_role_change_drops_from_contractor_list(auth_client, project, user):
    row = make_active_contractor(project, user, 'Flip Co')
    listing = auth_client.get(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'role': 'contractor', 'status': 'active'},
    )
    assert str(row.id) in {r['id'] for r in _results(listing)}

    patch = auth_client.patch(
        f'/api/v1/projects/{project.id}/stakeholders/{row.id}/',
        {'status': StakeholderStatus.INACTIVE},
        format='json',
    )
    assert patch.status_code == 200, patch.content
    listing2 = auth_client.get(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'role': 'contractor', 'status': 'active'},
    )
    assert str(row.id) not in {r['id'] for r in _results(listing2)}

    auth_client.patch(
        f'/api/v1/projects/{project.id}/stakeholders/{row.id}/',
        {'status': StakeholderStatus.ACTIVE, 'role': 'Owner'},
        format='json',
    )
    listing3 = auth_client.get(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'role': 'contractor', 'status': 'active'},
    )
    assert str(row.id) not in {r['id'] for r in _results(listing3)}

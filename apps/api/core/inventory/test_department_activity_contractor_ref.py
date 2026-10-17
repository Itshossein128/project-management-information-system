"""TDD: department activity contractor_ref (027 US1)."""

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from inventory.models import Department, DepartmentActivityRecord
from projects.models import StakeholderStatus
from projects.tests.contractor_select_helpers import (
    make_active_contractor,
    make_inactive_contractor,
    make_non_contractor,
    make_second_project,
)


def _list_url(project_id):
    return reverse(
        'project-department-activity-record-list',
        kwargs={'project_pk': project_id},
    )


@pytest.fixture
def hr_auth_client(auth_client, user):
    group, _ = Group.objects.get_or_create(name='hr')
    user.groups.add(group)
    return auth_client


@pytest.mark.django_db
def test_create_requires_active_contractor_ref_and_snapshots_name(
    hr_auth_client, project, user
):
    contractor = make_active_contractor(project, user, 'Snap Co')
    payload = {
        'department': Department.SECURITY,
        'date': '2024-03-01',
        'location': 'Gate',
        'activity_description': 'Patrol',
        'contractor_ref': str(contractor.id),
    }
    resp = hr_auth_client.post(_list_url(project.id), payload, format='json')
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body['contractor_ref'] == str(contractor.id)
    assert body['contractor'] == 'Snap Co'
    row = DepartmentActivityRecord.objects.get(pk=body['id'])
    assert row.contractor_ref_id == contractor.id
    assert row.contractor == 'Snap Co'


@pytest.mark.django_db
def test_create_rejects_missing_inactive_foreign_and_non_contractor(
    hr_auth_client, project, user
):
    url = _list_url(project.id)
    base = {
        'department': Department.SECURITY,
        'date': '2024-03-02',
        'location': 'Gate',
        'activity_description': 'Patrol',
    }
    missing = hr_auth_client.post(url, base, format='json')
    assert missing.status_code == 400

    inactive = make_inactive_contractor(project, user, 'Inactive Co')
    bad_inactive = hr_auth_client.post(
        url, {**base, 'contractor_ref': str(inactive.id)}, format='json'
    )
    assert bad_inactive.status_code == 400

    owner = make_non_contractor(project, user)
    bad_role = hr_auth_client.post(
        url, {**base, 'contractor_ref': str(owner.id)}, format='json'
    )
    assert bad_role.status_code == 400

    other = make_second_project(user)
    foreign = make_active_contractor(other, user, 'Foreign Co')
    bad_foreign = hr_auth_client.post(
        url, {**base, 'contractor_ref': str(foreign.id)}, format='json'
    )
    assert bad_foreign.status_code == 400


@pytest.mark.django_db
def test_warehouse_clears_contractor_ref(hr_auth_client, project, user):
    contractor = make_active_contractor(project, user, 'Wh Co')
    resp = hr_auth_client.post(
        _list_url(project.id),
        {
            'department': Department.WAREHOUSE,
            'date': '2024-03-03',
            'material_type': 'Cement',
            'unit': 'ton',
            'consumption_location': 'Site',
            'supplier': 'SupplyCo',
            'quantity_in': '1',
            'quantity_out': '0',
            'contractor_ref': str(contractor.id),
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body['contractor'] == ''
    assert body.get('contractor_ref') in (None, '')
    row = DepartmentActivityRecord.objects.get(pk=body['id'])
    assert row.contractor_ref_id is None


@pytest.mark.django_db
def test_filter_by_contractor_ref_and_legacy_name(hr_auth_client, project, user):
    c1 = make_active_contractor(project, user, 'Filter Alpha')
    c2 = make_active_contractor(project, user, 'Filter Beta')
    for c, loc in ((c1, 'A'), (c2, 'B')):
        hr_auth_client.post(
            _list_url(project.id),
            {
                'department': Department.SECURITY,
                'date': '2024-03-04',
                'location': loc,
                'activity_description': 'Work',
                'contractor_ref': str(c.id),
            },
            format='json',
        )

    by_ref = hr_auth_client.get(
        _list_url(project.id),
        {'department': Department.SECURITY, 'contractor_ref': str(c1.id)},
    )
    assert by_ref.status_code == 200
    rows = by_ref.json()['results']
    assert len(rows) == 1
    assert rows[0]['contractor'] == 'Filter Alpha'

    by_name = hr_auth_client.get(
        _list_url(project.id),
        {'department': Department.SECURITY, 'contractor': 'Filter Beta'},
    )
    assert by_name.status_code == 200
    assert len(by_name.json()['results']) == 1


@pytest.mark.django_db
def test_historical_snapshot_survives_inactive(hr_auth_client, project, user):
    contractor = make_active_contractor(project, user, 'History Co')
    created = hr_auth_client.post(
        _list_url(project.id),
        {
            'department': Department.SECURITY,
            'date': '2024-03-05',
            'location': 'Gate',
            'activity_description': 'Work',
            'contractor_ref': str(contractor.id),
        },
        format='json',
    )
    assert created.status_code == 201
    contractor.status = StakeholderStatus.INACTIVE
    contractor.save(update_fields=['status', 'updated_at'])

    detail = hr_auth_client.get(
        reverse(
            'project-department-activity-record-detail',
            kwargs={'project_pk': project.id, 'pk': created.json()['id']},
        )
    )
    assert detail.status_code == 200
    assert detail.json()['contractor'] == 'History Co'

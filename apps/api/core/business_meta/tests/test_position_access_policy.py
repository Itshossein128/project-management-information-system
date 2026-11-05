"""Inactive members cannot read project positions or the helper's other reads."""

import pytest
from rest_framework import status

from master_data.models import MemberStatus, ProjectPosition


def _rows(data):
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    return data


@pytest.fixture
def position(project):
    return ProjectPosition.objects.create(
        project=project,
        position_name='Planner',
        slug='planner',
    )


@pytest.mark.django_db
def test_inactive_member_cannot_read_positions_but_active_member_can(
    api_client, project, member, position,
):
    base = f'/api/v1/projects/{project.id}/positions/'
    api_client.force_authenticate(user=member.user)
    active = api_client.get(base)
    assert active.status_code == status.HTTP_200_OK
    rows = _rows(active.data)
    assert rows
    assert 'wage' not in rows[0]
    assert 'email' not in rows[0]
    assert 'phone' not in rows[0]

    detail = api_client.get(f'{base}{position.id}/')
    assert detail.status_code == status.HTTP_200_OK

    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    denied = api_client.get(base)
    assert denied.status_code == status.HTTP_403_FORBIDDEN
    denied_detail = api_client.get(f'{base}{position.id}/')
    assert denied_detail.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_inactive_member_cannot_read_direct_helper_callers(api_client, project, member):
    api_client.force_authenticate(user=member.user)
    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    space = api_client.get(f'/api/v1/projects/{project.id}/space-material-requests/')
    assert space.status_code == status.HTTP_403_FORBIDDEN
    records = api_client.get(f'/api/v1/projects/{project.id}/department-activity-records/')
    assert records.status_code == status.HTTP_403_FORBIDDEN

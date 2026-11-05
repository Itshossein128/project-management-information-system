"""Named observation exception is read-only and is not staff or HR."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectPosition
from projects.services import create_project_with_creator

User = get_user_model()


def _account(username, mobile, *, staff=False, superuser=False, group_name=None):
    if superuser:
        user = User.objects.create_superuser(
            username=username,
            password='testpass123',
            mobile=mobile,
            full_name=username,
        )
    else:
        user = User.objects.create_user(
            username=username,
            mobile=mobile,
            full_name=username,
            password='testpass123',
        )
        user.is_staff = staff
        user.is_superuser = False
        user.save(update_fields=['is_staff', 'is_superuser'])
    if group_name:
        group, _created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
    return user


def _client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_observation_reads_positions_but_cannot_write_or_manage_members(project, project_manager_role):
    position = ProjectPosition.objects.create(
        project=project,
        position_name='Planner',
        slug='planner',
    )
    positions = f'/api/v1/projects/{project.id}/positions/'
    members = f'/api/v1/projects/{project.id}/members/'
    accounts = {
        'staff': _account('staffonly', '+989120000011', staff=True),
        'hr': _account('hronly', '+989120000012', group_name='hr'),
        'admin': _account('sysadmin', '+989120000013', group_name='admin'),
        'superuser': _account('rootuser', '+989120000014', superuser=True),
    }
    for name in ('staff', 'hr'):
        client = _client(accounts[name])
        assert client.get(positions).status_code == status.HTTP_403_FORBIDDEN, name
        assert client.post(
            positions,
            {'position_name': 'Blocked', 'slug': 'blocked'},
            format='json',
        ).status_code == status.HTTP_403_FORBIDDEN, name

    for name in ('admin', 'superuser'):
        client = _client(accounts[name])
        listed = client.get(positions)
        assert listed.status_code == status.HTTP_200_OK, name
        detail = client.get(f'{positions}{position.id}/')
        assert detail.status_code == status.HTTP_200_OK, name
        created = client.post(
            positions,
            {'position_name': 'New title', 'slug': 'new-title'},
            format='json',
        )
        assert created.status_code == status.HTTP_403_FORBIDDEN, name
        added = client.post(
            members,
            {'user_id': str(accounts['staff'].id), 'role_ids': [str(project_manager_role.id)]},
            format='json',
        )
        assert added.status_code == status.HTTP_403_FORBIDDEN, name
        assert not ProjectMember.objects.filter(user=accounts['staff']).exists()


@pytest.mark.django_db
def test_inactive_observer_can_still_read(project):
    observer = _account('observer', '+989120000015', superuser=True)
    membership = ProjectMember.objects.create(
        project=project,
        user=observer,
        status=MemberStatus.INACTIVE,
    )
    client = _client(observer)
    response = client.get(f'/api/v1/projects/{project.id}/positions/')
    assert response.status_code == status.HTTP_200_OK
    assert membership.status == MemberStatus.INACTIVE


@pytest.mark.django_db
def test_project_manager_does_not_manage_another_project(user, other_user, project_manager_role):
    other_project = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-002',
        project_name='Other Project',
        employer='Employer Co',
        start_date='2024-02-01',
    )
    client = _client(user)
    response = client.post(
        f'/api/v1/projects/{other_project.id}/members/',
        {'user_id': str(other_user.id), 'role_ids': [str(project_manager_role.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

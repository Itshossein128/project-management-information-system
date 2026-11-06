"""Document allow/deny pairs that UI buttons must match (server is authoritative)."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from master_data.models import Role

User = get_user_model()


def _client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_observer_cannot_write_members_even_if_ui_showed_read(project, project_manager_role):
    """Observation admin: read positions OK; manage_members write denied."""
    admin = User.objects.create_user(
        username='parity_admin',
        mobile='+989120000401',
        password='x',
    )
    group, _ = Group.objects.get_or_create(name='admin')
    admin.groups.add(group)
    client = _client(admin)
    assert client.get(f'/api/v1/projects/{project.id}/positions/').status_code == status.HTTP_200_OK
    assert (
        client.post(
            f'/api/v1/projects/{project.id}/members/',
            {'user_id': str(admin.id), 'role_ids': [str(project_manager_role.id)]},
            format='json',
        ).status_code
        == status.HTTP_403_FORBIDDEN
    )


@pytest.mark.django_db
def test_viewer_member_denied_manage_members(user, other_user, project, viewer_role):
    member = ProjectMember.objects.get(project=project, user=user)
    member.member_roles.all().delete()
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    client = _client(user)
    assert (
        client.post(
            f'/api/v1/projects/{project.id}/members/',
            {'user_id': str(other_user.id), 'role_ids': [str(viewer_role.id)]},
            format='json',
        ).status_code
        == status.HTTP_403_FORBIDDEN
    )


@pytest.mark.django_db
def test_active_manager_can_manage_members(user, other_user, project, project_manager_role):
    client = _client(user)
    response = client.post(
        f'/api/v1/projects/{project.id}/members/',
        {'user_id': str(other_user.id), 'role_ids': [str(project_manager_role.id)]},
        format='json',
    )
    assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_409_CONFLICT)

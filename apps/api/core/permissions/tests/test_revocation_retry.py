"""A6-P4: permission must be re-evaluated after revoke (no sticky allow)."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, RolePermission
from permissions.project import active_member_has_codename

User = get_user_model()


@pytest.mark.django_db
def test_permission_denied_after_membership_deactivate(user, project, project_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    assert active_member_has_codename(user, project.id, 'manage_members') is True

    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])

    assert active_member_has_codename(user, project.id, 'manage_members') is False

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f'/api/v1/projects/{project.id}/members/',
        {'user_id': str(user.id), 'role_ids': [str(project_manager_role.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_denied_after_explicit_deny(user, other_user, project, project_manager_role):
    from permissions.services import set_permission_override

    member = ProjectMember.objects.get(project=project, user=user)
    set_permission_override(member, 'manage_members', False, actor=user)
    assert active_member_has_codename(user, project.id, 'manage_members') is False

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f'/api/v1/projects/{project.id}/members/',
        {'user_id': str(other_user.id), 'role_ids': [str(project_manager_role.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

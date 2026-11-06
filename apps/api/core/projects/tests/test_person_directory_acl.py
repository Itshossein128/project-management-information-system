"""A6-P4 person directory and lookup ACL."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
from master_data.models import Permission, RolePermission

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_lookup_requires_manage_members(api_client, user, other_user, project, viewer_role):
    ProjectMemberRole.objects.filter(member__project=project, member__user=user).delete()
    # demote creator to viewer without manage_members
    member = project.members.get(user=user)
    member.member_roles.all().delete()
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    api_client.force_authenticate(user=user)
    response = api_client.get(
        '/api/v1/users/lookup/',
        {'q': other_user.full_name[:4], 'project_id': str(project.id)},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_lookup_omits_contacts_without_person_permission(
    api_client, user, other_user, project, project_manager_role
):
    other_user.email = 'hidden@example.com'
    other_user.mobile = '+989121111111'
    other_user.save(update_fields=['email', 'mobile'])
    # Ensure PM role lacks view_person_contacts for this test
    RolePermission.objects.filter(
        role=project_manager_role,
        permission_codename='view_person_contacts',
    ).delete()
    api_client.force_authenticate(user=user)
    response = api_client.get(
        '/api/v1/users/lookup/',
        {'q': other_user.full_name[:4], 'project_id': str(project.id)},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data
    row = response.data[0]
    assert 'user_id' in row and 'full_name' in row
    assert 'email' not in row or row.get('email') in ('', None)
    assert 'mobile' not in row or row.get('mobile') in ('', None)


@pytest.mark.django_db
def test_roster_omits_contacts_without_person_permission(
    api_client, user, other_user, project, project_manager_role
):
    from master_data.models import MemberStatus, ProjectMember

    RolePermission.objects.filter(
        role=project_manager_role,
        permission_codename='view_person_contacts',
    ).delete()
    ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    other_user.email = 'roster@example.com'
    other_user.save(update_fields=['email'])
    api_client.force_authenticate(user=user)
    response = api_client.get(f'/api/v1/projects/{project.id}/members/')
    assert response.status_code == status.HTTP_200_OK
    target = next(r for r in response.data if str(r['user_id']) == str(other_user.id))
    assert target['email'] == ''
    assert target.get('invited_email') in ('', None)
    assert target.get('invited_mobile') in ('', None)
    assert isinstance(target.get('position_titles'), list)


@pytest.mark.django_db
def test_lookup_email_match_requires_view_person_contacts(
    api_client, user, other_user, project, project_manager_role
):
    other_user.email = 'lookup.email.match@example.com'
    other_user.save(update_fields=['email'])
    RolePermission.objects.filter(
        role=project_manager_role,
        permission_codename='view_person_contacts',
    ).delete()
    api_client.force_authenticate(user=user)
    by_name = api_client.get(
        '/api/v1/users/lookup/',
        {'q': other_user.full_name[:4], 'project_id': str(project.id)},
    )
    assert by_name.status_code == status.HTTP_200_OK
    assert any(str(row['user_id']) == str(other_user.id) for row in by_name.data)
    by_email = api_client.get(
        '/api/v1/users/lookup/',
        {'q': 'lookup.email.match', 'project_id': str(project.id)},
    )
    assert by_email.status_code == status.HTTP_200_OK
    assert not any(str(row['user_id']) == str(other_user.id) for row in by_email.data)


@pytest.mark.django_db
def test_project_manager_default_omits_view_person_contacts(project_manager_role):
    codes = {rp.permission_codename for rp in project_manager_role.role_permissions.all()}
    assert 'view_person_contacts' not in codes
    assert 'view_person_contacts' not in DEFAULT_ROLE_PERMISSIONS['project_manager']


@pytest.mark.django_db
def test_inactive_member_effective_permissions_are_empty(auth_client, user, project):
    member = ProjectMember.objects.get(project=project, user=user)
    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    response = auth_client.get(
        f'/api/v1/projects/{project.id}/members/{user.id}/permissions/',
    )
    assert response.status_code == status.HTTP_200_OK
    effective = response.json()['effective']
    assert all(v is False for v in effective.values())

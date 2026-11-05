"""Permission origin, deny, reset, and removing one of two roles."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import ProjectMemberRole, Role, RolePermission


def _role(name, *codes):
    role = Role.objects.create(role_name=name, description='')
    for code in codes:
        RolePermission.objects.create(role=role, permission_codename=code)
    return role


@pytest.mark.django_db
def test_two_roles_deny_reset_and_removal_keep_the_other_role(auth_client, project, member):
    planning = _role('برنامه‌ریزی آزمایشی', 'view_project')
    cost = _role('کنترل هزینه آزمایشی', 'edit_wbs')
    ProjectMemberRole.objects.filter(member=member).delete()
    ProjectMemberRole.objects.create(member=member, role=planning)
    ProjectMemberRole.objects.create(member=member, role=cost)
    url = f'/api/v1/projects/{project.id}/members/{member.user_id}/permissions/'
    client = APIClient()
    client.force_authenticate(user=member.user)
    listed = client.get(url)
    by_code = {row['codename']: row for row in listed.data['permissions']}
    assert by_code['view_project']['granted'] is True
    assert by_code['view_project']['origin'] == 'inherit'
    assert by_code['edit_wbs']['origin'] == 'inherit'

    denied = auth_client.post(
        url,
        {'permission_codename': 'view_project', 'is_granted': False},
        format='json',
    )
    assert denied.status_code == status.HTTP_200_OK
    denied_row = next(row for row in denied.data['permissions'] if row['codename'] == 'view_project')
    assert denied_row['origin'] == 'deny'
    assert denied_row['granted'] is False
    member.refresh_from_db()
    assert member.has_permission('view_project') is False

    reset = auth_client.delete(f'{url}?permission_codename=view_project')
    assert reset.status_code == status.HTTP_200_OK
    reset_row = next(row for row in reset.data['permissions'] if row['codename'] == 'view_project')
    assert reset_row['origin'] == 'inherit'
    assert reset_row['granted'] is True

    removed = auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': [str(planning.id)]},
        format='json',
    )
    assert removed.status_code == status.HTTP_200_OK
    after = auth_client.get(url)
    after_codes = {row['codename']: row for row in after.data['permissions']}
    assert after_codes['view_project']['granted'] is True
    assert after_codes['edit_wbs']['granted'] is False


@pytest.mark.django_db
def test_unknown_permission_code_is_rejected(auth_client, project, member):
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/permissions/',
        {'permission_codename': 'not_a_permission', 'is_granted': True},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

"""Local roles stay inside one project."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import (
    MemberStatus,
    ProjectMember,
    ProjectMemberRole,
    Role,
    RoleAccessChange,
    RolePermission,
)
from projects.services import create_project_with_creator

User = get_user_model()


def _client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_local_role_is_invisible_and_unusable_in_another_project(
    user, other_user, project, project_manager_role,
):
    project_b = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-LOCAL-B',
        project_name='Project B',
        employer='Employer Co',
        start_date='2024-03-01',
    )
    created = _client(user).post(
        f'/api/v1/projects/{project.id}/roles/',
        {'role_name': 'هماهنگ کننده BIM', 'description': 'محلی'},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    role_id = created.data['id']
    listed_a = _client(user).get(f'/api/v1/projects/{project.id}/roles/')
    listed_b = _client(other_user).get(f'/api/v1/projects/{project_b.id}/roles/')
    assert listed_a.status_code == status.HTTP_200_OK
    assert listed_b.status_code == status.HTTP_200_OK
    assert role_id in {row['id'] for row in listed_a.data}
    assert str(project_manager_role.id) in {row['id'] for row in listed_a.data}
    assert str(project_manager_role.id) in {row['id'] for row in listed_b.data}
    assert role_id not in {row['id'] for row in listed_b.data}
    denied = _client(other_user).patch(
        f'/api/v1/projects/{project_b.id}/roles/{role_id}/',
        {'description': 'تغییر'},
        format='json',
    )
    assert denied.status_code == status.HTTP_404_NOT_FOUND
    member_b = ProjectMember.objects.get(project=project_b, user=other_user)
    crossed = _client(other_user).patch(
        f'/api/v1/projects/{project_b.id}/members/{other_user.id}/',
        {'role_ids': [role_id]},
        format='json',
    )
    assert crossed.status_code == status.HTTP_400_BAD_REQUEST
    assert crossed.data['error']['code'] == 'role_project_mismatch'
    assert ProjectMemberRole.objects.filter(member=member_b, role_id=role_id).count() == 0


@pytest.mark.django_db
def test_project_manager_cannot_delete_global_role_and_assigned_role_blocks_delete(
    user, project, member,
):
    admin = User.objects.create_user(
        username='roleadmin',
        mobile='+989120000031',
        full_name='Role Admin',
        password='testpass123',
    )
    group, _created = Group.objects.get_or_create(name='admin')
    admin.groups.add(group)
    created = _client(admin).post(
        '/api/v1/roles/',
        {'role_name': 'نقش سفارشی سراسری', 'permissions': ['view_project']},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    role_id = created.data['id']
    assert _client(user).delete(f'/api/v1/roles/{role_id}/').status_code == status.HTTP_403_FORBIDDEN
    _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': [role_id]},
        format='json',
    )
    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])
    blocked = _client(admin).delete(f'/api/v1/roles/{role_id}/')
    assert blocked.status_code == status.HTTP_409_CONFLICT
    assert blocked.data['error']['code'] == 'role_in_use'
    assert blocked.data['error']['details']['assignment_count'] >= 1
    assert ProjectMemberRole.objects.filter(role_id=role_id).count() == 1
    member.status = MemberStatus.ACTIVE
    member.save(update_fields=['status'])
    cleared = _client(user).patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': []},
        format='json',
    )
    assert cleared.status_code == status.HTTP_200_OK
    deleted = _client(admin).delete(f'/api/v1/roles/{role_id}/')
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert not Role.objects.filter(pk=role_id).exists()


@pytest.mark.django_db
def test_system_role_remains_undeletable(project_manager_role):
    admin = User.objects.create_user(
        username='roleadmin2',
        mobile='+989120000032',
        full_name='Role Admin 2',
        password='testpass123',
        is_staff=True,
    )
    response = _client(admin).delete(f'/api/v1/roles/{project_manager_role.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Role.objects.filter(pk=project_manager_role.id).exists()


def _org_user(username, mobile, *, staff=False, group_name=None):
    account = User.objects.create_user(
        username=username,
        mobile=mobile,
        full_name=username,
        password='testpass123',
        is_staff=staff,
    )
    if group_name:
        account.groups.add(Group.objects.get_or_create(name=group_name)[0])
    return account


@pytest.mark.django_db
def test_global_route_cannot_read_or_manage_local_role_and_rename_is_recorded(
    user, other_user, project,
):
    created = _client(user).post(
        f'/api/v1/projects/{project.id}/roles/',
        {'role_name': 'نقش محلی بسته', 'description': 'اول'},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    role_id = created.data['id']
    assert RoleAccessChange.objects.filter(
        role_id=role_id,
        action='role_created',
        actor=user,
        project=project,
    ).exists()

    listed = _client(other_user).get('/api/v1/roles/')
    assert listed.status_code == status.HTTP_200_OK
    assert role_id not in {row['id'] for row in listed.data}

    outsider = _client(other_user)
    assert outsider.get(f'/api/v1/roles/{role_id}/').status_code == status.HTTP_404_NOT_FOUND
    assert outsider.get(f'/api/v1/roles/{role_id}/impact/').status_code == status.HTTP_404_NOT_FOUND
    assert outsider.patch(
        f'/api/v1/roles/{role_id}/',
        {'role_name': 'نقش دزدیده'},
        format='json',
    ).status_code == status.HTTP_404_NOT_FOUND

    for actor in (
        _org_user('localstaff', '+989120000051', staff=True),
        _org_user('localadmin', '+989120000052', group_name='admin'),
        _org_user('localhr', '+989120000053', group_name='hr'),
    ):
        api = _client(actor)
        assert api.get(f'/api/v1/roles/{role_id}/').status_code == status.HTTP_404_NOT_FOUND
        assert api.get(f'/api/v1/roles/{role_id}/impact/').status_code == status.HTTP_404_NOT_FOUND
        assert api.patch(
            f'/api/v1/roles/{role_id}/',
            {'role_name': 'نقش دزدیده'},
            format='json',
        ).status_code == status.HTTP_404_NOT_FOUND
        assert api.patch(
            f'/api/v1/roles/{role_id}/permissions/',
            {'permissions': ['manage_members']},
            format='json',
        ).status_code == status.HTTP_404_NOT_FOUND
        assert api.put(
            f'/api/v1/roles/{role_id}/permissions/',
            {'permissions': ['view_project']},
            format='json',
        ).status_code == status.HTTP_404_NOT_FOUND
        assert api.delete(f'/api/v1/roles/{role_id}/').status_code == status.HTTP_404_NOT_FOUND

    role = Role.objects.get(pk=role_id)
    assert role.role_name == 'نقش محلی بسته'
    assert not RolePermission.objects.filter(role=role).exists()

    renamed = _client(user).patch(
        f'/api/v1/projects/{project.id}/roles/{role_id}/',
        {'role_name': 'نقش محلی تازه'},
        format='json',
    )
    assert renamed.status_code == status.HTTP_200_OK
    renamed_row = RoleAccessChange.objects.get(
        role_id=role_id,
        action='role_renamed',
        actor=user,
    )
    assert renamed_row.before['role_name'] == 'نقش محلی بسته'
    assert renamed_row.after['role_name'] == 'نقش محلی تازه'
    assert renamed_row.project_id == project.id

    described = _client(user).patch(
        f'/api/v1/projects/{project.id}/roles/{role_id}/',
        {'description': 'شرح تازه'},
        format='json',
    )
    assert described.status_code == status.HTTP_200_OK
    assert RoleAccessChange.objects.filter(
        role_id=role_id,
        action='role_renamed',
        actor=user,
        after__description='شرح تازه',
    ).exists()

    admin = _org_user('globalkeeper', '+989120000054', group_name='admin')
    global_role = _client(admin).post(
        '/api/v1/roles/',
        {'role_name': 'نقش سراسری باز', 'permissions': ['view_project']},
        format='json',
    )
    assert global_role.status_code == status.HTTP_201_CREATED
    global_id = global_role.data['id']
    assert RoleAccessChange.objects.filter(
        role_id=global_id,
        action='role_created',
        actor=admin,
    ).exists()
    kept = _client(admin).patch(
        f'/api/v1/roles/{global_id}/',
        {'description': 'توضیح سراسری'},
        format='json',
    )
    assert kept.status_code == status.HTTP_200_OK
    assert RoleAccessChange.objects.filter(
        role_id=global_id,
        action='role_renamed',
        actor=admin,
        after__description='توضیح سراسری',
    ).exists()
    repermissioned = _client(admin).put(
        f'/api/v1/roles/{global_id}/permissions/',
        {'permissions': ['view_dashboard']},
        format='json',
    )
    assert repermissioned.status_code == status.HTTP_200_OK
    permission_row = RoleAccessChange.objects.filter(
        role_id=global_id,
        action='role_permissions_changed',
        subject_user__isnull=True,
        after__permissions=['view_dashboard'],
    )
    assert permission_row.exists()

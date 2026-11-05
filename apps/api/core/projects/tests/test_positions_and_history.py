"""Several job titles and the base access-change record."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import PositionPermission, ProjectPosition, RoleAccessChange


@pytest.mark.django_db
def test_selectable_titles_and_independent_roles(auth_client, project, member, viewer_role):
    local = ProjectPosition.objects.create(
        project=project,
        position_name='سمت محلی',
        slug='local-title',
        is_active=True,
    )
    public = ProjectPosition.objects.create(
        project=None,
        position_name='سمت عمومی',
        slug='public-title',
        is_active=True,
    )
    other = ProjectPosition.objects.create(
        project=None,
        position_name='سمت دیگر پروژه',
        slug='foreign-title',
        is_active=True,
    )
    other.project_id = project.id
    # A title owned by a second project is created below.
    from projects.services import create_project_with_creator
    from django.contrib.auth import get_user_model

    outsider = get_user_model().objects.create_user(
        username='titleoutsider',
        mobile='+989120000041',
        full_name='Outsider',
        password='testpass123',
    )
    project_b = create_project_with_creator(
        creator=outsider,
        project_code='PRJ-TITLE-B',
        project_name='Title B',
        employer='Employer Co',
        start_date='2024-04-01',
    )
    foreign = ProjectPosition.objects.create(
        project=project_b,
        position_name='سمت پروژه دیگر',
        slug='foreign-project-title',
        is_active=True,
    )
    other.delete()
    selectable = auth_client.get(
        f'/api/v1/projects/{project.id}/positions/?selectable=1',
    )
    assert selectable.status_code == status.HTTP_200_OK
    rows = selectable.data['results'] if isinstance(selectable.data, dict) else selectable.data
    selectable_ids = {str(row['id']) for row in rows}
    assert str(local.id) in selectable_ids
    assert str(public.id) in selectable_ids
    assert str(foreign.id) not in selectable_ids

    PositionPermission.objects.create(position=local, permission_codename='view_reports')
    saved = auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'position_ids': [str(local.id), str(public.id)], 'role_ids': [str(viewer_role.id)]},
        format='json',
    )
    assert saved.status_code == status.HTTP_200_OK
    member.refresh_from_db()
    assert set(member.positions.values_list('id', flat=True)) == {local.id, public.id}
    assert member.member_roles.filter(role=viewer_role).exists()
    permissions = auth_client.get(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/permissions/',
    )
    by_code = {row['codename']: row for row in permissions.data['permissions']}
    assert by_code['view_reports']['granted'] is True
    assert by_code['view_reports']['origin'] == 'inherit'

    rejected = auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'position_ids': [str(foreign.id)]},
        format='json',
    )
    assert rejected.status_code == status.HTTP_400_BAD_REQUEST
    member.refresh_from_db()
    assert foreign.id not in set(member.positions.values_list('id', flat=True))
    assert RoleAccessChange.objects.filter(
        project=project,
        action__in=['roles_replaced', 'positions_replaced'],
    ).exists()


@pytest.mark.django_db
def test_suspended_assignment_blocks_delete_and_history_remains(auth_client, project, member):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from master_data.models import MemberStatus, Role

    admin = get_user_model().objects.create_user(
        username='histadmin',
        mobile='+989120000042',
        full_name='Hist Admin',
        password='testpass123',
    )
    admin.groups.add(Group.objects.get_or_create(name='admin')[0])
    created = APIClient()
    created.force_authenticate(user=admin)
    role = created.post(
        '/api/v1/roles/',
        {'role_name': 'نقش تاریخچه', 'permissions': ['view_dashboard']},
        format='json',
    )
    role_id = role.data['id']
    auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': [role_id]},
        format='json',
    )
    member.status = MemberStatus.SUSPENDED
    member.save(update_fields=['status'])
    blocked = created.delete(f'/api/v1/roles/{role_id}/')
    assert blocked.status_code == status.HTTP_409_CONFLICT
    assert Role.objects.filter(pk=role_id).exists()
    member.status = MemberStatus.ACTIVE
    member.save(update_fields=['status'])
    auth_client.patch(
        f'/api/v1/projects/{project.id}/members/{member.user_id}/',
        {'role_ids': []},
        format='json',
    )
    assert created.delete(f'/api/v1/roles/{role_id}/').status_code == status.HTTP_204_NO_CONTENT
    history = auth_client.get(f'/api/v1/projects/{project.id}/access-changes/')
    assert history.status_code == status.HTTP_200_OK
    assert any(row['action'] == 'roles_replaced' for row in history.data)
    assert history.data[0]['created_at']

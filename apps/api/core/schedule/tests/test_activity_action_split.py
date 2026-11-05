"""Edit, delete, and approval are separate on one activity."""

import importlib

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, RolePermission

User = get_user_model()


def _role_with(*codenames, name):
    role = Role.objects.create(role_name=name, description='')
    for codename in codenames:
        RolePermission.objects.create(role=role, permission_codename=codename)
    return role


def _join(project, user, role):
    member = ProjectMember.objects.create(
        project=project,
        user=user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=role)
    return member


@pytest.mark.django_db
def test_editor_can_update_but_not_delete_or_approve(project, activity):
    editor = User.objects.create_user(
        username='activityeditor',
        mobile='+989120000021',
        full_name='Editor',
        password='testpass123',
    )
    role = _role_with('view_activities', 'edit_activities', name='edit_only_activities')
    _join(project, editor, role)
    client = APIClient()
    client.force_authenticate(user=editor)
    base = f'/api/v1/projects/{project.id}/activities/{activity.id}/'
    updated = client.patch(base, {'activity_name': 'Renamed'}, format='json')
    assert updated.status_code == status.HTTP_200_OK
    deleted = client.delete(base)
    assert deleted.status_code == status.HTTP_403_FORBIDDEN
    approved = client.post(f'{base}measurement/approve/', {}, format='json')
    assert approved.status_code == status.HTTP_403_FORBIDDEN
    activity.refresh_from_db()
    assert activity.activity_name == 'Renamed'
    assert activity.is_deleted is False


@pytest.mark.django_db
def test_backfill_lets_existing_editor_delete(project, activity):
    role = _role_with('view_activities', 'edit_activities', name='legacy_activity_editor')
    grant_delete_activities = importlib.import_module(
        'master_data.migrations.0014_grant_delete_activities',
    ).grant_delete_activities
    grant_delete_activities(apps, None)
    assert RolePermission.objects.filter(
        role=role,
        permission_codename='delete_activities',
    ).exists()
    editor = User.objects.create_user(
        username='legacyeditor',
        mobile='+989120000022',
        full_name='Legacy',
        password='testpass123',
    )
    _join(project, editor, role)
    client = APIClient()
    client.force_authenticate(user=editor)
    response = client.delete(f'/api/v1/projects/{project.id}/activities/{activity.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project
from projects.services import create_project_with_creator

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        mobile='+989121234567',
        full_name='Test User',
        password='testpass123',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otheruser',
        mobile='+989121234568',
        full_name='Other User',
        password='testpass123',
    )


@pytest.fixture
def project_manager_role(db):
    return Role.objects.get(role_name='project_manager')


@pytest.fixture
def viewer_role(db):
    return Role.objects.get(role_name='viewer')


@pytest.fixture
def project(db, user, project_manager_role):
    return create_project_with_creator(
        creator=user,
        project_code='PRJ-001',
        project_name='Test Project',
        employer='Employer Co',
        start_date='2024-01-01',
    )


@pytest.fixture
def member(db, project, other_user, viewer_role):
    m = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=m, role=viewer_role)
    return m


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project
from projects.services import create_project_with_creator

User = get_user_model()


@pytest.fixture(autouse=True)
def test_cache_backend(settings):
    """Use in-memory cache in tests (ratelimit + API cache)."""
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }


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
def site_supervisor_role(db):
    return Role.objects.get(role_name='site_supervisor')


@pytest.fixture
def viewer_member(db, project, other_user, site_supervisor_role):
    """Member with view_reports (site_supervisor role)."""
    m = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=m, role=site_supervisor_role)
    return m


@pytest.fixture
def wbs(db, project):
    from wbs.services import create_wbs_node

    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    return node


@pytest.fixture
def activity(db, project, wbs, user):
    from projects.models import Activity

    return Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A1',
        activity_name='Activity 1',
        total_quantity=100,
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

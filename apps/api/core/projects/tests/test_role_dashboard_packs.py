"""FR-RPT US2: role dashboard packs, portfolio scope, SoD on IPC approve."""

import pytest

pytest_plugins = ['contracts.tests.conftest']
from django.contrib.auth import get_user_model
from rest_framework import status

from config.exceptions import CodedValidationError
from contracts.models import IPCStatus
from contracts.services.ipc_service import approve_ipc, submit_ipc
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.services import create_project_with_creator

User = get_user_model()


@pytest.fixture
def finance_manager_role(db):
    return Role.objects.get(role_name='finance_manager')


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        username='financeuser',
        mobile='+989121234569',
        full_name='Finance User',
        password='testpass123',
    )


@pytest.fixture
def finance_client(api_client, finance_user, finance_manager_role):
    api_client.force_authenticate(user=finance_user)
    return api_client


@pytest.mark.django_db
def test_portfolio_dashboard_only_member_projects(
    finance_client, finance_user, finance_manager_role, user, project_manager_role
):
    project_a = create_project_with_creator(
        creator=user,
        project_code='PA-001',
        project_name='Project A',
        employer='E',
        start_date='2024-01-01',
    )
    project_b = create_project_with_creator(
        creator=user,
        project_code='PB-001',
        project_name='Project B',
        employer='E',
        start_date='2024-01-01',
    )
    project_c = create_project_with_creator(
        creator=user,
        project_code='PC-001',
        project_name='Project C',
        employer='E',
        start_date='2024-01-01',
    )

    for proj in (project_a, project_b):
        member = ProjectMember.objects.create(
            project=proj,
            user=finance_user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=finance_manager_role)

    resp = finance_client.get('/api/v1/portfolio/dashboard/')
    assert resp.status_code == 200
    ids = {p['project_id'] for p in resp.data['projects']}
    assert str(project_a.id) in ids
    assert str(project_b.id) in ids
    assert str(project_c.id) not in ids


@pytest.mark.django_db
def test_finance_pack_on_project(finance_client, finance_user, project, finance_manager_role):
    member = ProjectMember.objects.create(
        project=project,
        user=finance_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    resp = finance_client.get(f'/api/v1/projects/{project.id}/dashboard/pack/')
    assert resp.status_code == 200
    assert resp.data['pack_id'] == 'finance'
    assert resp.data['groups']


@pytest.fixture
def viewer_client(api_client, other_user, project, viewer_role):
    member = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    api_client.force_authenticate(user=other_user)
    return api_client


@pytest.mark.django_db
def test_viewer_can_get_pack(viewer_client, project):
    resp = viewer_client.get(f'/api/v1/projects/{project.id}/dashboard/pack/')
    assert resp.status_code == 200
    assert resp.data['pack_id'] == 'project_manager'


@pytest.mark.django_db
def test_ipc_creator_cannot_self_approve(ipc_with_item, user):
    ipc = ipc_with_item
    submit_ipc(ipc, user)
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.SUBMITTED
    with pytest.raises(CodedValidationError) as exc:
        approve_ipc(ipc, user)
    codes = exc.value.get_codes()
    assert 'sod_self_approve' in codes

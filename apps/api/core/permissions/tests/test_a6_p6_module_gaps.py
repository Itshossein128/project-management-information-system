"""Representative two-project reads for A6-P6 inventory rows the shared suite does not name."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

PROJECT_READS = (
    ('M04', 'reporting-configurations/'),
    ('M06', 'tables/'),
    ('M07', 'wbs/'),
    ('M08', 'activities/'),
    ('M09', 'daily-reports/'),
    ('M10', 'concrete-batches/'),
    ('M11', 'risk-events/'),
    ('M12', 'decision-cases/'),
    ('M13', 'overtime-requests/'),
    ('M15', 'budgets/'),
    ('M16', 'cash-flow/'),
    ('M17', 'contracts/'),
    ('M18', 'subcontractors/'),
    ('M19', 'requisitions/'),
    ('M21', 'materials/'),
    ('M22', 'correspondence/'),
    ('M26', 'economic/snapshot/'),
    ('M27', 'alert-rules/'),
)


def _activate(project):
    from django.utils import timezone

    from projects.models import ProjectStatus

    project.status = ProjectStatus.ACTIVE
    project.scope_description = 'B'
    project.contract_amount = 1
    project.budget_approved_at = timezone.now()
    project.save()


@pytest.mark.django_db
@pytest.mark.parametrize('module_id,suffix', PROJECT_READS)
def test_member_can_read_own_project_and_not_the_other(
    user, other_user, project, project_manager_role, module_id, suffix,
):
    from projects.services import create_project_with_creator

    other = create_project_with_creator(
        creator=other_user,
        project_code=f'GAP-{module_id}',
        project_name=f'Gap {module_id}',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    _activate(other)
    client = APIClient()
    client.force_authenticate(user=user)
    own = client.get(f'/api/v1/projects/{project.id}/{suffix}')
    foreign = client.get(f'/api/v1/projects/{other.id}/{suffix}')
    assert own.status_code == status.HTTP_200_OK, module_id
    assert foreign.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND), module_id


@pytest.mark.django_db
def test_org_reference_read_is_open_and_write_is_not_for_project_manager(user, project):
    client = APIClient()
    client.force_authenticate(user=user)
    listed = client.get('/api/v1/organization-units/')
    created = client.post('/api/v1/organization-units/', {'name': 'Gap unit'}, format='json')
    assert listed.status_code == status.HTTP_200_OK
    assert created.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_notification_list_requires_sign_in_and_stays_on_the_caller(user):
    anonymous = APIClient()
    refused = anonymous.get('/api/v1/notifications/')
    client = APIClient()
    client.force_authenticate(user=user)
    own = client.get('/api/v1/notifications/')
    assert refused.status_code == status.HTTP_401_UNAUTHORIZED
    assert own.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_same_person_cannot_read_a_third_project(user, other_user, project, project_manager_role, viewer_role):
    """U02: membership in A and B does not reveal a project the person has not joined."""
    from master_data.models import ProjectMember, ProjectMemberRole
    from projects.services import create_project_with_creator

    second = create_project_with_creator(
        creator=other_user,
        project_code='GAP-U02-B',
        project_name='Gap U02 B',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    _activate(second)
    member = ProjectMember.objects.create(project=second, user=user, status='active')
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    third = create_project_with_creator(
        creator=other_user,
        project_code='GAP-U02-C',
        project_name='Gap U02 C',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    _activate(third)
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.get(f'/api/v1/projects/{project.id}/').status_code == status.HTTP_200_OK
    assert client.get(f'/api/v1/projects/{second.id}/').status_code == status.HTTP_200_OK
    assert client.get(f'/api/v1/projects/{third.id}/').status_code in (
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
    )


@pytest.mark.django_db
def test_two_roles_then_deny_blocks_project_approve(user, project, project_manager_role, viewer_role):
    """U03: collected roles do not survive an explicit deny on finalization."""
    from master_data.models import ProjectMember, ProjectMemberRole
    from permissions.services import set_permission_override

    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=viewer_role)
    set_permission_override(member, 'approve_project', False, actor=user)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(f'/api/v1/projects/{project.id}/approve/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

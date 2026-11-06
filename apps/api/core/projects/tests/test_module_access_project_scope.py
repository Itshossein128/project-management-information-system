"""A6-P4 project isolation and observation write deny."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from permissions.project import assert_same_project
from config.exceptions import CodedValidationError

User = get_user_model()


@pytest.mark.django_db
def test_member_of_a_cannot_list_foreign_project_detail(user, other_user, project, project_manager_role):
    from projects.services import create_project_with_creator
    from projects.models import ProjectStatus
    from django.utils import timezone

    other = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-B',
        project_name='Other Project',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    other.status = ProjectStatus.ACTIVE
    other.scope_description = 'B'
    other.contract_amount = 1
    other.budget_approved_at = timezone.now()
    other.save()

    client = APIClient()
    client.force_authenticate(user=user)
    # user is member of project A only
    denied = client.get(f'/api/v1/projects/{other.id}/')
    assert denied.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
    allowed = client.get(f'/api/v1/projects/{project.id}/')
    assert allowed.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_observation_cannot_post_members(project, project_manager_role):
    admin = User.objects.create_user(
        username='obs_admin',
        mobile='+989120000201',
        password='x',
        full_name='Obs Admin',
    )
    group, _ = Group.objects.get_or_create(name='admin')
    admin.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=admin)
    positions = client.get(f'/api/v1/projects/{project.id}/positions/')
    assert positions.status_code == status.HTTP_200_OK
    created = client.post(
        f'/api/v1/projects/{project.id}/members/',
        {'user_id': str(admin.id), 'role_ids': [str(project_manager_role.id)]},
        format='json',
    )
    assert created.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_assert_same_project_helper():
    with pytest.raises(CodedValidationError) as exc:
        assert_same_project('1', '2')
    assert exc.value.default_code == 'project_scope_mismatch'


@pytest.mark.django_db
def test_communication_plan_rejects_foreign_stakeholder(
    auth_client, project, user, other_user, project_manager_role, finance_manager_role
):
    """Member of project A cannot bind project B stakeholder to a plan in A."""
    from projects.services import create_project_with_creator
    from projects.models import ProjectStatus, Stakeholder, StakeholderStatus
    from django.utils import timezone

    other = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-B-SCOPE',
        project_name='Other Scope B',
        employer='Employer B',
        start_date='2024-01-01',
    )
    other.status = ProjectStatus.ACTIVE
    other.scope_description = 'B'
    other.contract_amount = 1
    other.budget_approved_at = timezone.now()
    other.save()

    other_member, _ = ProjectMember.objects.get_or_create(
        project=other,
        user=user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if other_member.status != MemberStatus.ACTIVE:
        other_member.status = MemberStatus.ACTIVE
        other_member.save(update_fields=['status'])
    ProjectMemberRole.objects.get_or_create(member=other_member, role=finance_manager_role)

    foreign_stakeholder = Stakeholder.objects.create(
        project=other,
        name='B Stakeholder',
        status=StakeholderStatus.ACTIVE,
        created_by=other_user,
        updated_by=other_user,
    )

    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)

    url = f'/api/v1/projects/{project.id}/communication-plans/'
    resp = auth_client.post(
        url,
        {
            'audience': 'Team',
            'message': 'Weekly',
            'channel_type': 'email',
            'frequency': 'weekly',
            'stakeholder': str(foreign_stakeholder.id),
            'status': 'active',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'project_scope_mismatch' in str(resp.json())


@pytest.mark.django_db
def test_bulk_contract_items_rejects_foreign_activity(
    auth_client, project, user, other_user, project_manager_role, finance_manager_role
):
    from contracts.models import Contract, ContractType
    from projects.services import create_project_with_creator
    from projects.models import ProjectStatus, Activity
    from wbs.services import create_wbs_node
    from django.utils import timezone

    other = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-B-CI',
        project_name='Other Contract B',
        employer='Employer B2',
        start_date='2024-01-01',
    )
    other.status = ProjectStatus.ACTIVE
    other.scope_description = 'B'
    other.contract_amount = 1
    other.budget_approved_at = timezone.now()
    other.save()

    other_member, _ = ProjectMember.objects.get_or_create(
        project=other,
        user=user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if other_member.status != MemberStatus.ACTIVE:
        other_member.status = MemberStatus.ACTIVE
        other_member.save(update_fields=['status'])
    ProjectMemberRole.objects.get_or_create(member=other_member, role=finance_manager_role)

    wbs_b, _ = create_wbs_node(project_id=other.id, wbs_code='B1', wbs_name='Root B')
    foreign_activity = Activity.objects.create(
        project=other,
        wbs=wbs_b,
        activity_code='AB',
        activity_name='Foreign act',
        total_quantity=10,
        created_by=user,
        updated_by=user,
    )

    contract = Contract.objects.create(
        project=project,
        contract_number='C-SCOPE-A',
        contract_type=ContractType.MAIN,
        counterparty='CP',
        original_amount='1000',
        adjusted_amount='1000',
        created_by=user,
        updated_by=user,
    )

    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)

    url = f'/api/v1/projects/{project.id}/contracts/{contract.id}/items/'
    resp = auth_client.post(
        url,
        [{'activity': str(foreign_activity.id), 'boq_code': 'x', 'description': 'Line', 'unit_price': '1', 'quantity': '1'}],
        format='json',
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'project_scope_mismatch' in str(resp.json())


@pytest.mark.django_db
def test_workflow_start_rejects_foreign_definition(
    auth_client, project, user, other_user, project_manager_role, finance_manager_role
):
    from projects.services import create_project_with_creator
    from projects.models import ProjectStatus
    from django.utils import timezone

    from cost_control.models import (
        BudgetChangeRequest,
        BudgetChangeRequestStatus,
        BudgetVersion,
        BudgetVersionKind,
        BudgetVersionStatus,
    )
    from workflow.models import WorkflowDefinition, WorkflowDefinitionStatus, WorkflowType, WorkflowStage

    other = create_project_with_creator(
        creator=other_user,
        project_code='PRJ-B-WF',
        project_name='Other Workflow B',
        employer='Employer B3',
        start_date='2024-01-01',
    )
    other.status = ProjectStatus.ACTIVE
    other.scope_description = 'B'
    other.contract_amount = 1
    other.budget_approved_at = timezone.now()
    other.save()

    other_member, _ = ProjectMember.objects.get_or_create(
        project=other,
        user=user,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if other_member.status != MemberStatus.ACTIVE:
        other_member.status = MemberStatus.ACTIVE
        other_member.save(update_fields=['status'])
    ProjectMemberRole.objects.get_or_create(member=other_member, role=finance_manager_role)

    foreign_def = WorkflowDefinition.objects.create(
        project=other,
        name='Foreign wf',
        workflow_type=WorkflowType.BUDGET_CHANGE,
        status=WorkflowDefinitionStatus.ACTIVE,
        created_by=user,
        updated_by=user,
    )
    WorkflowStage.objects.create(
        definition=foreign_def,
        order=1,
        name='Only',
        approver_user=user,
    )

    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)

    version = BudgetVersion.objects.filter(project_id=project.id, is_deleted=False).first()
    if version is None:
        version = BudgetVersion.objects.create(
            project=project,
            kind=BudgetVersionKind.APPROVED,
            status=BudgetVersionStatus.APPROVED,
            version_number=1,
            currency='IRR',
            is_control=True,
            created_by=user,
            updated_by=user,
        )
    bcr = BudgetChangeRequest.objects.create(
        project=project,
        base_version=version,
        reason='scope',
        amount_delta=0,
        project_impact='none',
        status=BudgetChangeRequestStatus.DRAFT,
        requested_by=user,
        created_by=user,
        updated_by=user,
    )

    inst_url = f'/api/v1/projects/{project.id}/workflows/instances/'
    resp = auth_client.post(
        inst_url,
        {
            'definition': str(foreign_def.id),
            'subject_type': 'budget_change',
            'subject_id': str(bcr.id),
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'project_scope_mismatch' in str(resp.data)

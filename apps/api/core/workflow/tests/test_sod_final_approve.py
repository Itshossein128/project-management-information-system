"""A6-P4 workflow approve/reject: stage membership and no edit_project bypass."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from cost_control.models import (
    BudgetChangeRequest,
    BudgetChangeRequestStatus,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
)
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from workflow.models import WorkflowInstance, WorkflowInstanceStatus, WorkflowType

User = get_user_model()

DEFINITIONS = '/api/v1/projects/{project_id}/workflows/definitions/'
INSTANCES = '/api/v1/projects/{project_id}/workflows/instances/'


def _budget_change_request(project, user) -> BudgetChangeRequest:
    version = BudgetVersion.objects.filter(project=project, is_deleted=False).first()
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
    return BudgetChangeRequest.objects.create(
        project=project,
        base_version=version,
        reason='test',
        amount_delta=0,
        project_impact='none',
        status=BudgetChangeRequestStatus.DRAFT,
        requested_by=user,
        created_by=user,
        updated_by=user,
    )


def _activate_single_stage_def(
    auth_client,
    project,
    *,
    approver_user,
    approver_role: str | None = None,
) -> str:
    """Create and activate a one-stage workflow; approver by user id and/or role name."""
    url = DEFINITIONS.format(project_id=project.id)
    stage = {
        'order': 1,
        'name': 'Gate',
        'approval_mode': 'any',
        'on_reject': 'stop',
    }
    if approver_user is not None:
        stage['approver_user'] = str(approver_user.id)
    if approver_role:
        stage['approver_role'] = approver_role
    resp = auth_client.post(
        url,
        {
            'name': 'SoD test flow',
            'workflow_type': WorkflowType.BUDGET_CHANGE,
            'stages': [stage],
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    def_id = resp.data['id']
    act = auth_client.post(f'{url}{def_id}/activate/', {}, format='json')
    assert act.status_code == status.HTTP_200_OK, act.content
    return def_id


@pytest.mark.django_db
def test_approve_denied_when_wrong_stage(auth_client, project, user, other_user, project_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)

    def_id = _activate_single_stage_def(auth_client, project, approver_user=other_user)
    bcr = _budget_change_request(project, user)

    inst_url = INSTANCES.format(project_id=project.id)
    start = auth_client.post(
        inst_url,
        {
            'definition': def_id,
            'subject_type': 'budget_change',
            'subject_id': str(bcr.id),
        },
        format='json',
    )
    assert start.status_code == status.HTTP_201_CREATED, start.content
    inst_id = start.data['id']

    approve = auth_client.post(f'{inst_url}{inst_id}/approve/', {'comment': 'x'}, format='json')
    assert approve.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_approve_denied_when_member_inactive(
    auth_client, project, user, other_user, project_manager_role, finance_manager_role,
):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)
    fm_member = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=fm_member, role=finance_manager_role)

    def_id = _activate_single_stage_def(auth_client, project, approver_user=None, approver_role='finance_manager')
    bcr = _budget_change_request(project, user)

    inst_url = INSTANCES.format(project_id=project.id)
    start = auth_client.post(
        inst_url,
        {
            'definition': def_id,
            'subject_type': 'budget_change',
            'subject_id': str(bcr.id),
        },
        format='json',
    )
    assert start.status_code == status.HTTP_201_CREATED, start.content
    inst_id = start.data['id']

    fm_member.status = MemberStatus.INACTIVE
    fm_member.save(update_fields=['status'])

    other_client = auth_client
    other_client.force_authenticate(user=other_user)
    approve = other_client.post(f'{inst_url}{inst_id}/approve/', {'comment': 'x'}, format='json')
    assert approve.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_approve_denied_when_not_project_member(
    auth_client, project, user, other_user, project_manager_role, finance_manager_role,
):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)
    fm_member = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=fm_member, role=finance_manager_role)

    def_id = _activate_single_stage_def(auth_client, project, approver_user=None, approver_role='finance_manager')
    bcr = _budget_change_request(project, user)

    inst_url = INSTANCES.format(project_id=project.id)
    start = auth_client.post(
        inst_url,
        {
            'definition': def_id,
            'subject_type': 'budget_change',
            'subject_id': str(bcr.id),
        },
        format='json',
    )
    assert start.status_code == status.HTTP_201_CREATED, start.content
    inst_id = start.data['id']

    fm_member.delete()

    other_client = auth_client
    other_client.force_authenticate(user=other_user)
    approve = other_client.post(f'{inst_url}{inst_id}/approve/', {'comment': 'x'}, format='json')
    assert approve.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_edit_project_cannot_bypass_wrong_stage_for_reject(auth_client, project, user, other_user, project_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.get_or_create(member=member, role=project_manager_role)

    def_id = _activate_single_stage_def(auth_client, project, approver_user=other_user)
    bcr = _budget_change_request(project, user)

    inst_url = INSTANCES.format(project_id=project.id)
    start = auth_client.post(
        inst_url,
        {
            'definition': def_id,
            'subject_type': 'budget_change',
            'subject_id': str(bcr.id),
        },
        format='json',
    )
    assert start.status_code == status.HTTP_201_CREATED, start.content
    inst_id = start.data['id']

    reject = auth_client.post(f'{inst_url}{inst_id}/reject/', {'comment': 'no'}, format='json')
    assert reject.status_code == status.HTTP_403_FORBIDDEN
    inst = WorkflowInstance.objects.get(pk=inst_id)
    assert inst.status == WorkflowInstanceStatus.IN_PROGRESS

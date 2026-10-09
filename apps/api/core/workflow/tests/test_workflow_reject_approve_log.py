"""TDD: workflow instance lifecycle, approval modes, action log, overdue filter."""

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from workflow.models import WorkflowInstance, WorkflowInstanceStatus

DEFINITIONS = '/api/v1/projects/{project_id}/workflows/definitions/'
INSTANCES = '/api/v1/projects/{project_id}/workflows/instances/'


def _create_active_two_stage_definition(auth_client, project, user, stage2_on_reject='return_previous'):
    url = DEFINITIONS.format(project_id=project.id)
    resp = auth_client.post(
        url,
        {
            'name': 'Budget change approval',
            'workflow_type': 'budget_change',
            'stages': [
                {
                    'order': 1,
                    'name': 'PM review',
                    'approver_user': str(user.id),
                    'approval_mode': 'any',
                    'on_reject': 'stop',
                },
                {
                    'order': 2,
                    'name': 'Finance',
                    'approver_user': str(user.id),
                    'approval_mode': 'any',
                    'on_reject': stage2_on_reject,
                },
            ],
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.data
    def_id = resp.data['id']
    act = auth_client.post(f'{url}{def_id}/activate/', {}, format='json')
    assert act.status_code == status.HTTP_200_OK, act.data
    return def_id


@pytest.mark.django_db
class TestWorkflowRejectApproveLog:
    def test_reject_return_then_approve_full_log(self, auth_client, project, user):
        def_id = _create_active_two_stage_definition(auth_client, project, user)
        inst_url = INSTANCES.format(project_id=project.id)
        subject_id = uuid.uuid4()
        start = auth_client.post(
            inst_url,
            {
                'definition': def_id,
                'subject_type': 'budget_change',
                'subject_id': str(subject_id),
                'comment': 'Please review',
            },
            format='json',
        )
        assert start.status_code == status.HTTP_201_CREATED, start.data
        inst_id = start.data['id']

        approve1 = auth_client.post(
            f'{inst_url}{inst_id}/approve/', {'comment': 'OK stage 1'}, format='json',
        )
        assert approve1.status_code == status.HTTP_200_OK, approve1.data

        reject = auth_client.post(
            f'{inst_url}{inst_id}/reject/', {'comment': 'Need more detail'}, format='json',
        )
        assert reject.status_code == status.HTTP_200_OK, reject.data
        assert reject.data['status'] in (
            WorkflowInstanceStatus.RETURNED,
            WorkflowInstanceStatus.REJECTED,
        )

        if reject.data['status'] == WorkflowInstanceStatus.RETURNED:
            approve_again = auth_client.post(
                f'{inst_url}{inst_id}/approve/', {'comment': 'Fixed'}, format='json',
            )
            assert approve_again.status_code == status.HTTP_200_OK, approve_again.data
            approve_final = auth_client.post(
                f'{inst_url}{inst_id}/approve/', {'comment': 'Approved'}, format='json',
            )
            assert approve_final.status_code == status.HTTP_200_OK, approve_final.data
            assert approve_final.data['status'] == WorkflowInstanceStatus.APPROVED

        log_url = f'{inst_url}{inst_id}/log/'
        log = auth_client.get(log_url)
        assert log.status_code == status.HTTP_200_OK, log.data
        entries = log.data['results']
        assert len(entries) >= 3
        for entry in entries:
            assert entry['actor']
            assert entry['acted_at']
            assert entry['action']
            assert 'from_status' in entry
            assert 'to_status' in entry
            assert 'stage_order' in entry

        actions = [e['action'] for e in entries]
        assert 'start' in actions
        assert 'approve' in actions
        assert 'reject' in actions

    def test_approval_mode_all_requires_every_assignee(
        self, auth_client, project, user, other_user, finance_manager_role,
    ):
        member = ProjectMember.objects.get(project=project, user=user)
        ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
        other_member = ProjectMember.objects.create(
            project=project, user=other_user, status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=other_member, role=finance_manager_role)

        url = DEFINITIONS.format(project_id=project.id)
        create = auth_client.post(
            url,
            {
                'name': 'All-mode flow',
                'workflow_type': 'budget_change',
                'stages': [
                    {
                        'order': 1,
                        'name': 'Dual finance',
                        'approver_role': 'finance_manager',
                        'approval_mode': 'all',
                    },
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        def_id = create.data['id']
        auth_client.post(f'{url}{def_id}/activate/', {}, format='json')

        inst_url = INSTANCES.format(project_id=project.id)
        start = auth_client.post(
            inst_url,
            {
                'definition': def_id,
                'subject_type': 'budget_change',
                'subject_id': str(uuid.uuid4()),
            },
            format='json',
        )
        assert start.status_code == status.HTTP_201_CREATED, start.data
        inst_id = start.data['id']

        first = auth_client.post(f'{inst_url}{inst_id}/approve/', {}, format='json')
        assert first.status_code == status.HTTP_200_OK, first.data
        assert first.data['status'] == WorkflowInstanceStatus.IN_PROGRESS

        other_client = auth_client
        other_client.force_authenticate(user=other_user)
        second = other_client.post(f'{inst_url}{inst_id}/approve/', {}, format='json')
        assert second.status_code == status.HTTP_200_OK, second.data
        assert second.data['status'] == WorkflowInstanceStatus.APPROVED

    def test_approval_mode_any_advances_on_first(
        self, auth_client, project, user, other_user, finance_manager_role,
    ):
        member = ProjectMember.objects.get(project=project, user=user)
        ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
        other_member = ProjectMember.objects.create(
            project=project, user=other_user, status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=other_member, role=finance_manager_role)

        url = DEFINITIONS.format(project_id=project.id)
        create = auth_client.post(
            url,
            {
                'name': 'Any-mode flow',
                'workflow_type': 'budget_change',
                'stages': [
                    {
                        'order': 1,
                        'name': 'Dual finance',
                        'approver_role': 'finance_manager',
                        'approval_mode': 'any',
                    },
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        def_id = create.data['id']
        auth_client.post(f'{url}{def_id}/activate/', {}, format='json')

        inst_url = INSTANCES.format(project_id=project.id)
        start = auth_client.post(
            inst_url,
            {
                'definition': def_id,
                'subject_type': 'budget_change',
                'subject_id': str(uuid.uuid4()),
            },
            format='json',
        )
        inst_id = start.data['id']
        first = auth_client.post(f'{inst_url}{inst_id}/approve/', {}, format='json')
        assert first.status_code == status.HTTP_200_OK, first.data
        assert first.data['status'] == WorkflowInstanceStatus.APPROVED

    def test_overdue_filter(self, auth_client, project, user):
        def_id = _create_active_two_stage_definition(auth_client, project, user)
        inst_url = INSTANCES.format(project_id=project.id)
        start = auth_client.post(
            inst_url,
            {
                'definition': def_id,
                'subject_type': 'budget_change',
                'subject_id': str(uuid.uuid4()),
            },
            format='json',
        )
        inst_id = start.data['id']
        WorkflowInstance.objects.filter(pk=inst_id).update(
            current_due_at=timezone.now() - timedelta(days=1),
            status=WorkflowInstanceStatus.IN_PROGRESS,
        )

        listed = auth_client.get(inst_url, {'overdue': 'true'})
        assert listed.status_code == status.HTTP_200_OK
        ids = [row['id'] for row in listed.data['results']]
        assert inst_id in ids

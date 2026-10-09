"""TDD: workflow definition activate gate and budget_change sample."""

import pytest
from rest_framework import status

DEFINITIONS = '/api/v1/projects/{project_id}/workflows/definitions/'


def _definition_payload(user, stages, **overrides):
    data = {
        'name': 'Budget change approval',
        'workflow_type': 'budget_change',
        'description': 'Sample FR-COL flow',
        'stages': stages,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestWorkflowActivateGate:
    def test_activate_incomplete_stages_rejected(self, auth_client, project, user):
        url = DEFINITIONS.format(project_id=project.id)
        create = auth_client.post(
            url,
            _definition_payload(
                user,
                stages=[
                    {
                        'order': 1,
                        'name': 'PM review',
                        'approver_user': str(user.id),
                        'approval_mode': 'any',
                    },
                    {
                        'order': 2,
                        'name': 'Finance',
                        'approver_user': None,
                        'approver_role': '',
                        'approval_mode': 'any',
                    },
                ],
            ),
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        def_id = create.data['id']
        activate_url = f'{url}{def_id}/activate/'
        resp = auth_client.post(activate_url, {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'incomplete_stages'

    def test_activate_valid_budget_change_definition(self, auth_client, project, user):
        url = DEFINITIONS.format(project_id=project.id)
        create = auth_client.post(
            url,
            _definition_payload(
                user,
                stages=[
                    {
                        'order': 1,
                        'name': 'PM review',
                        'approver_user': str(user.id),
                        'approval_mode': 'any',
                        'on_reject': 'stop',
                        'deadline_days': 3,
                    },
                    {
                        'order': 2,
                        'name': 'Finance approve',
                        'approver_user': str(user.id),
                        'approver_role': 'finance_manager',
                        'approval_mode': 'all',
                        'on_reject': 'return_previous',
                        'deadline_days': 5,
                    },
                ],
            ),
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        def_id = create.data['id']
        activate_url = f'{url}{def_id}/activate/'
        resp = auth_client.post(activate_url, {}, format='json')
        assert resp.status_code == status.HTTP_200_OK, resp.data
        assert resp.data['status'] == 'active'

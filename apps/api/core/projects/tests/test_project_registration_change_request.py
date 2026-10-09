import pytest
from rest_framework import status


@pytest.mark.django_db
class TestProjectRegistrationChangeRequest:
    def test_protected_patch_blocked_when_active(self, auth_client, project):
        response = auth_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'employer': 'New Employer Name'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        code = response.data.get('error', {}).get('code') or response.data.get('code')
        assert code == 'protected_field_requires_change_request'

    def test_change_request_lifecycle(self, auth_client, project):
        base = f'/api/v1/projects/{project.id}/change-requests/'
        create = auth_client.post(
            base,
            {
                'reason': 'Correct employer legal name for contract',
                'proposed_changes': {'employer': 'Legal Employer LLC'},
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        cr_id = create.data['id']
        assert create.data['status'] == 'draft'

        dup = auth_client.post(
            base,
            {
                'reason': 'Another open request should fail now',
                'proposed_changes': {'employer': 'Other'},
            },
            format='json',
        )
        assert dup.status_code == status.HTTP_409_CONFLICT

        submit = auth_client.post(f'{base}{cr_id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == 'submitted'
        assert submit.data['previous_values'].get('employer') == project.employer

        approve = auth_client.post(f'{base}{cr_id}/approve/')
        assert approve.status_code == status.HTTP_200_OK
        assert approve.data['status'] == 'approved'

        detail = auth_client.get(f'/api/v1/projects/{project.id}/')
        assert detail.data['employer'] == 'Legal Employer LLC'

    def test_reject_leaves_project_unchanged(self, auth_client, project):
        original = project.employer
        base = f'/api/v1/projects/{project.id}/change-requests/'
        create = auth_client.post(
            base,
            {
                'reason': 'Attempt to change budget ceiling amount',
                'proposed_changes': {'contract_amount': '99999.00'},
            },
            format='json',
        )
        cr_id = create.data['id']
        auth_client.post(f'{base}{cr_id}/submit/')
        reject = auth_client.post(f'{base}{cr_id}/reject/', {'decision_notes': 'No'}, format='json')
        assert reject.status_code == status.HTTP_200_OK
        assert reject.data['status'] == 'rejected'
        detail = auth_client.get(f'/api/v1/projects/{project.id}/')
        assert detail.data['employer'] == original
        assert float(detail.data['contract_amount']) == float(project.contract_amount)

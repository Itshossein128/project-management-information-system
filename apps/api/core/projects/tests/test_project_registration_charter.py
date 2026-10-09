import pytest
from rest_framework import status

from projects.services import create_project_with_creator


@pytest.mark.django_db
class TestProjectRegistrationCharter:
    def test_charter_upsert_and_get(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='CHR-001',
            project_name='Charter',
            employer='E',
            start_date='2024-01-01',
        )
        url = f'/api/v1/projects/{project.id}/kickoff-charter/'
        missing = auth_client.get(url)
        assert missing.status_code == status.HTTP_404_NOT_FOUND

        payload = {
            'justification': 'Why',
            'success_criteria': 'Done when X',
            'constraints': 'Budget',
            'assumptions': 'Access',
            'key_stakeholders_summary': 'Owner, PM',
            'pm_authority': 'Full site authority',
        }
        put = auth_client.put(url, payload, format='json')
        assert put.status_code == status.HTTP_200_OK
        for key, value in payload.items():
            assert put.data[key] == value

        got = auth_client.get(url)
        assert got.status_code == status.HTTP_200_OK
        assert got.data['success_criteria'] == 'Done when X'

        patch = auth_client.patch(url, {'assumptions': 'Updated'}, format='json')
        assert patch.status_code == status.HTTP_200_OK
        assert patch.data['assumptions'] == 'Updated'
        assert patch.data['justification'] == 'Why'

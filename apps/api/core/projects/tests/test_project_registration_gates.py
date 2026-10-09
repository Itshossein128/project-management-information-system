import pytest
from rest_framework import status

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.services import baseline_service


@pytest.mark.django_db
class TestProjectRegistrationGates:
    def test_draft_cannot_lock_baseline(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='GATE-001',
            project_name='Gate Draft',
            employer='E',
            start_date='2024-01-01',
        )
        assert project.status == ProjectStatus.DRAFT
        with pytest.raises(Exception) as exc:
            bl = baseline_service.create_baseline_snapshot(
                project_id=project.id,
                version_name='v1',
                user=user,
                is_locked=True,
            )
            del bl
        assert 'project_not_active_for_baseline' in str(exc.value) or getattr(
            exc.value, 'default_code', '',
        ) == 'project_not_active_for_baseline'

    def test_pending_cannot_create_commitment(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='GATE-002',
            project_name='Gate Pending',
            employer='E',
            start_date='2024-01-01',
        )
        auth_client.post(f'/api/v1/projects/{project.id}/submit/')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/commitments/',
            {
                'commitment_number': 'CM-1',
                'amount': '100',
                'commitment_date': '2024-01-15',
                'currency': 'IRR',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'commitment' in str(response.data).lower() or response.data.get('code') == 'project_not_active_for_commitment'

    def test_suspended_cannot_lock_baseline(self, auth_client, project, user):
        auth_client.post(f'/api/v1/projects/{project.id}/suspend/')
        with pytest.raises(Exception) as exc:
            baseline_service.create_baseline_snapshot(
                project_id=project.id,
                version_name='v-sus',
                user=user,
                is_locked=True,
            )
        assert 'project_not_active_for_baseline' in str(exc.value) or getattr(
            exc.value, 'default_code', '',
        ) == 'project_not_active_for_baseline'

    def test_active_can_lock_baseline(self, project, user):
        bl = baseline_service.create_baseline_snapshot(
            project_id=project.id,
            version_name='v-ok',
            user=user,
            is_locked=True,
        )
        assert bl.is_locked is True

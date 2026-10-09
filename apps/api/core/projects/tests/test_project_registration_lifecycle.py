import pytest
from rest_framework import status

from permissions.constants import PERMISSIONS
from projects.models import Project, ProjectStatus
from projects.services import create_project_with_creator


@pytest.mark.django_db
class TestProjectRegistrationLifecycle:
    def test_status_choices_include_lifecycle(self):
        values = set(ProjectStatus.values)
        for code in (
            'draft',
            'pending_approval',
            'active',
            'suspended',
            'completed',
            'archived',
        ):
            assert code in values

    def test_create_defaults_to_draft(self, auth_client):
        response = auth_client.post(
            '/api/v1/projects/',
            {
                'project_code': 'DRAFT-001',
                'project_name': 'Draft Project',
                'employer': 'Employer',
                'start_date': '2024-06-01',
                'purpose': 'Build',
                'scope_description': 'Scope A',
                'main_deliverables': 'Deliverable',
                'contract_number': 'C-1',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'draft'
        assert response.data['purpose'] == 'Build'
        assert response.data['scope_description'] == 'Scope A'
        assert response.data['main_deliverables'] == 'Deliverable'
        assert response.data['contract_number'] == 'C-1'
        assert response.data.get('budget_approved_at') in (None, '')

    def test_approve_project_permission_exists(self):
        assert 'approve_project' in PERMISSIONS

    def test_submit_and_approve_with_gates(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='LIFE-001',
            project_name='Lifecycle',
            employer='E',
            start_date='2024-01-01',
        )
        assert project.status == ProjectStatus.DRAFT
        # Clear auto-assigned PM to test gate
        project.project_manager = None
        project.scope_description = ''
        project.contract_amount = None
        project.save()

        submit = auth_client.post(f'/api/v1/projects/{project.id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == 'pending_approval'

        bad = auth_client.post(f'/api/v1/projects/{project.id}/approve/')
        assert bad.status_code == status.HTTP_400_BAD_REQUEST
        err = bad.data.get('error') or {}
        assert err.get('code') == 'activation_gates_failed' or 'activation_gates' in str(bad.data)
        details = err.get('details') or bad.data
        missing = details.get('missing') if isinstance(details, dict) else None
        if missing is None and isinstance(details, dict):
            nested = details.get('detail')
            if isinstance(nested, dict):
                missing = nested.get('missing')
        assert missing is None or 'project_manager' in missing

        project.refresh_from_db()
        project.project_manager = user
        project.scope_description = 'Full scope'
        project.contract_amount = 1000
        project.save()

        ok = auth_client.post(f'/api/v1/projects/{project.id}/approve/')
        assert ok.status_code == status.HTTP_200_OK
        assert ok.data['status'] == 'active'
        assert ok.data['budget_approved_at']

    def test_reject_returns_to_draft(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='LIFE-002',
            project_name='Reject',
            employer='E',
            start_date='2024-01-01',
        )
        auth_client.post(f'/api/v1/projects/{project.id}/submit/')
        response = auth_client.post(f'/api/v1/projects/{project.id}/reject/', {'reason': 'Incomplete'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'draft'

    def test_suspend_resume_complete_archive(self, auth_client, project):
        assert project.status == ProjectStatus.ACTIVE
        s = auth_client.post(f'/api/v1/projects/{project.id}/suspend/')
        assert s.status_code == status.HTTP_200_OK
        assert s.data['status'] == 'suspended'
        r = auth_client.post(f'/api/v1/projects/{project.id}/resume/')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['status'] == 'active'
        c = auth_client.post(f'/api/v1/projects/{project.id}/complete/')
        assert c.status_code == status.HTTP_200_OK
        assert c.data['status'] == 'completed'
        a = auth_client.post(f'/api/v1/projects/{project.id}/archive/')
        assert a.status_code == status.HTTP_200_OK
        assert a.data['status'] == 'archived'
        patch = auth_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'contractor': 'X'},
            format='json',
        )
        assert patch.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_transition(self, auth_client, user):
        project = create_project_with_creator(
            creator=user,
            project_code='LIFE-003',
            project_name='Bad',
            employer='E',
            start_date='2024-01-01',
        )
        response = auth_client.post(f'/api/v1/projects/{project.id}/approve/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_code(self, auth_client, project):
        response = auth_client.post(
            '/api/v1/projects/',
            {
                'project_code': project.project_code,
                'project_name': 'Dup',
                'employer': 'E',
                'start_date': '2024-06-01',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

import pytest
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember, Role
from projects.models import Project


@pytest.mark.django_db
class TestProjectList:
    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_only_sees_member_projects(self, auth_client, user, other_user, project):
        Project.objects.create(
            project_code='OTHER',
            project_name='Other Project',
            employer='X',
            start_date='2024-01-01',
        )
        response = auth_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        codes = [p['project_code'] for p in response.data['results']]
        assert 'PRJ-001' in codes
        assert 'OTHER' not in codes

    def test_creator_is_project_manager(self, project, user):
        member = ProjectMember.objects.get(project=project, user=user)
        roles = list(member.member_roles.values_list('role__role_name', flat=True))
        assert 'project_manager' in roles


@pytest.mark.django_db
class TestProjectCreate:
    def test_create_project(self, auth_client, user):
        response = auth_client.post(
            '/api/v1/projects/',
            {
                'project_code': 'NEW-001',
                'project_name': 'New Project',
                'employer': 'Employer',
                'start_date': '2024-06-01',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert ProjectMember.objects.filter(
            project_id=response.data['project_id'],
            user=user,
            status=MemberStatus.ACTIVE,
        ).exists()


@pytest.mark.django_db
class TestProjectPatch:
    def test_edit_with_permission(self, auth_client, project):
        response = auth_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'project_name': 'Updated Name'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.project_name == 'Updated Name'

    def test_edit_without_permission(self, api_client, other_user, project, member):
        api_client.force_authenticate(user=other_user)
        response = api_client.patch(
            f'/api/v1/projects/{project.id}/',
            {'project_name': 'Hacked'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_inactive_member_cannot_access(self, api_client, other_user, project, member):
        member.status = MemberStatus.INACTIVE
        member.save()
        api_client.force_authenticate(user=other_user)
        response = api_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

import pytest
from django.contrib.auth.models import Group
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

    @pytest.mark.parametrize('search', ['PRJ-001', 'test project', 'Employer', 'پروژه'])
    def test_search_matches_code_name_or_employer(self, auth_client, project, search):
        project.project_name = 'Test Project پروژه'
        project.employer = 'Employer'
        project.save()
        response = auth_client.get('/api/v1/projects/', {'search': search})
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_search_excludes_nonmatches_and_nonmembers(self, auth_client, project):
        Project.objects.create(
            project_code='HIDDEN', project_name='Secret Needle',
            employer='X', start_date='2024-01-01',
        )
        response = auth_client.get('/api/v1/projects/', {'search': 'Needle'})
        assert response.status_code == 200
        assert response.data['count'] == 0

    def test_search_and_status_apply_before_pagination(self, api_client, user, project):
        user.is_superuser = True
        user.save()
        api_client.force_authenticate(user=user)
        for code in ['SEARCH-B', 'SEARCH-A', 'SEARCH-C']:
            Project.objects.create(
                project_code=code, project_name='Matching project', status='active',
                employer='X', start_date='2024-01-01',
            )
        params = {'search': 'SEARCH-', 'status': 'active', 'page_size': 2}
        first = api_client.get('/api/v1/projects/', params).data
        second = api_client.get('/api/v1/projects/', {**params, 'page': 2}).data
        assert first['count'] == second['count'] == 3
        assert len(first['results']) == 2
        assert len(second['results']) == 1
        assert {p['project_code'] for p in first['results'] + second['results']} == {
            'SEARCH-A', 'SEARCH-B', 'SEARCH-C',
        }
        assert first['next'] and second['previous']


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
class TestProjectFromTemplate:
    def test_from_template_attaches_creator_as_member(self, api_client, user):
        Group.objects.get_or_create(name='business-setup')
        user.groups.add(Group.objects.get(name='business-setup'))
        api_client.force_authenticate(user=user)

        response = api_client.post(
            '/api/v1/projects/from_template/',
            {
                'name': 'Warehouse From Template',
                'slug': 'WH-TMPL-001',
                'template': 'warehouse',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data['project_id']
        assert ProjectMember.objects.filter(
            project_id=project_id,
            user=user,
            status=MemberStatus.ACTIVE,
        ).exists()

        list_response = api_client.get('/api/v1/projects/')
        assert list_response.status_code == status.HTTP_200_OK
        codes = [p['project_code'] for p in list_response.data['results']]
        assert 'WH-TMPL-001' in codes

        detail = api_client.get(f'/api/v1/projects/{project_id}/')
        assert detail.status_code == status.HTTP_200_OK


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
            {'project_name': 'Unauthorized Edit'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        project.refresh_from_db()
        assert project.project_name != 'Unauthorized Edit'

    def test_inactive_member_cannot_access(self, api_client, other_user, project, member):
        member.status = MemberStatus.INACTIVE
        member.save()
        api_client.force_authenticate(user=other_user)
        response = api_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN



@pytest.mark.django_db
class TestProjectDelete:
    def test_delete_project_success(self, auth_client, project):
        response = auth_client.delete(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(id=project.id).exists()

    def test_delete_project_without_permission(self, api_client, other_user, project, member):
        api_client.force_authenticate(user=other_user)
        response = api_client.delete(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Project.objects.filter(id=project.id).exists()

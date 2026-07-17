import pytest
from django.contrib.auth.models import Group

from master_data.models import Role


@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(
        username='adminuser',
        mobile='+989121234569',
        full_name='Admin User',
        password='testpass123',
    )
    admin_group, _ = Group.objects.get_or_create(name='admin')
    u.groups.add(admin_group)
    return u


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.mark.django_db
class TestRoleAPI:
    def test_list_roles_authenticated(self, auth_client):
        response = auth_client.get('/api/v1/roles/')
        assert response.status_code == 200
        assert len(response.data) >= 7
        assert 'is_system' in response.data[0]
        assert 'permissions' in response.data[0]

    def test_permission_catalog(self, auth_client):
        response = auth_client.get('/api/v1/permissions/')
        assert response.status_code == 200
        assert any(item['codename'] == 'view_wbs' for item in response.data)

    def test_create_custom_role(self, admin_client):
        response = admin_client.post(
            '/api/v1/roles/',
            {
                'role_name': 'custom_inspector',
                'description': 'Custom inspector role',
                'permissions': ['view_project', 'view_wbs', 'view_reports'],
            },
            format='json',
        )
        assert response.status_code == 201
        assert response.data['role_name'] == 'custom_inspector'
        assert response.data['is_system'] is False
        assert set(response.data['permissions']) == {'view_project', 'view_wbs', 'view_reports'}

    def test_create_role_requires_admin(self, auth_client):
        response = auth_client.post(
            '/api/v1/roles/',
            {'role_name': 'blocked_role', 'permissions': ['view_project']},
            format='json',
        )
        assert response.status_code == 403

    def test_cannot_delete_system_role(self, admin_client, project_manager_role):
        response = admin_client.delete(f'/api/v1/roles/{project_manager_role.id}/')
        assert response.status_code == 403

    def test_delete_custom_role(self, admin_client):
        role = Role.objects.create(role_name='temp_role', description='temp')
        response = admin_client.delete(f'/api/v1/roles/{role.id}/')
        assert response.status_code == 204
        assert not Role.objects.filter(pk=role.id).exists()

    def test_cannot_modify_system_role(self, admin_client, viewer_role):
        response = admin_client.patch(
            f'/api/v1/roles/{viewer_role.id}/',
            {'description': 'Changed'},
            format='json',
        )
        assert response.status_code == 403

    def test_update_custom_role_permissions(self, admin_client):
        role = Role.objects.create(role_name='perm_role', description='')
        response = admin_client.put(
            f'/api/v1/roles/{role.id}/permissions/',
            {'permissions': ['view_project', 'edit_wbs']},
            format='json',
        )
        assert response.status_code == 200
        assert set(response.data['permissions']) == {'view_project', 'edit_wbs'}

    def test_cannot_modify_system_role_permissions(self, admin_client, viewer_role):
        response = admin_client.put(
            f'/api/v1/roles/{viewer_role.id}/permissions/',
            {'permissions': ['view_project']},
            format='json',
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestMemberPermissionReset:
    def test_delete_permission_override_resets_to_inherited(
        self, auth_client, project, user, other_user, member,
    ):
        from permissions.services import set_permission_override

        set_permission_override(member, 'view_wbs', False)
        response = auth_client.delete(
            f'/api/v1/projects/{project.id}/members/{other_user.id}/permissions/'
            f'?permission_codename=view_wbs',
        )
        assert response.status_code == 200
        effective = response.data['effective']
        assert effective['view_wbs'] is True

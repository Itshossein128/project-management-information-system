import pytest

from master_data.models import ProjectMemberPermissionOverride
from permissions.services import set_permission_override


@pytest.mark.django_db
class TestPermissions:
    def test_role_grants_access(self, auth_client, project, user):
        response = auth_client.get(f'/api/v1/projects/{project.id}/wbs/')
        assert response.status_code == 200

    def test_deny_override_blocks_role_permission(self, auth_client, project, user):
        member = project.members.get(user=user)
        set_permission_override(member, 'edit_wbs', False)
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {'wbs_code': '9', 'wbs_name': 'Blocked'},
            format='json',
        )
        assert response.status_code == 403

    def test_grant_override_allows_without_role_permission(self, api_client, other_user, project, member):
        set_permission_override(member, 'edit_wbs', True)
        api_client.force_authenticate(user=other_user)
        response = api_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {'wbs_code': '1', 'wbs_name': 'Root'},
            format='json',
        )
        assert response.status_code == 201

    def test_project_manager_has_all_permissions(self, project, user):
        member = project.members.get(user=user)
        from permissions.constants import ALL_PERMISSION_CODENAMES

        for codename in ALL_PERMISSION_CODENAMES:
            assert member.has_permission(codename) is True

    def test_custom_override_deny(self, member):
        set_permission_override(member, 'view_project', False)
        assert member.has_permission('view_project') is False

    def test_custom_override_grant(self, member):
        member.member_roles.all().delete()
        set_permission_override(member, 'view_wbs', True)
        assert member.has_permission('view_wbs') is True

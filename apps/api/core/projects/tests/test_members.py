"""Project member API tests."""

import pytest
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember


@pytest.fixture
def members_base(project):
    return f'/api/v1/projects/{project.id}/members/'


@pytest.mark.django_db
class TestProjectMembersAPI:
    def test_list_members(self, auth_client, members_base, member):
        response = auth_client.get(members_base)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_add_member(self, auth_client, members_base, other_user, viewer_role):
        response = auth_client.post(
            members_base,
            {
                'user_id': str(other_user.id),
                'role_ids': [str(viewer_role.id)],
            },
            format='json',
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert ProjectMember.objects.filter(user=other_user).exists()

    def test_update_member_status(self, auth_client, members_base, member):
        response = auth_client.patch(
            f'{members_base}{member.user_id}/',
            {'status': MemberStatus.INACTIVE},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        member.refresh_from_db()
        assert member.status == MemberStatus.INACTIVE

    def test_member_can_read_effective_permissions(self, api_client, project, other_user, member):
        api_client.force_authenticate(user=other_user)
        response = api_client.get(
            f'/api/v1/projects/{project.id}/members/{other_user.id}/permissions/',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'effective' in response.data
        assert response.data['effective']['view_wbs'] is True

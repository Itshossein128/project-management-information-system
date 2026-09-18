"""Block CRUD API tests."""

import pytest
from django.urls import reverse
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, RolePermission
from procurement.models import Block, RequisitionHeader


@pytest.fixture
def blocks_url(project):
    return reverse('procurement-block-list', kwargs={'project_pk': project.id})


@pytest.fixture
def block_detail_url(project, block):
    return reverse(
        'procurement-block-detail',
        kwargs={'project_pk': project.id, 'pk': block.id},
    )


@pytest.fixture
def block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-01',
        block_name='Block One',
        budget=100000,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestBlockCRUD:
    def test_list_blocks(self, auth_client, project, block, blocks_url):
        resp = auth_client.get(blocks_url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data if isinstance(resp.data, list) else resp.data['results']
        assert len(results) == 1
        assert results[0]['block_code'] == 'BLK-01'

    def test_create_block(self, auth_client, project, blocks_url):
        resp = auth_client.post(
            blocks_url,
            {
                'block_code': 'BLK-NEW',
                'block_name': 'New Block',
                'budget': '250000.00',
                'is_active': True,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['block_code'] == 'BLK-NEW'
        assert str(resp.data['project']) == str(project.id)
        assert Block.objects.filter(project=project, block_code='BLK-NEW').exists()

    def test_create_block_with_wbs(self, auth_client, project, wbs, blocks_url):
        resp = auth_client.post(
            blocks_url,
            {
                'block_code': 'BLK-WBS',
                'block_name': 'WBS Block',
                'wbs': str(wbs.id),
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert str(resp.data['wbs']) == str(wbs.id)
        assert resp.data['wbs_code'] == '1'

    def test_update_block(self, auth_client, block, block_detail_url):
        resp = auth_client.patch(
            block_detail_url,
            {'block_name': 'Updated Name', 'is_active': False},
            format='json',
        )
        assert resp.status_code == status.HTTP_200_OK
        block.refresh_from_db()
        assert block.block_name == 'Updated Name'
        assert block.is_active is False

    def test_soft_delete_block(self, auth_client, block, block_detail_url):
        resp = auth_client.delete(block_detail_url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        block.refresh_from_db()
        assert block.is_deleted is True

    def test_duplicate_block_code_rejected(self, auth_client, block, blocks_url):
        resp = auth_client.post(
            blocks_url,
            {'block_code': 'BLK-01', 'block_name': 'Duplicate'},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        details = resp.data.get('error', {}).get('details', resp.data)
        assert 'block_code' in details

    def test_delete_block_with_requisitions_rejected(
        self, auth_client, project, block, block_detail_url, user
    ):
        RequisitionHeader.objects.create(
            project=project,
            block=block,
            requested_by=user,
            request_date='2026-01-01',
            created_by=user,
        )
        resp = auth_client.delete(block_detail_url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        block.refresh_from_db()
        assert block.is_deleted is False


@pytest.mark.django_db
class TestBlockPermissions:
    def test_list_requires_view_procurement(
        self, api_client, project, other_user, viewer_role, blocks_url
    ):
        member = ProjectMember.objects.create(
            project=project,
            user=other_user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=viewer_role)
        api_client.force_authenticate(user=other_user)
        resp = api_client.get(blocks_url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_requires_edit_reports(
        self, api_client, project, other_user, blocks_url
    ):
        from master_data.models import Role

        role, _ = Role.objects.get_or_create(role_name='procurement_only')
        RolePermission.objects.filter(role=role).delete()
        RolePermission.objects.create(role=role, permission_codename='view_procurement')
        RolePermission.objects.create(role=role, permission_codename='view_project')

        member = ProjectMember.objects.create(
            project=project,
            user=other_user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=role)
        api_client.force_authenticate(user=other_user)

        resp = api_client.post(
            blocks_url,
            {'block_code': 'BLK-X', 'block_name': 'X'},
            format='json',
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

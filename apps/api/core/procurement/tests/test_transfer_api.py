"""Internal transfer API: project authorization and related-object tenancy."""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, RolePermission
from procurement.models import Block, InternalTransfer
from projects.models import Project
from resources.models import Material


@pytest.fixture
def transfers_url(project):
    return reverse('procurement-transfer-list', kwargs={'project_pk': project.id})


@pytest.fixture
def source_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-SRC',
        block_name='Source',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def target_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-TGT',
        block_name='Target',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def material(db, project):
    return Material.objects.create(
        project=project,
        material_code='MAT-TR',
        material_name='Cement',
    )


@pytest.fixture
def other_project(db):
    return Project.objects.create(
        project_name='Other Project',
        project_code='PRJ-OTHER',
    )


@pytest.fixture
def foreign_block(db, other_project, user):
    return Block.objects.create(
        project=other_project,
        block_code='BLK-FOREIGN',
        block_name='Foreign Block',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def foreign_material(db, other_project):
    return Material.objects.create(
        project=other_project,
        material_code='MAT-FOREIGN',
        material_name='Foreign Cement',
    )


@pytest.mark.django_db
class TestTransferApiPermissions:
    def test_list_requires_authentication(self, api_client, transfers_url):
        resp = api_client.get(transfers_url)
        assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_list_requires_project_membership(self, api_client, other_user, transfers_url):
        api_client.force_authenticate(user=other_user)
        resp = api_client.get(transfers_url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_list_requires_view_procurement(
        self, api_client, project, other_user, viewer_role, transfers_url
    ):
        member = ProjectMember.objects.create(
            project=project,
            user=other_user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=viewer_role)
        api_client.force_authenticate(user=other_user)
        resp = api_client.get(transfers_url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_requires_edit_procurement(
        self,
        api_client,
        project,
        other_user,
        source_block,
        target_block,
        material,
        transfers_url,
    ):
        role, _ = Role.objects.get_or_create(role_name='procurement_viewer_only')
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
            transfers_url,
            {
                'source_block': str(source_block.id),
                'target_block': str(target_block.id),
                'material': str(material.id),
                'quantity': '10.0000',
                'reason': 'Surplus',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTransferApiTenancy:
    def test_create_transfer_same_project(
        self, auth_client, source_block, target_block, material, transfers_url
    ):
        resp = auth_client.post(
            transfers_url,
            {
                'source_block': str(source_block.id),
                'target_block': str(target_block.id),
                'material': str(material.id),
                'quantity': '12.5000',
                'reason': 'Move surplus cement',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert InternalTransfer.objects.filter(
            source_block=source_block,
            target_block=target_block,
            material=material,
        ).exists()

    @pytest.mark.parametrize('bad_qty', ['0', '0.0000', '-1.0000'])
    def test_create_rejects_non_positive_quantity(
        self, auth_client, source_block, target_block, material, transfers_url, bad_qty
    ):
        resp = auth_client.post(
            transfers_url,
            {
                'source_block': str(source_block.id),
                'target_block': str(target_block.id),
                'material': str(material.id),
                'quantity': bad_qty,
                'reason': 'Invalid quantity',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        details = resp.data.get('error', {}).get('details', resp.data)
        assert 'quantity' in details
        assert not InternalTransfer.objects.filter(reason='Invalid quantity').exists()

    def test_create_rejects_foreign_source_block(
        self, auth_client, foreign_block, target_block, material, transfers_url
    ):
        resp = auth_client.post(
            transfers_url,
            {
                'source_block': str(foreign_block.id),
                'target_block': str(target_block.id),
                'material': str(material.id),
                'quantity': '5.0000',
                'reason': 'Cross-project source',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        details = resp.data.get('error', {}).get('details', resp.data)
        assert 'source_block' in details

    def test_create_rejects_foreign_target_block(
        self, auth_client, source_block, foreign_block, material, transfers_url
    ):
        resp = auth_client.post(
            transfers_url,
            {
                'source_block': str(source_block.id),
                'target_block': str(foreign_block.id),
                'material': str(material.id),
                'quantity': '5.0000',
                'reason': 'Cross-project target',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        details = resp.data.get('error', {}).get('details', resp.data)
        assert 'target_block' in details

    def test_create_rejects_foreign_material(
        self, auth_client, source_block, target_block, foreign_material, transfers_url
    ):
        resp = auth_client.post(
            transfers_url,
            {
                'source_block': str(source_block.id),
                'target_block': str(target_block.id),
                'material': str(foreign_material.id),
                'quantity': '5.0000',
                'reason': 'Cross-project material',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        details = resp.data.get('error', {}).get('details', resp.data)
        assert 'material' in details

    def test_list_does_not_leak_other_project_transfers(
        self,
        auth_client,
        project,
        user,
        source_block,
        target_block,
        material,
        foreign_block,
        other_project,
        transfers_url,
    ):
        own = InternalTransfer.objects.create(
            source_block=source_block,
            target_block=target_block,
            material=material,
            quantity=Decimal('3.0000'),
            reason='Own transfer',
            created_by=user,
        )
        foreign_target = Block.objects.create(
            project=other_project,
            block_code='BLK-FOREIGN-TGT',
            block_name='Foreign Target',
            created_by=user,
            updated_by=user,
        )
        foreign_material = Material.objects.create(
            project=other_project,
            material_code='MAT-OTHER',
            material_name='Other Mat',
        )
        InternalTransfer.objects.create(
            source_block=foreign_block,
            target_block=foreign_target,
            material=foreign_material,
            quantity=Decimal('9.0000'),
            reason='Secret transfer',
            created_by=user,
        )

        resp = auth_client.get(transfers_url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data if isinstance(resp.data, list) else resp.data['results']
        ids = {str(row['id']) for row in results}
        assert str(own.id) in ids
        assert len(ids) == 1

    def test_non_member_cannot_list_via_known_project_id(
        self, api_client, other_user, user, source_block, target_block, material, transfers_url
    ):
        InternalTransfer.objects.create(
            source_block=source_block,
            target_block=target_block,
            material=material,
            quantity=Decimal('1.0000'),
            reason='Hidden',
            created_by=user,
        )
        api_client.force_authenticate(user=other_user)
        resp = api_client.get(transfers_url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

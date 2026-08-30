"""Tests for workshop block provisioning and API guards."""

import pytest
from django.urls import reverse
from rest_framework import status

from procurement.models import Block, BlockKind, WORKSHOP_BLOCK_CODE
from procurement.services.workshop_block_service import ensure_workshop_block


@pytest.mark.django_db
class TestEnsureWorkshopBlock:
    def test_creates_workshop_block(self, project, user):
        block = ensure_workshop_block(project, created_by=user)
        assert block.block_code == WORKSHOP_BLOCK_CODE
        assert block.block_name == 'کارگاه'
        assert block.block_kind == BlockKind.WORKSHOP
        assert block.project_id == project.id

    def test_idempotent(self, project, user):
        first = ensure_workshop_block(project, created_by=user)
        second = ensure_workshop_block(project, created_by=user)
        assert first.id == second.id
        assert Block.objects.filter(
            project=project,
            block_kind=BlockKind.WORKSHOP,
            is_deleted=False,
        ).count() == 1

    def test_auto_created_on_project_create(self, project):
        block = Block.objects.get(
            project=project,
            block_kind=BlockKind.WORKSHOP,
            is_deleted=False,
        )
        assert block.block_code == WORKSHOP_BLOCK_CODE


@pytest.fixture
def workshop_block(project, user):
    return ensure_workshop_block(project, created_by=user)


@pytest.fixture
def standard_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-STD',
        block_name='Standard Block',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def blocks_url(project):
    return reverse('procurement-block-list', kwargs={'project_pk': project.id})


@pytest.fixture
def workshop_block_detail_url(project, workshop_block):
    return reverse(
        'procurement-block-detail',
        kwargs={'project_pk': project.id, 'pk': workshop_block.id},
    )


@pytest.mark.django_db
class TestWorkshopBlockAPI:
    def test_excluded_from_default_list(self, auth_client, project, workshop_block, standard_block, blocks_url):
        resp = auth_client.get(blocks_url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data if isinstance(resp.data, list) else resp.data['results']
        codes = [row['block_code'] for row in results]
        assert WORKSHOP_BLOCK_CODE not in codes
        assert standard_block.block_code in codes

    def test_included_when_exclude_system_false(self, auth_client, workshop_block, blocks_url):
        resp = auth_client.get(blocks_url, {'exclude_system': 'false'})
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data if isinstance(resp.data, list) else resp.data['results']
        codes = [row['block_code'] for row in results]
        assert WORKSHOP_BLOCK_CODE in codes

    def test_cannot_delete_workshop_block(self, auth_client, workshop_block_detail_url, workshop_block):
        resp = auth_client.delete(workshop_block_detail_url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        workshop_block.refresh_from_db()
        assert workshop_block.is_deleted is False

    def test_cannot_update_workshop_block(self, auth_client, workshop_block_detail_url, workshop_block):
        resp = auth_client.patch(
            workshop_block_detail_url,
            {'block_name': 'Changed'},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        workshop_block.refresh_from_db()
        assert workshop_block.block_name == 'کارگاه'

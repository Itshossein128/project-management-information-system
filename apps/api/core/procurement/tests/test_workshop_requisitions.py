"""Tests for workshop-scoped requisitions."""

import pytest
from django.urls import reverse
from rest_framework import status

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from procurement.models import Block, BlockKind, RequisitionHeader, RequisitionScope, WORKSHOP_BLOCK_CODE
from procurement.services.workshop_block_service import ensure_workshop_block


@pytest.fixture
def material(db, project):
    from resources.models import Material

    return Material.objects.create(
        project=project,
        material_code='MAT-01',
        material_name='Cement',
        estimated_total_qty=1000,
    )


@pytest.fixture
def standard_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-A',
        block_name='Block A',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def requisitions_url(project):
    return reverse('procurement-req-list', kwargs={'project_pk': project.id})


@pytest.mark.django_db
class TestWorkshopRequisitions:
    def test_create_workshop_requisition_auto_assigns_block(
        self, auth_client, project, user, material, requisitions_url
    ):
        ensure_workshop_block(project, created_by=user)
        resp = auth_client.post(
            requisitions_url,
            {
                'project': str(project.id),
                'scope': RequisitionScope.WORKSHOP,
                'request_date': '2026-01-15',
                'items': [{'material': str(material.id), 'requested_qty': '10'}],
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        header = RequisitionHeader.objects.get(id=resp.data['id'])
        assert header.scope == RequisitionScope.WORKSHOP
        assert header.block.block_kind == BlockKind.WORKSHOP
        assert header.block.block_code == WORKSHOP_BLOCK_CODE

    def test_block_scope_rejects_workshop_block(
        self, auth_client, project, user, material, standard_block, requisitions_url
    ):
        workshop = ensure_workshop_block(project, created_by=user)
        resp = auth_client.post(
            requisitions_url,
            {
                'project': str(project.id),
                'scope': RequisitionScope.BLOCK,
                'block': str(workshop.id),
                'request_date': '2026-01-15',
                'items': [{'material': str(material.id), 'requested_qty': '5'}],
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_block_scope_requires_block(
        self, auth_client, project, material, requisitions_url
    ):
        resp = auth_client.post(
            requisitions_url,
            {
                'project': str(project.id),
                'scope': RequisitionScope.BLOCK,
                'request_date': '2026-01-15',
                'items': [{'material': str(material.id), 'requested_qty': '5'}],
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_filter_by_scope(
        self, auth_client, project, user, material, standard_block, requisitions_url
    ):
        workshop_block = ensure_workshop_block(project, created_by=user)
        RequisitionHeader.objects.create(
            project=project,
            block=standard_block,
            scope=RequisitionScope.BLOCK,
            requested_by=user,
            request_date='2026-01-01',
            created_by=user,
        )
        RequisitionHeader.objects.create(
            project=project,
            block=workshop_block,
            scope=RequisitionScope.WORKSHOP,
            requested_by=user,
            request_date='2026-01-02',
            created_by=user,
        )

        resp = auth_client.get(requisitions_url, {'scope': RequisitionScope.WORKSHOP})
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data if isinstance(resp.data, list) else resp.data['results']
        assert len(results) == 1
        assert results[0]['scope'] == RequisitionScope.WORKSHOP

    def test_workshop_supervisor_can_submit_draft(
        self, api_client, project, user, material, requisitions_url
    ):
        workshop_block = ensure_workshop_block(project, created_by=user)
        supervisor = user.__class__.objects.create_user(
            username='ws_super',
            password='pass',
        )
        role, _ = Role.objects.get_or_create(role_name='workshop_supervisor')
        member = ProjectMember.objects.create(
            project=project,
            user=supervisor,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=role)

        req = RequisitionHeader.objects.create(
            project=project,
            block=workshop_block,
            scope=RequisitionScope.WORKSHOP,
            requested_by=user,
            request_date='2026-01-01',
            created_by=user,
        )
        RequisitionHeader.objects.filter(pk=req.pk).update(status='draft')

        submit_url = reverse(
            'procurement-req-submit',
            kwargs={'project_pk': project.id, 'pk': req.id},
        )
        api_client.force_authenticate(user=supervisor)
        resp = api_client.post(submit_url, {'comments': 'submit'}, format='json')
        assert resp.status_code == status.HTTP_200_OK, resp.data

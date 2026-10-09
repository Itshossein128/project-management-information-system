"""US4: create commitment from approved requisition."""

from datetime import date

import pytest
from rest_framework import status

from cost_control.cbs_services import create_cbs_node
from procurement.models import (
    Block,
    RequisitionHeader,
    RequisitionScope,
    RequisitionStatus,
    RequisitionType,
)


@pytest.fixture
def block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-CM',
        block_name='Commitment Block',
        created_by=user,
        updated_by=user,
    )


def _req(project, user, block, status):
    return RequisitionHeader.objects.create(
        project=project,
        block=block,
        scope=RequisitionScope.BLOCK,
        requisition_type=RequisitionType.PLANNED,
        requested_by=user,
        request_date=date.today(),
        status=status,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
def test_create_commitment_rejects_non_approved(auth_client, project, user, block):
    req = _req(project, user, block, RequisitionStatus.DRAFT)
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/requisitions/{req.id}/create-commitment/',
        {
            'commitment_number': 'CM-FROM-DRAFT',
            'amount': '1000',
            'commitment_date': '2024-06-01',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'requisition_not_approved' in str(resp.json())


@pytest.mark.django_db
def test_create_commitment_from_approved(auth_client, project, user, block):
    req = _req(project, user, block, RequisitionStatus.APPROVED)
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='C.REQ',
        cbs_name='From req',
        created_by=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/requisitions/{req.id}/create-commitment/',
        {
            'commitment_number': 'CM-FROM-REQ',
            'amount': '2500',
            'commitment_date': '2024-06-01',
            'cbs': str(node.id),
            'payment_terms': 'Per PO',
            'counterparty': 'Vendor',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body['requisition'] == str(req.id)
    assert body['payment_terms'] == 'Per PO'
    assert body['status'] == 'draft'
    approve = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/{body["id"]}/approve/'
    )
    assert approve.status_code == status.HTTP_200_OK, approve.content

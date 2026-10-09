from decimal import Decimal

import pytest

from cost_control.cbs_services import create_cbs_node
from cost_control.models import Commitment, CommitmentStatus


@pytest.mark.django_db
def test_approve_requires_wbs_or_cbs(auth_client, project):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-1',
            'amount': '1000',
            'commitment_date': '2024-06-01',
            'currency': 'IRR',
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    cid = create.json()['id']
    approve = auth_client.post(f'/api/v1/projects/{project.id}/commitments/{cid}/approve/')
    assert approve.status_code == 400
    assert 'wbs_or_cbs_required' in str(approve.json())


@pytest.mark.django_db
def test_approve_with_cbs(auth_client, project, user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='C.10',
        cbs_name='Sub',
        created_by=user,
    )
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-2',
            'amount': '500',
            'commitment_date': '2024-06-01',
            'cbs': str(node.id),
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    cid = create.json()['id']
    approve = auth_client.post(f'/api/v1/projects/{project.id}/commitments/{cid}/approve/')
    assert approve.status_code == 200, approve.content
    assert Commitment.objects.get(pk=cid).status == CommitmentStatus.APPROVED


@pytest.mark.django_db
def test_payment_cannot_exceed_commitment(auth_client, project, user, wbs):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-3',
            'amount': '100',
            'commitment_date': '2024-06-01',
            'wbs': str(wbs.id),
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    cid = create.json()['id']
    auth_client.post(f'/api/v1/projects/{project.id}/commitments/{cid}/approve/')
    pay = auth_client.post(
        f'/api/v1/projects/{project.id}/payments/',
        {'commitment': cid, 'amount': '150', 'paid_at': '2024-06-10'},
        format='json',
    )
    assert pay.status_code == 400
    assert 'payment_exceeds_commitment' in str(pay.json())


@pytest.mark.django_db
def test_payment_reduces_remaining(auth_client, project, wbs):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-4',
            'amount': '1000',
            'commitment_date': '2024-06-01',
            'wbs': str(wbs.id),
        },
        format='json',
    )
    cid = create.json()['id']
    auth_client.post(f'/api/v1/projects/{project.id}/commitments/{cid}/approve/')
    pay = auth_client.post(
        f'/api/v1/projects/{project.id}/payments/',
        {'commitment': cid, 'amount': '400', 'paid_at': '2024-06-10'},
        format='json',
    )
    assert pay.status_code == 201, pay.content
    detail = auth_client.get(f'/api/v1/projects/{project.id}/commitments/{cid}/')
    assert detail.status_code == 200
    assert Decimal(str(detail.json()['remaining'])) == Decimal('600')

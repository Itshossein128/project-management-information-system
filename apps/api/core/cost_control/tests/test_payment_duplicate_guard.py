"""US3: duplicate payment document guard + exception path."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import Commitment, CommitmentStatus


@pytest.fixture
def approved_commitment(project, wbs, user):
    return Commitment.objects.create(
        project=project,
        commitment_number='CM-PAY-1',
        amount=Decimal('1000'),
        commitment_date='2024-01-01',
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
def test_duplicate_document_blocked(auth_client, project, approved_commitment):
    base = f'/api/v1/projects/{project.id}/payments/'
    first = auth_client.post(
        base,
        {
            'commitment': str(approved_commitment.id),
            'amount': '100',
            'paid_at': '2024-06-01',
            'document_ref': 'PAY-DOC-1',
        },
        format='json',
    )
    assert first.status_code == status.HTTP_201_CREATED, first.content
    second = auth_client.post(
        base,
        {
            'commitment': str(approved_commitment.id),
            'amount': '50',
            'paid_at': '2024-06-02',
            'document_ref': 'PAY-DOC-1',
        },
        format='json',
    )
    assert second.status_code == status.HTTP_400_BAD_REQUEST
    assert 'duplicate_payment_document' in str(second.json())


@pytest.mark.django_db
def test_duplicate_with_exception_allowed(auth_client, project, approved_commitment, user):
    base = f'/api/v1/projects/{project.id}/payments/'
    auth_client.post(
        base,
        {
            'commitment': str(approved_commitment.id),
            'amount': '100',
            'paid_at': '2024-06-01',
            'document_ref': 'PAY-DOC-2',
        },
        format='json',
    )
    second = auth_client.post(
        base,
        {
            'commitment': str(approved_commitment.id),
            'amount': '50',
            'paid_at': '2024-06-02',
            'document_ref': 'PAY-DOC-2',
            'acknowledge_duplicate_exception': True,
            'exception_reason': 'Authorized split transfer',
        },
        format='json',
    )
    assert second.status_code == status.HTTP_201_CREATED, second.content
    body = second.json()
    assert body['duplicate_exception_reason'] == 'Authorized split transfer'
    assert body['duplicate_exception_by'] == str(user.id)


@pytest.mark.django_db
def test_partial_installments_distinct_refs(auth_client, project, approved_commitment):
    base = f'/api/v1/projects/{project.id}/payments/'
    for i, amt in enumerate(('300', '200'), start=1):
        resp = auth_client.post(
            base,
            {
                'commitment': str(approved_commitment.id),
                'amount': amt,
                'paid_at': f'2024-06-0{i}',
                'document_ref': f'PAY-PART-{i}',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content
    detail = auth_client.get(
        f'/api/v1/projects/{project.id}/commitments/{approved_commitment.id}/'
    )
    assert detail.status_code == status.HTTP_200_OK
    assert detail.json()['amount'] == '1000.00' or float(detail.json()['amount']) == 1000.0
    assert float(detail.json()['remaining']) == 500.0

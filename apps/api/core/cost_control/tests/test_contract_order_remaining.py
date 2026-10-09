"""US3: contract remaining via cost payments on linked commitments."""

from decimal import Decimal

import pytest
from rest_framework import status

from contracts.models import Contract, ContractType
from cost_control.models import Commitment, CommitmentStatus


@pytest.mark.django_db
def test_contract_cost_remaining(auth_client, project, wbs, user):
    contract = Contract.objects.create(
        project=project,
        contract_number='C-REM-1',
        contract_type=ContractType.MAIN,
        counterparty='Vendor',
        original_amount='5000',
        adjusted_amount='5000',
        created_by=user,
        updated_by=user,
    )
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='CM-C-1',
        amount=Decimal('5000'),
        commitment_date='2024-01-01',
        wbs=wbs,
        contract=contract,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    pay = auth_client.post(
        f'/api/v1/projects/{project.id}/payments/',
        {
            'commitment': str(commitment.id),
            'amount': '1200',
            'paid_at': '2024-06-01',
            'document_ref': 'PAY-C-1',
        },
        format='json',
    )
    assert pay.status_code == status.HTTP_201_CREATED, pay.content
    resp = auth_client.get(
        f'/api/v1/projects/{project.id}/costs/contract-remaining/',
        {'contract_id': str(contract.id)},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    data = resp.json()
    assert data['approved_amount'] == 5000.0
    assert data['paid_total'] == 1200.0
    assert data['remaining'] == 3800.0

"""US3: ledger report row types."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import (
    ActualCost,
    ActualCostStatus,
    Commitment,
    CommitmentStatus,
    CostCategory,
)


@pytest.mark.django_db
def test_ledger_report_three_row_types(auth_client, project, wbs, user):
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='CM-LR-1',
        amount=Decimal('600'),
        commitment_date='2024-01-01',
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        document_ref='PO-LR',
        created_by=user,
        updated_by=user,
    )
    ActualCost.objects.create(
        project=project,
        wbs=wbs,
        commitment=commitment,
        cost_date='2024-02-01',
        amount=Decimal('400'),
        cost_category=CostCategory.LABOR,
        status=ActualCostStatus.APPROVED,
        document_ref='INV-LR',
        created_by=user,
        updated_by=user,
    )
    pay = auth_client.post(
        f'/api/v1/projects/{project.id}/payments/',
        {
            'commitment': str(commitment.id),
            'amount': '200',
            'paid_at': '2024-03-01',
            'document_ref': 'PAY-LR',
        },
        format='json',
    )
    assert pay.status_code == status.HTTP_201_CREATED, pay.content
    report = auth_client.get(f'/api/v1/projects/{project.id}/costs/ledger-report/')
    assert report.status_code == status.HTTP_200_OK
    by_type = {r['row_type']: r for r in report.json()['rows']}
    assert by_type['commitment']['document_ref'] == 'PO-LR'
    assert by_type['actual']['document_ref'] == 'INV-LR'
    assert by_type['payment']['document_ref'] == 'PAY-LR'

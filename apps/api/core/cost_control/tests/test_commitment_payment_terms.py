"""US1: commitment payment_terms + contract FK + remaining on approve."""

from decimal import Decimal

import pytest
from rest_framework import status

from contracts.models import Contract, ContractType
from cost_control.cbs_services import create_cbs_node
from cost_control.models import (
    Budget,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
    CostCategory,
)


@pytest.mark.django_db
def test_commitment_payment_terms_round_trip(auth_client, project, user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='C.PT',
        cbs_name='Terms',
        created_by=user,
    )
    contract = Contract.objects.create(
        project=project,
        contract_number='C-PT-1',
        contract_type=ContractType.MAIN,
        counterparty='Vendor',
        original_amount='5000000',
        adjusted_amount='5000000',
        created_by=user,
        updated_by=user,
    )
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-PT-1',
            'amount': '1000',
            'commitment_date': '2024-06-01',
            'cbs': str(node.id),
            'payment_terms': 'Net 30 after invoice',
            'contract': str(contract.id),
            'counterparty': 'Vendor Co',
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    body = create.json()
    assert body['payment_terms'] == 'Net 30 after invoice'
    assert body['contract'] == str(contract.id)

    detail = auth_client.get(f'/api/v1/projects/{project.id}/commitments/{body["id"]}/')
    assert detail.status_code == status.HTTP_200_OK
    assert detail.json()['payment_terms'] == 'Net 30 after invoice'


@pytest.mark.django_db
def test_approved_commitment_reduces_remaining(auth_client, project, wbs, user):
    version = BudgetVersion.objects.create(
        project=project,
        kind=BudgetVersionKind.APPROVED,
        status=BudgetVersionStatus.APPROVED,
        version_number=1,
        currency='IRR',
        is_control=True,
        created_by=user,
        updated_by=user,
    )
    Budget.objects.create(
        project=project,
        version=version,
        level='wbs',
        wbs=wbs,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('1000'),
        created_by=user,
        updated_by=user,
    )
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/commitments/',
        {
            'commitment_number': 'CM-REM-1',
            'amount': '400',
            'commitment_date': '2024-06-01',
            'wbs': str(wbs.id),
            'payment_terms': 'Net 15',
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    cid = create.json()['id']
    approve = auth_client.post(f'/api/v1/projects/{project.id}/commitments/{cid}/approve/')
    assert approve.status_code == status.HTTP_200_OK, approve.content

    remaining = auth_client.get(f'/api/v1/projects/{project.id}/budgets/remaining/')
    assert remaining.status_code == status.HTTP_200_OK
    labor = next(h for h in remaining.json()['headings'] if h['cost_category'] == 'labor')
    assert labor['committed'] == 400.0
    assert labor['remaining'] == 600.0

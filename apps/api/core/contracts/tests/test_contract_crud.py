from decimal import Decimal

import pytest

from contracts.models import ChangeOrder, ChangeOrderStatus, ContractItem

BASE = '/api/v1/projects/{project_id}/contracts'


def test_list_contracts(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1
    assert resp.data['results'][0]['contract_number'] == 'C-001'


def test_create_contract(finance_client, project):
    url = f'{BASE.format(project_id=project.id)}/'
    resp = finance_client.post(
        url,
        {
            'contract_number': 'C-002',
            'contract_type': 'subcontract',
            'counterparty': 'Sub Co',
            'original_amount': '500000000',
            'retention_pct': '5',
        },
        format='json',
    )
    assert resp.status_code == 201
    assert resp.data['contract_number'] == 'C-002'
    assert float(resp.data['effective_amount']) == 500000000.0


def test_bulk_contract_items(finance_client, project, contract, activity):
    url = f'{BASE.format(project_id=project.id)}/{contract.id}/items/'
    resp = finance_client.post(
        url,
        [
            {
                'activity': str(activity.id),
                'boq_code': 'BOQ-2',
                'description': 'Concrete',
                'unit_price': '20000',
                'quantity': '50',
            }
        ],
        format='json',
    )
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert ContractItem.objects.filter(contract=contract, is_deleted=False).count() == 1


def test_change_order_approve_updates_adjusted_amount(finance_client, project, contract, user):
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=1,
        description='Scope increase',
        amount_change=Decimal('100000000'),
        status=ChangeOrderStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    url = (
        f'{BASE.format(project_id=project.id)}/{contract.id}/change-orders/{co.id}/approve/'
    )
    resp = finance_client.post(url)
    assert resp.status_code == 200
    contract.refresh_from_db()
    assert float(contract.adjusted_amount) == pytest.approx(1100000000.0)

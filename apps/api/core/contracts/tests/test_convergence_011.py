"""Convergence tests for 011-contracts-ipc (T024–T028, SC-001, FR-007)."""
from datetime import date
from decimal import Decimal

import pytest

from contracts.collection_service import remaining_receivable
from contracts.models import Contract, ContractType, IPC, IPCStatus
from contracts.services.ipc_service import auto_populate_ipc
from config.exceptions import CodedValidationError


BASE = '/api/v1/projects/{project_id}'


@pytest.mark.django_db
def test_populate_locked_after_submit(finance_client, project, ipc):
    ipc.gross_amount = Decimal('100000')
    ipc.save(update_fields=['gross_amount'])
    base = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}'
    assert finance_client.post(f'{base}/submit/').status_code == 200

    resp = finance_client.post(f'{base}/populate/')
    assert resp.status_code == 400
    assert 'ipc_locked_after_submit' in str(resp.json())

    with pytest.raises(CodedValidationError) as exc:
        auto_populate_ipc(ipc.id)
    assert exc.value.default_code == 'ipc_locked_after_submit'


@pytest.mark.django_db
def test_sc001_submit_approve_collect_to_zero(finance_client, project, ipc):
    ipc.gross_amount = Decimal('1000')
    ipc.save(update_fields=['gross_amount'])
    base = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}'

    submit = finance_client.post(f'{base}/submit/')
    assert submit.status_code == 200
    assert Decimal(submit.data['submitted_amount']) == Decimal('1000')

    approve = finance_client.post(
        f'{base}/approve/',
        {'approved_amount': '1000', 'planned_payment_date': '2024-06-01'},
        format='json',
    )
    assert approve.status_code == 200, approve.content
    submitted_frozen = Decimal(approve.data['submitted_amount'])

    # Net may be less than gross due to contract retention/tax — collect up to payable net
    ipc.refresh_from_db()
    payable = Decimal(str(ipc.net_amount or ipc.approved_amount or 0))
    assert payable > 0

    half = (payable / 2).quantize(Decimal('0.01'))
    rest = payable - half
    col_url = f'{base}/collections/'
    r1 = finance_client.post(
        col_url,
        {'amount': str(half), 'collected_at': '2024-06-10'},
        format='json',
    )
    assert r1.status_code == 201, r1.content
    r2 = finance_client.post(
        col_url,
        {'amount': str(rest), 'collected_at': '2024-06-20'},
        format='json',
    )
    assert r2.status_code == 201, r2.content

    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.APPROVED
    assert ipc.submitted_amount == submitted_frozen
    assert remaining_receivable(ipc) == Decimal('0')


@pytest.mark.django_db
def test_payment_terms_persist_through_change_order(finance_client, project, contract, user):
    contract.payment_terms = 'Net 30 after approval'
    contract.original_amount = Decimal('1000000')
    contract.adjusted_amount = Decimal('1000000')
    contract.save(update_fields=['payment_terms', 'original_amount', 'adjusted_amount'])

    co_url = f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/change-orders/'
    create = finance_client.post(
        co_url,
        {'description': 'Scope add', 'amount_change': '50000'},
        format='json',
    )
    assert create.status_code == 201, create.content
    co_id = create.data['id']

    approve = finance_client.post(f'{co_url}{co_id}/approve/')
    assert approve.status_code == 200, approve.content

    detail = finance_client.get(
        f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/'
    )
    assert detail.status_code == 200
    assert detail.data['payment_terms'] == 'Net 30 after approval'
    assert Decimal(str(detail.data['adjusted_amount'])) == Decimal('1050000')


@pytest.mark.django_db
def test_ipc_create_rejects_foreign_contract(finance_client, project, user, db):
    from projects.models import Project

    other = Project.objects.create(
        project_code='PRJ-FOREIGN-011',
        project_name='Other Proj',
    )
    foreign = Contract.objects.create(
        project=other,
        contract_number='FOREIGN-1',
        contract_type=ContractType.MAIN,
        counterparty='Other',
        original_amount=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/ipcs/'
    resp = finance_client.post(
        url,
        {'contract_id': str(foreign.id), 'period_start': '2024-01-01', 'period_end': '2024-01-31'},
        format='json',
    )
    assert resp.status_code == 404

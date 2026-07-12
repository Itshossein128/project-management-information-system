from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest

from contracts.models import (
    ChangeOrder,
    ChangeOrderStatus,
    Contract,
    ContractStatus,
    ContractType,
    IPC,
    IPCDeduction,
    IPCItem,
    IPCStatus,
)
from contracts.services.ipc_service import next_change_number
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole

BASE = '/api/v1/projects/{project_id}'


def test_contract_list_filters(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/contracts/?contract_type=main&counterparty=Employer'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1


def test_contract_retrieve_and_patch(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/'
    detail = finance_client.get(url)
    assert detail.status_code == 200
    assert detail.data['contract_number'] == 'C-001'

    patched = finance_client.patch(url, {'counterparty': 'New Employer'}, format='json')
    assert patched.status_code == 200
    assert patched.data['counterparty'] == 'New Employer'


def test_contract_delete_soft(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/'
    resp = finance_client.delete(url)
    assert resp.status_code == 204
    contract.refresh_from_db()
    assert contract.is_deleted is True


def test_contract_create_sets_adjusted_amount(finance_client, project):
    url = f'{BASE.format(project_id=project.id)}/contracts/'
    resp = finance_client.post(
        url,
        {'contract_number': 'C-NEW', 'original_amount': '100', 'contract_type': 'main'},
        format='json',
    )
    assert resp.status_code == 201
    assert float(resp.data['effective_amount']) == 100.0


def test_viewer_cannot_create_contract(viewer_client, project):
    url = f'{BASE.format(project_id=project.id)}/contracts/'
    resp = viewer_client.post(url, {'contract_number': 'X'}, format='json')
    assert resp.status_code == 403


def test_change_order_create_and_patch(finance_client, project, contract):
    base = f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/change-orders/'
    created = finance_client.post(base, {'description': 'CO1', 'amount_change': '5000'}, format='json')
    assert created.status_code == 201
    co_id = created.data['id']
    patched = finance_client.patch(
        f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/change-orders/{co_id}/',
        {'description': 'Updated'},
        format='json',
    )
    assert patched.status_code == 200
    assert patched.data['description'] == 'Updated'


def test_ipc_list_filters(finance_client, project, ipc_with_item, contract):
    url = (
        f'{BASE.format(project_id=project.id)}/ipcs/'
        f'?contract_id={contract.id}&status=draft'
    )
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1


def test_ipc_overdue_filter(finance_client, project, contract, user):
    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=9,
        status=IPCStatus.APPROVED,
        planned_payment_date=date.today() - timedelta(days=5),
        gross_amount=Decimal('1'),
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/ipcs/?overdue=true'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) >= 1


def test_ipc_populate_and_item_update(finance_client, project, ipc_with_item):
    item = ipc_with_item.items.first()
    populate = finance_client.post(
        f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/populate/'
    )
    assert populate.status_code == 200

    updated = finance_client.patch(
        f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/items/{item.id}/',
        {'qty_current': '12'},
        format='json',
    )
    assert updated.status_code == 200
    assert float(updated.data['gross_amount']) > 0


def test_ipc_patch_draft_only(finance_client, project, ipc_with_item):
    ipc_with_item.status = IPCStatus.SUBMITTED
    ipc_with_item.save(update_fields=['status'])
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/'
    resp = finance_client.patch(url, {'notes': 'nope'}, format='json')
    assert resp.status_code == 400


def test_submit_non_draft_rejected(finance_client, project, ipc_with_item):
    ipc_with_item.status = IPCStatus.SUBMITTED
    ipc_with_item.save(update_fields=['status'])
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/submit/'
    resp = finance_client.post(url)
    assert resp.status_code == 400


def test_deduction_validation_and_crud(finance_client, project, ipc_with_item):
    base = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/deductions/'

    bad_type = finance_client.post(
        base, {'deduction_type': 'retention', 'amount': '1'}, format='json'
    )
    assert bad_type.status_code == 400

    missing_amount = finance_client.post(
        base, {'deduction_type': 'other'}, format='json'
    )
    assert missing_amount.status_code == 400

    created = finance_client.post(
        base,
        {'deduction_type': 'material_price_diff', 'amount': '1000', 'description': 'x'},
        format='json',
    )
    assert created.status_code == 201
    ded = next(d for d in created.data['deductions'] if d['deduction_type'] == 'material_price_diff')

    patched = finance_client.patch(
        f'{base}{ded["id"]}/',
        {'amount': '2000'},
        format='json',
    )
    assert patched.status_code == 200

    deleted = finance_client.delete(f'{base}{ded["id"]}/')
    assert deleted.status_code == 200


def test_deduction_blocked_when_not_draft(finance_client, project, ipc_with_item):
    ipc_with_item.status = IPCStatus.SUBMITTED
    ipc_with_item.save(update_fields=['status'])
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/deductions/'
    resp = finance_client.post(
        url, {'deduction_type': 'other', 'amount': '1'}, format='json'
    )
    assert resp.status_code == 400


def test_subcontract_ipc_pay_creates_outflow(finance_client, project, user, activity):
    sub = Contract.objects.create(
        project=project,
        contract_number='SUB-1',
        contract_type=ContractType.SUBCONTRACT,
        counterparty='Sub',
        original_amount=Decimal('100'),
        adjusted_amount=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    ipc = IPC.objects.create(
        project=project,
        contract=sub,
        ipc_number=1,
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('50000'),
        net_amount=Decimal('45000'),
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/pay/'
    resp = finance_client.post(url, {'actual_payment_date': '1403/01/15'}, format='json')
    assert resp.status_code == 200
    from cash_flow.models import CashTransaction, CashTransactionType

    tx = CashTransaction.objects.get(ipc=ipc, is_deleted=False)
    assert tx.tx_type == CashTransactionType.OUT


def test_ipc_pdf_export(finance_client, project, ipc_with_item):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/pdf/'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'application/pdf'
    assert resp.content[:4] == b'%PDF'


def test_pay_idempotent_cash_transaction(finance_client, project, ipc_with_item):
    ipc_with_item.status = IPCStatus.APPROVED
    ipc_with_item.net_amount = Decimal('90000')
    ipc_with_item.save()
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/pay/'
    finance_client.post(url)
    finance_client.post(url)
    from cash_flow.models import CashTransaction

    assert CashTransaction.objects.filter(ipc=ipc_with_item, is_deleted=False).count() == 1


def test_next_change_number(db, contract, user):
    ChangeOrder.objects.create(
        contract=contract,
        change_number=2,
        description='x',
        created_by=user,
        updated_by=user,
    )
    assert next_change_number(contract.id) == 3


def test_contract_model_properties(contract):
    assert contract.effective_amount == contract.adjusted_amount
    assert contract.advance_amount > 0


def test_publish_ipc_submitted_handles_broker_failure(finance_client, project, ipc_with_item):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/submit/'
    with patch('events.publisher.EventPublisher') as mock_cls:
        mock_cls.return_value.publish.side_effect = RuntimeError('down')
        resp = finance_client.post(url)
    assert resp.status_code == 200


def test_guarantee_expiry_alert_on_list(finance_client, project, contract):
    contract.performance_guarantee_expiry = date.today() + timedelta(days=10)
    contract.save(update_fields=['performance_guarantee_expiry'])
    url = f'{BASE.format(project_id=project.id)}/contracts/'
    resp = finance_client.get(url)
    assert resp.data['results'][0]['guarantee_expiry_alert'] is True

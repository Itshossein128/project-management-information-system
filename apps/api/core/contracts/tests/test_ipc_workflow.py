from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from cash_flow.models import CashTransaction
from contracts.models import IPC, IPCStatus

BASE = '/api/v1/projects/{project_id}'


def test_create_ipc(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/ipcs/'
    with patch('contracts.tasks.populate_ipc_async.delay', side_effect=RuntimeError('no broker')):
        resp = finance_client.post(
            url,
            {'contract_id': str(contract.id), 'period_start': '2024-04-01', 'period_end': '2024-04-30'},
            format='json',
        )
    assert resp.status_code == 201
    assert resp.data['ipc_number'] == 1


def test_ipc_workflow_creates_cash_transaction(finance_client, project, ipc, user):
    ipc.gross_amount = Decimal('1000000')
    ipc.net_amount = Decimal('800000')
    ipc.save(update_fields=['gross_amount', 'net_amount'])
    base = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}'

    submit = finance_client.post(f'{base}/submit/')
    assert submit.status_code == 200
    assert submit.data['status'] == 'submitted'

    approve = finance_client.post(f'{base}/approve/')
    assert approve.status_code == 200
    assert approve.data['status'] == 'approved'

    pay = finance_client.post(f'{base}/pay/', {'actual_payment_date': '2024-05-15'}, format='json')
    assert pay.status_code == 200
    assert pay.data['status'] == 'paid'

    assert CashTransaction.objects.filter(ipc=ipc, is_deleted=False).count() == 1


def test_reject_returns_to_draft(finance_client, project, ipc):
    ipc.status = IPCStatus.SUBMITTED
    ipc.save(update_fields=['status'])
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/reject/'
    resp = finance_client.post(url, {'reason': 'Incomplete docs'}, format='json')
    assert resp.status_code == 200
    assert resp.data['status'] == 'draft'
    assert resp.data['rejection_reason'] == 'Incomplete docs'


def test_manual_deduction_api(finance_client, project, ipc):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/deductions/'
    resp = finance_client.post(
        url,
        {'deduction_type': 'other', 'amount': '50000', 'description': 'Penalty'},
        format='json',
    )
    assert resp.status_code == 201
    types = [d['deduction_type'] for d in resp.data['deductions']]
    assert 'other' in types


def test_submit_publishes_event(finance_client, project, ipc):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/submit/'
    with patch('contracts.views._publish_ipc_submitted') as mock_publish:
        resp = finance_client.post(url)
    assert resp.status_code == 200
    mock_publish.assert_called_once()

from decimal import Decimal

import pytest

from contracts.models import IPCStatus


BASE = '/api/v1/projects/{project_id}/ipcs'


@pytest.mark.django_db
def test_submit_freezes_submitted_amount(finance_client, project, ipc):
    ipc.gross_amount = Decimal('1000000')
    ipc.save(update_fields=['gross_amount'])
    resp = finance_client.post(f'{BASE.format(project_id=project.id)}/{ipc.id}/submit/')
    assert resp.status_code == 200
    assert resp.data['status'] == 'submitted'
    assert Decimal(resp.data['submitted_amount']) == Decimal('1000000')
    assert resp.data['approved_amount'] is None


@pytest.mark.django_db
def test_approve_sets_approved_amount_default(finance_client, project, ipc):
    ipc.gross_amount = Decimal('500000')
    ipc.save(update_fields=['gross_amount'])
    base = f'{BASE.format(project_id=project.id)}/{ipc.id}'
    assert finance_client.post(f'{base}/submit/').status_code == 200
    approve = finance_client.post(f'{base}/approve/', {}, format='json')
    assert approve.status_code == 200
    assert approve.data['status'] == 'approved'
    assert Decimal(approve.data['submitted_amount']) == Decimal('500000')
    assert Decimal(approve.data['approved_amount']) == Decimal('500000')


@pytest.mark.django_db
def test_approve_reduced_requires_variance_note(finance_client, project, ipc):
    ipc.gross_amount = Decimal('1000000')
    ipc.save(update_fields=['gross_amount'])
    base = f'{BASE.format(project_id=project.id)}/{ipc.id}'
    assert finance_client.post(f'{base}/submit/').status_code == 200

    missing = finance_client.post(
        f'{base}/approve/',
        {'approved_amount': '900000'},
        format='json',
    )
    assert missing.status_code == 400
    assert 'approval_variance_note_required' in str(missing.json())

    ok = finance_client.post(
        f'{base}/approve/',
        {
            'approved_amount': '900000',
            'approval_variance_note': 'BOQ variance on item 3',
            'planned_payment_date': '2024-06-01',
        },
        format='json',
    )
    assert ok.status_code == 200, ok.content
    assert Decimal(ok.data['approved_amount']) == Decimal('900000')
    assert ok.data['approval_variance_note'] == 'BOQ variance on item 3'
    assert Decimal(ok.data['submitted_amount']) == Decimal('1000000')


@pytest.mark.django_db
def test_approve_cannot_exceed_submitted(finance_client, project, ipc):
    ipc.gross_amount = Decimal('100')
    ipc.save(update_fields=['gross_amount'])
    base = f'{BASE.format(project_id=project.id)}/{ipc.id}'
    assert finance_client.post(f'{base}/submit/').status_code == 200
    resp = finance_client.post(
        f'{base}/approve/',
        {'approved_amount': '150', 'approval_variance_note': 'x'},
        format='json',
    )
    assert resp.status_code == 400
    assert 'approved_exceeds_submitted' in str(resp.json())


@pytest.mark.django_db
def test_submit_requires_positive_gross(finance_client, project, ipc):
    resp = finance_client.post(f'{BASE.format(project_id=project.id)}/{ipc.id}/submit/')
    assert resp.status_code == 400
    assert 'ipc_gross_required' in str(resp.json())

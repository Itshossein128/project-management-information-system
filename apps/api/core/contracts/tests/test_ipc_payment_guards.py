"""Payment must consume an approved IPC, including when callers hold stale objects."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from cash_flow.models import CashTransaction
from config.exceptions import CodedValidationError
from contracts.models import IPC, IPCStatus
from contracts.services.ipc_service import pay_ipc


@pytest.mark.django_db
@pytest.mark.parametrize('status', [IPCStatus.DRAFT, IPCStatus.SUBMITTED, IPCStatus.UNDER_REVIEW])
def test_payment_rejects_unapproved_ipc(finance_client, ipc, status):
    ipc.status = status
    ipc.gross_amount = Decimal('100')
    ipc.net_amount = Decimal('80')
    ipc.save()

    response = finance_client.post(
        f'/api/v1/projects/{ipc.project_id}/ipcs/{ipc.id}/pay/',
        {'actual_payment_date': '2024-05-15'},
        format='json',
    )

    assert response.status_code == 400
    assert response.data['error']['code'] == 'ipc_not_payable'
    ipc.refresh_from_db()
    assert ipc.status == status
    assert ipc.actual_payment_date is None
    assert not CashTransaction.objects.filter(ipc=ipc).exists()


@pytest.mark.django_db
def test_payment_rechecks_persisted_approval(ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.save(update_fields=['status'])
    stale = IPC.objects.get(pk=ipc.pk)
    IPC.objects.filter(pk=ipc.pk).update(status=IPCStatus.DRAFT)

    with pytest.raises(CodedValidationError) as error:
        pay_ipc(stale, user, date(2024, 5, 15))

    assert error.value.default_code == 'ipc_not_payable'
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.DRAFT
    assert ipc.actual_payment_date is None
    assert not CashTransaction.objects.filter(ipc=ipc).exists()


@pytest.mark.django_db
def test_payment_uses_current_approved_state(ipc, user):
    # The passed instance is still draft; payment must reload the approved row.
    IPC.objects.filter(pk=ipc.pk).update(
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('100'),
        net_amount=Decimal('80'),
    )

    paid = pay_ipc(ipc, user, date(2024, 5, 15))

    assert paid.status == IPCStatus.PAID
    ipc.refresh_from_db()
    assert ipc.actual_payment_date == date(2024, 5, 15)
    assert CashTransaction.objects.get(ipc=ipc).amount == Decimal('80')


@pytest.mark.django_db
def test_cash_transaction_failure_rolls_back_payment(ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.save(update_fields=['status'])

    with patch(
        'contracts.services.ipc_service._upsert_ipc_cash_transaction',
        side_effect=RuntimeError('ledger unavailable'),
    ):
        with pytest.raises(RuntimeError, match='ledger unavailable'):
            pay_ipc(ipc, user, date(2024, 5, 15))

    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.APPROVED
    assert ipc.actual_payment_date is None
    assert not CashTransaction.objects.filter(ipc=ipc).exists()

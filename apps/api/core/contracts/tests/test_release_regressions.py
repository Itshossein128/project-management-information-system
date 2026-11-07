"""Financial integrity and recovery cases required by the release coverage gate."""
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

import pytest
from django.db.models.signals import post_save
from rest_framework.exceptions import NotFound, ValidationError

from config.exceptions import CodedValidationError
from contracts.collection_service import add_collection
from contracts.models import ChangeOrder, ChangeOrderStatus, IPC, IPCCollection, IPCStatus
from contracts.services.contract_service import (
    approve_change_order, bulk_upsert_contract_items, reject_change_order,
)
from contracts.services.ipc_service import approve_ipc, auto_populate_ipc, update_ipc_item
from master_data.models import RoleAccessChange


def test_missing_contract_line_update_does_not_create_a_line(contract, user):
    with pytest.raises(NotFound):
        bulk_upsert_contract_items(contract, [{'id': str(uuid4()), 'quantity': '10'}], user)
    assert not contract.items.exists()


def test_collection_uses_approved_amount_when_net_is_unset(ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.gross_amount = Decimal('200')
    ipc.approved_amount = Decimal('100')
    ipc.net_amount = None
    ipc.save()
    with pytest.raises(ValidationError, match='collection_exceeds_payable'):
        add_collection(ipc=ipc, amount='101', collected_at=date.today(), user=user)
    assert not IPCCollection.objects.filter(ipc=ipc).exists()


@pytest.mark.parametrize('amount', ['0', '-1'])
def test_nonpositive_collection_is_rejected(ipc, user, amount):
    ipc.status = IPCStatus.APPROVED
    ipc.net_amount = Decimal('100')
    ipc.save()
    with pytest.raises(ValidationError, match='greater than zero'):
        add_collection(ipc=ipc, amount=amount, collected_at=date.today(), user=user)
    assert not IPCCollection.objects.filter(ipc=ipc).exists()


def test_collection_rolls_back_if_a_save_hook_changes_parent_amounts(ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.gross_amount = ipc.net_amount = Decimal('100')
    ipc.save()

    def mutate_parent(sender, instance, **kwargs):
        IPC.objects.filter(pk=instance.ipc_id).update(gross_amount=Decimal('999'))

    post_save.connect(mutate_parent, sender=IPCCollection, weak=False)
    try:
        with pytest.raises(CodedValidationError) as error:
            add_collection(ipc=ipc, amount='10', collected_at=date.today(), user=user)
        assert error.value.default_code == 'collection_mutated_ipc'
    finally:
        post_save.disconnect(mutate_parent, sender=IPCCollection)
    ipc.refresh_from_db()
    assert ipc.gross_amount == Decimal('100')
    assert not IPCCollection.objects.filter(ipc=ipc).exists()


def test_emergency_change_order_approval_is_audited_and_idempotent(contract, user):
    user.is_superuser = True
    user.save(update_fields=['is_superuser'])
    contract.refresh_from_db()
    before = contract.adjusted_amount
    change = ChangeOrder.objects.create(
        contract=contract, change_number=1, amount_change=Decimal('100'),
        status=ChangeOrderStatus.SUBMITTED, created_by=user, updated_by=user,
    )
    approve_change_order(change, user, break_glass_reason='Emergency review documented')
    approve_change_order(change, user)
    contract.refresh_from_db()
    assert contract.adjusted_amount == before + Decimal('100')
    history = RoleAccessChange.objects.get(action='sod_break_glass', project=contract.project)
    assert history.after['reason'] == 'Emergency review documented'
    assert history.after['record_id'] == str(change.id)


def test_change_order_reversal_keeps_adjusted_amount_nonnegative(contract, user):
    contract.adjusted_amount = Decimal('10')
    contract.save(update_fields=['adjusted_amount'])
    change = ChangeOrder.objects.create(
        contract=contract, change_number=1, amount_change=Decimal('100'),
        status=ChangeOrderStatus.APPROVED, created_by=user, updated_by=user,
    )
    reject_change_order(change, user)
    contract.refresh_from_db()
    assert contract.adjusted_amount == 0
    assert change.status == ChangeOrderStatus.REJECTED


def test_populating_next_ipc_preserves_previously_billed_quantity(ipc_with_item, user):
    ipc_with_item.status = IPCStatus.APPROVED
    ipc_with_item.save(update_fields=['status'])
    next_ipc = IPC.objects.create(
        project=ipc_with_item.project, contract=ipc_with_item.contract,
        ipc_number=2, period_start=date(2024, 4, 1), period_end=date(2024, 4, 30),
        created_by=user, updated_by=user,
    )
    auto_populate_ipc(next_ipc.id)
    line = next_ipc.items.get()
    assert line.qty_previous == Decimal('10')
    assert line.qty_current == 0
    assert line.qty_cumulative == Decimal('10')


@pytest.mark.parametrize('status,amount,code', [
    (IPCStatus.DRAFT, '10', 'ipc_not_approvable'),
    (IPCStatus.SUBMITTED, '-1', 'approved_amount_invalid'),
])
def test_invalid_approval_preserves_ipc(ipc, other_user, status, amount, code):
    ipc.status = status
    ipc.submitted_amount = Decimal('100')
    ipc.save()
    with pytest.raises(CodedValidationError) as error:
        approve_ipc(ipc, other_user, approved_amount=amount)
    assert error.value.default_code == code
    ipc.refresh_from_db()
    assert ipc.status == status
    assert ipc.approved_amount is None


def test_submitted_ipc_line_cannot_be_edited(ipc_with_item, user):
    ipc_with_item.status = IPCStatus.SUBMITTED
    ipc_with_item.save(update_fields=['status'])
    line = ipc_with_item.items.get()
    with pytest.raises(CodedValidationError) as error:
        update_ipc_item(ipc_with_item, line, '999', user)
    assert error.value.default_code == 'ipc_locked_after_submit'
    line.refresh_from_db()
    assert line.qty_current == Decimal('10')


def test_submit_validation_error_is_reported_without_mutating_ipc(finance_client, ipc):
    with patch('contracts.views.submit_ipc', side_effect=ValueError('Submission rejected')):
        response = finance_client.post(f'/api/v1/projects/{ipc.project_id}/ipcs/{ipc.id}/submit/')
    assert response.status_code == 400
    assert response.data['detail'] == 'Submission rejected'
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.DRAFT


@pytest.mark.parametrize('window', ['invalid', '-1'])
def test_receivables_report_handles_invalid_window_and_filters_contract(finance_client, ipc, window):
    ipc.status = IPCStatus.APPROVED
    ipc.net_amount = Decimal('100')
    ipc.planned_payment_date = date.today() - timedelta(days=1)
    ipc.save()
    response = finance_client.get(
        f'/api/v1/projects/{ipc.project_id}/ipcs/receivables-report/',
        {'near_due_days': window, 'contract_id': str(ipc.contract_id)},
    )
    assert response.status_code == 200
    assert [item['ipc_id'] for item in response.data['items']] == [str(ipc.id)]

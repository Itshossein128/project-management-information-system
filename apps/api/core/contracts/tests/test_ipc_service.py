from datetime import date
from decimal import Decimal

import pytest

from contracts.models import ContractType, IPC, IPCDeduction, IPCStatus
from contracts.services.ipc_service import apply_deductions, auto_populate_ipc, next_ipc_number
from schedule.models import ActivityProgress


def test_next_ipc_number_starts_at_one(db, contract):
    assert next_ipc_number(contract.id) == 1


def test_next_ipc_number_increments(db, contract, project, user):
    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=3,
        created_by=user,
        updated_by=user,
    )
    assert next_ipc_number(contract.id) == 4


def test_auto_populate_from_activity_progress(db, ipc, contract_item, activity):
    ActivityProgress.objects.create(
        activity=activity,
        report_date=date(2024, 2, 28),
        actual_progress=0.1,
    )
    ActivityProgress.objects.create(
        activity=activity,
        report_date=date(2024, 3, 15),
        actual_progress=0.25,
    )

    auto_populate_ipc(ipc.id)
    ipc.refresh_from_db()

    item = ipc.items.get()
    assert float(item.qty_current) == pytest.approx(15.0, rel=1e-3)
    assert float(ipc.gross_amount) == pytest.approx(150000.0, rel=1e-3)


def test_apply_deductions_retention_and_tax(db, ipc, contract):
    contract.advance_payment_pct = Decimal('0')
    contract.save(update_fields=['advance_payment_pct'])
    ipc.gross_amount = Decimal('1000000')
    ipc.save(update_fields=['gross_amount'])

    apply_deductions(ipc.id)
    ipc.refresh_from_db()

    deductions = {d.deduction_type: float(d.amount) for d in ipc.deductions.filter(is_deleted=False)}
    assert deductions['retention'] == pytest.approx(100000.0)
    assert deductions['tax'] == pytest.approx(90000.0)
    assert deductions['insurance'] == pytest.approx(10000.0)
    assert float(ipc.net_amount) == pytest.approx(800000.0, rel=1e-3)


def test_apply_deductions_preserves_manual(db, ipc, user):
    ipc.gross_amount = Decimal('500000')
    ipc.save(update_fields=['gross_amount'])
    IPCDeduction.objects.create(
        ipc=ipc,
        deduction_type='material_price_diff',
        amount=Decimal('25000'),
        description='Steel price diff',
        created_by=user,
        updated_by=user,
    )

    apply_deductions(ipc.id)
    ipc.refresh_from_db()

    manual = ipc.deductions.filter(deduction_type='material_price_diff', is_deleted=False).get()
    assert float(manual.amount) == 25000.0


def test_advance_recovery_capped(db, project, user, contract_item):
    contract = contract_item.contract
    contract.contract_type = ContractType.SUBCONTRACT
    contract.advance_payment_pct = Decimal('20')
    contract.original_amount = Decimal('1000000')
    contract.adjusted_amount = Decimal('1000000')
    contract.save()

    paid_ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.PAID,
        gross_amount=Decimal('500000'),
        created_by=user,
        updated_by=user,
    )
    IPCDeduction.objects.create(
        ipc=paid_ipc,
        deduction_type='advance_recovery',
        amount=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )

    ipc2 = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=2,
        status=IPCStatus.DRAFT,
        gross_amount=Decimal('500000'),
        created_by=user,
        updated_by=user,
    )
    apply_deductions(ipc2.id)
    recovery = ipc2.deductions.filter(deduction_type='advance_recovery', is_deleted=False).first()
    assert recovery is not None
    assert float(recovery.amount) == pytest.approx(100000.0)

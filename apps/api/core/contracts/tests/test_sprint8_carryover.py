"""Sprint 8 carry-over: change orders, IPC cash tx, monitoring tasks."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from cash_flow.models import CashTransaction, CashTransactionType, InflowCategory, OutflowCategory
from contracts.models import ChangeOrder, ChangeOrderStatus, Contract, ContractStatus, ContractType, IPC, IPCStatus
from alerts.models import AlertLog
from contracts.tasks import monitor_guarantee_expiry, monitor_ipc_payment_delays
from master_data.models import ProjectMember, ProjectMemberRole
from notifications.models import Notification

BASE = '/api/v1/projects/{project_id}/contracts'


def test_change_order_approve_increases_adjusted_amount(finance_client, project, contract, user):
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=1,
        description='Scope increase',
        amount_change=Decimal('100000000'),
        status=ChangeOrderStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{contract.id}/change-orders/{co.id}/approve/'
    resp = finance_client.post(url)
    assert resp.status_code == 200
    contract.refresh_from_db()
    assert float(contract.adjusted_amount) == pytest.approx(1100000000.0)


def test_change_order_approve_negative_delta_reduces_adjusted_amount(finance_client, project, user):
    contract = Contract.objects.create(
        project=project,
        contract_number='C-NEG',
        contract_type=ContractType.MAIN,
        counterparty='Employer',
        original_amount=Decimal('1000000'),
        adjusted_amount=Decimal('1000000'),
        created_by=user,
        updated_by=user,
    )
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=1,
        description='Scope reduction',
        amount_change=Decimal('-200000'),
        status=ChangeOrderStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{contract.id}/change-orders/{co.id}/approve/'
    resp = finance_client.post(url)
    assert resp.status_code == 200
    contract.refresh_from_db()
    assert float(contract.adjusted_amount) == pytest.approx(800000.0)


def test_change_order_approve_negative_adjusted_amount_returns_400(finance_client, project, user):
    contract = Contract.objects.create(
        project=project,
        contract_number='C-ZERO',
        contract_type=ContractType.MAIN,
        counterparty='Employer',
        original_amount=Decimal('100000'),
        adjusted_amount=Decimal('50000'),
        created_by=user,
        updated_by=user,
    )
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=1,
        description='Too large reduction',
        amount_change=Decimal('-60000'),
        status=ChangeOrderStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{contract.id}/change-orders/{co.id}/approve/'
    resp = finance_client.post(url)
    assert resp.status_code == 400
    assert resp.data['detail'] == 'Failed to reject change order.'
    contract.refresh_from_db()
    assert float(contract.adjusted_amount) == pytest.approx(50000.0)


def test_change_order_reject_reverses_approved_adjustment(finance_client, project, contract, user):
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=1,
        description='Temporary scope',
        amount_change=Decimal('50000000'),
        status=ChangeOrderStatus.APPROVED,
        approved_date=date.today(),
        created_by=user,
        updated_by=user,
    )
    contract.adjusted_amount = Decimal('1050000000')
    contract.save(update_fields=['adjusted_amount'])
    url = f'{BASE.format(project_id=project.id)}/{contract.id}/change-orders/{co.id}/reject/'
    resp = finance_client.post(url)
    assert resp.status_code == 200
    contract.refresh_from_db()
    assert float(contract.adjusted_amount) == pytest.approx(1000000000.0)


def test_main_contract_ipc_pay_creates_inflow(finance_client, project, contract, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=2,
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('1000000'),
        net_amount=Decimal('900000'),
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/pay/'
    resp = finance_client.post(url, {'actual_payment_date': '2024-05-15'}, format='json')
    assert resp.status_code == 200
    tx = CashTransaction.objects.get(ipc=ipc, is_deleted=False)
    assert tx.tx_type == CashTransactionType.IN
    assert tx.category == InflowCategory.IPC_RECEIPT


def test_subcontract_ipc_pay_creates_outflow(finance_client, project, user):
    sub = Contract.objects.create(
        project=project,
        contract_number='SUB-2',
        contract_type=ContractType.SUBCONTRACT,
        counterparty='Sub Co',
        original_amount=Decimal('100000'),
        created_by=user,
        updated_by=user,
    )
    ipc = IPC.objects.create(
        project=project,
        contract=sub,
        ipc_number=1,
        status=IPCStatus.APPROVED,
        net_amount=Decimal('45000'),
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/pay/'
    resp = finance_client.post(url, format='json')
    assert resp.status_code == 200
    tx = CashTransaction.objects.get(ipc=ipc, is_deleted=False)
    assert tx.tx_type == CashTransactionType.OUT
    assert tx.category == OutflowCategory.SUBCONTRACTOR_PAYMENT


def test_ipc_pay_twice_updates_existing_transaction(finance_client, project, ipc_with_item):
    ipc_with_item.status = IPCStatus.APPROVED
    ipc_with_item.net_amount = Decimal('90000')
    ipc_with_item.save()
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc_with_item.id}/pay/'
    finance_client.post(url, {'actual_payment_date': '2024-05-01'}, format='json')
    first_tx = CashTransaction.objects.get(ipc=ipc_with_item, is_deleted=False)
    first_id = first_tx.id
    first_tx.amount = Decimal('1')
    first_tx.save(update_fields=['amount'])

    finance_client.post(url, {'actual_payment_date': '2024-06-01'}, format='json')
    assert CashTransaction.objects.filter(ipc=ipc_with_item, is_deleted=False).count() == 1
    first_tx.refresh_from_db()
    assert first_tx.id == first_id
    assert float(first_tx.amount) == pytest.approx(90000.0)
    assert first_tx.actual_date == date(2024, 6, 1)


def test_monitor_ipc_payment_delays_notifies_finance_and_pm(
    db, project, contract, user, other_user, finance_manager_role, project_manager_role
):
    finance_member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=finance_member, role=finance_manager_role)
    pm_member = ProjectMember.objects.create(
        project=project,
        user=other_user,
        status='active',
    )
    ProjectMemberRole.objects.create(member=pm_member, role=project_manager_role)

    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=9,
        status=IPCStatus.APPROVED,
        planned_payment_date=date.today() - timedelta(days=5),
        created_by=user,
        updated_by=user,
    )
    monitor_ipc_payment_delays()
    assert AlertLog.objects.filter(project=project).count() >= 1
    assert Notification.objects.filter(project=project).count() == 2


def test_monitor_ipc_payment_delays_skips_paid_ipc(db, project, contract, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=10,
        status=IPCStatus.PAID,
        planned_payment_date=date.today() - timedelta(days=5),
        actual_payment_date=date.today() - timedelta(days=1),
        created_by=user,
        updated_by=user,
    )
    monitor_ipc_payment_delays()
    assert Notification.objects.filter(project=project).count() == 0


def test_monitor_guarantee_expiry_within_threshold(db, project, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    Contract.objects.create(
        project=project,
        contract_number='G-15',
        status=ContractStatus.ACTIVE,
        performance_guarantee_expiry=date.today() + timedelta(days=15),
        created_by=user,
        updated_by=user,
    )
    monitor_guarantee_expiry()
    assert AlertLog.objects.filter(project=project, message__contains='حسن انجام کار').exists()
    assert Notification.objects.filter(project=project, message__contains='حسن انجام کار').exists()


def test_monitor_guarantee_expiry_outside_threshold(db, project, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    Contract.objects.create(
        project=project,
        contract_number='G-45',
        status=ContractStatus.ACTIVE,
        performance_guarantee_expiry=date.today() + timedelta(days=45),
        created_by=user,
        updated_by=user,
    )
    monitor_guarantee_expiry()
    assert Notification.objects.filter(project=project).count() == 0

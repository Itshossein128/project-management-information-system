"""Unit tests for Sprint 13 alert checkers."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from alerts.models import AlertLog, AlertRule
from alerts.services.alert_engine import check_and_fire_for_project
from contracts.models import Contract, ContractStatus, IPC, IPCStatus
from resources.models import (
    Material,
    MaterialRequest,
    MaterialRequestStatus,
    PurchaseOrder,
    Supplier,
)
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule


@pytest.mark.django_db
def test_critical_path_delay_fires(project, activity, user):
    AlertRule.objects.create(
        project=None,
        alert_type='critical_path_delay',
        name='CP',
        threshold=Decimal('5'),
        notify_roles='project_manager',
        is_active=True,
    )
    baseline = BaselineSchedule.objects.create(
        project=project,
        version_name='B1',
        is_current=True,
    )
    BaselineActivity.objects.create(
        baseline=baseline,
        activity=activity,
        is_critical=True,
    )
    ActivityProgress.objects.create(
        activity=activity,
        report_date=date.today(),
        planned_progress=Decimal('0.50'),
        actual_progress=Decimal('0.30'),
        updated_by=user,
    )
    check_and_fire_for_project(project.id)
    assert AlertLog.objects.filter(
        project=project,
        trigger_reference=f'critical_path:{activity.id}',
    ).exists()


@pytest.mark.django_db
def test_ipc_approval_delayed_fires(project, user):
    AlertRule.objects.create(
        project=None,
        alert_type='ipc_approval_delayed',
        name='IPC approve',
        threshold=Decimal('7'),
        notify_roles='project_manager',
        is_active=True,
    )
    contract = Contract.objects.create(
        project=project,
        contract_number='C-1',
        counterparty='Sub',
        contract_type='main',
        status=ContractStatus.ACTIVE,
        start_date=date(2024, 1, 1),
        created_by=user,
        updated_by=user,
    )
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.SUBMITTED,
        submitted_date=date.today() - timedelta(days=10),
        created_by=user,
        updated_by=user,
    )
    check_and_fire_for_project(project.id)
    assert AlertLog.objects.filter(
        project=project,
        trigger_reference=f'ipc_approval:{ipc.id}',
    ).exists()


@pytest.mark.django_db
def test_procurement_overdue_fires(project, user):
    AlertRule.objects.create(
        project=None,
        alert_type='procurement_overdue',
        name='Proc',
        threshold=Decimal('0'),
        notify_roles='project_manager',
        is_active=True,
    )
    material = Material.objects.create(
        project=project,
        material_code='M1',
        material_name='Cement',
    )
    supplier = Supplier.objects.create(
        project=project,
        supplier_name='Supplier',
        created_by=user,
        updated_by=user,
    )
    mr = MaterialRequest.objects.create(
        project=project,
        material=material,
        request_number=1,
        requested_qty=Decimal('10'),
        unit='ton',
        status=MaterialRequestStatus.ORDERED,
        created_by=user,
        updated_by=user,
    )
    po = PurchaseOrder.objects.create(
        project=project,
        material_request=mr,
        supplier=supplier,
        po_number=1,
        order_date=date.today() - timedelta(days=20),
        expected_delivery_date=date.today() - timedelta(days=2),
        ordered_qty=Decimal('10'),
        created_by=user,
        updated_by=user,
    )
    check_and_fire_for_project(project.id)
    assert AlertLog.objects.filter(
        project=project,
        trigger_reference=f'po_overdue:{po.id}',
    ).exists()

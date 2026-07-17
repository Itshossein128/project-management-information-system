from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

from contracts.models import Contract, ContractStatus, IPC, IPCStatus
from contracts.tasks import (
    monitor_guarantee_expiry,
    monitor_ipc_payment_delays,
    populate_ipc_async,
    send_ipc_delay_notification,
)
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from alerts.models import AlertLog
from notifications.models import Notification


def test_populate_ipc_async(db, ipc, contract_item, user, activity):
    from schedule.models import ActivityProgress

    ActivityProgress.objects.create(
        activity=activity,
        report_date=date(2024, 3, 15),
        actual_progress=Decimal('0.2'),
    )
    populate_ipc_async(str(ipc.id))
    ipc.refresh_from_db()
    assert ipc.items.filter(is_deleted=False).exists()


def test_send_ipc_delay_notification(db, project, contract, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    send_ipc_delay_notification(str(ipc.id), 7)
    assert Notification.objects.filter(project=project).exists()


def test_monitor_ipc_payment_delays(db, project, contract, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.APPROVED,
        planned_payment_date=date.today() - timedelta(days=3),
        created_by=user,
        updated_by=user,
    )
    monitor_ipc_payment_delays()
    assert AlertLog.objects.filter(project=project).exists()
    assert Notification.objects.filter(project=project).exists()


def test_monitor_guarantee_expiry(db, project, user, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    Contract.objects.create(
        project=project,
        contract_number='G-1',
        status=ContractStatus.ACTIVE,
        performance_guarantee_expiry=date.today() + timedelta(days=7),
        created_by=user,
        updated_by=user,
    )
    monitor_guarantee_expiry()
    assert AlertLog.objects.filter(project=project, message__contains='حسن انجام کار').exists()
    assert Notification.objects.filter(project=project).exists()

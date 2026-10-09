from datetime import date, timedelta
from decimal import Decimal

import pytest

from contracts.models import IPC, IPCCollection, IPCStatus


@pytest.mark.django_db
def test_receivables_report_overdue_and_near_due(finance_client, project, contract, user):
    today = date.today()
    overdue = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=301,
        gross_amount=Decimal('1000'),
        submitted_amount=Decimal('1000'),
        approved_amount=Decimal('1000'),
        net_amount=Decimal('1000'),
        status=IPCStatus.APPROVED,
        planned_payment_date=today - timedelta(days=10),
        created_by=user,
        updated_by=user,
    )
    near = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=302,
        gross_amount=Decimal('400'),
        submitted_amount=Decimal('400'),
        approved_amount=Decimal('400'),
        net_amount=Decimal('400'),
        status=IPCStatus.APPROVED,
        planned_payment_date=today + timedelta(days=3),
        created_by=user,
        updated_by=user,
    )
    future = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=303,
        gross_amount=Decimal('200'),
        submitted_amount=Decimal('200'),
        approved_amount=Decimal('200'),
        net_amount=Decimal('200'),
        status=IPCStatus.APPROVED,
        planned_payment_date=today + timedelta(days=30),
        created_by=user,
        updated_by=user,
    )
    collected = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=304,
        gross_amount=Decimal('500'),
        submitted_amount=Decimal('500'),
        approved_amount=Decimal('500'),
        net_amount=Decimal('500'),
        status=IPCStatus.APPROVED,
        planned_payment_date=today - timedelta(days=5),
        created_by=user,
        updated_by=user,
    )
    IPCCollection.objects.create(
        ipc=collected,
        amount=Decimal('500'),
        collected_at=today,
        created_by=user,
        updated_by=user,
    )

    url = f'/api/v1/projects/{project.id}/ipcs/receivables-report/?near_due_days=7'
    resp = finance_client.get(url)
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data['summary']['overdue_count'] == 1
    assert data['summary']['near_due_count'] == 1
    assert Decimal(data['summary']['overdue_remaining']) == Decimal('1000')
    assert Decimal(data['summary']['near_due_remaining']) == Decimal('400')

    bands = {row['ipc_id']: row['band'] for row in data['items']}
    assert bands[str(overdue.id)] == 'overdue'
    assert bands[str(near.id)] == 'near_due'
    assert str(future.id) not in bands
    assert str(collected.id) not in bands

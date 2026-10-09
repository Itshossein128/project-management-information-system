from datetime import date
from decimal import Decimal

import pytest

from contracts.models import IPC, IPCCollection, IPCStatus


@pytest.mark.django_db
def test_collection_never_changes_status_or_amounts(finance_client, project, contract, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=201,
        gross_amount=Decimal('1000'),
        submitted_amount=Decimal('1000'),
        approved_amount=Decimal('1000'),
        net_amount=Decimal('900'),
        status=IPCStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/collections/'
    r1 = finance_client.post(
        url,
        {'amount': '400', 'collected_at': '2024-06-01'},
        format='json',
    )
    assert r1.status_code == 201, r1.content
    r2 = finance_client.post(
        url,
        {'amount': '500', 'collected_at': '2024-06-20'},
        format='json',
    )
    assert r2.status_code == 201, r2.content

    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.APPROVED
    assert ipc.gross_amount == Decimal('1000')
    assert ipc.submitted_amount == Decimal('1000')
    assert ipc.approved_amount == Decimal('1000')
    assert ipc.net_amount == Decimal('900')
    assert IPCCollection.objects.filter(ipc=ipc, is_deleted=False).count() == 2


@pytest.mark.django_db
def test_collection_rejected_when_not_approved(finance_client, project, contract, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=202,
        gross_amount=Decimal('100'),
        net_amount=Decimal('100'),
        status=IPCStatus.SUBMITTED,
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/collections/'
    resp = finance_client.post(
        url,
        {'amount': '50', 'collected_at': date.today().isoformat()},
        format='json',
    )
    assert resp.status_code == 400
    assert 'collection_requires_approved' in str(resp.json())

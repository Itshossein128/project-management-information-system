from datetime import date
from decimal import Decimal

import pytest

from contracts.models import IPC, IPCCollection, IPCStatus


@pytest.mark.django_db
def test_partial_collections_preserve_ipc_amounts(finance_client, project, contract, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=99,
        gross_amount=Decimal('1000'),
        net_amount=Decimal('900'),
        status=IPCStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/collections/'
    r1 = finance_client.post(
        url,
        {'amount': '300', 'collected_at': '2024-06-01', 'currency': 'IRR'},
        format='json',
    )
    assert r1.status_code == 201, r1.content
    r2 = finance_client.post(
        url,
        {'amount': '200', 'collected_at': '2024-06-15', 'currency': 'IRR'},
        format='json',
    )
    assert r2.status_code == 201, r2.content

    ipc.refresh_from_db()
    assert ipc.gross_amount == Decimal('1000')
    assert ipc.net_amount == Decimal('900')
    assert IPCCollection.objects.filter(ipc=ipc, is_deleted=False).count() == 2

    listing = finance_client.get(url)
    assert listing.status_code == 200
    assert Decimal(listing.json()['collections_total']) == Decimal('500')
    assert Decimal(listing.json()['remaining_receivable']) == Decimal('400')


@pytest.mark.django_db
def test_over_collection_rejected(finance_client, project, contract, user):
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=100,
        gross_amount=Decimal('100'),
        net_amount=Decimal('100'),
        status=IPCStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    url = f'/api/v1/projects/{project.id}/ipcs/{ipc.id}/collections/'
    resp = finance_client.post(
        url,
        {'amount': '150', 'collected_at': '2024-06-01'},
        format='json',
    )
    assert resp.status_code == 400
    assert 'collection_exceeds_payable' in str(resp.json())

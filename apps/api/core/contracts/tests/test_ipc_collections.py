from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from contracts.collection_service import add_collection
from contracts.models import IPC, IPCCollection, IPCStatus
from contracts.services.ipc_service import pay_ipc


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


@pytest.mark.django_db
def test_payment_after_collection_commit_does_not_fail_response(finance_client, ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.gross_amount = Decimal('100')
    ipc.net_amount = Decimal('100')
    ipc.save()

    def collect_then_pay(**kwargs):
        row = add_collection(**kwargs)
        # Another legal operation can commit before the view sends its response.
        pay_ipc(ipc, user, date(2024, 6, 1))
        return row

    with patch('contracts.collection_views.add_collection', side_effect=collect_then_pay):
        response = finance_client.post(
            f'/api/v1/projects/{ipc.project_id}/ipcs/{ipc.id}/collections/',
            {'amount': '70', 'collected_at': '2024-06-01'},
            format='json',
        )

    assert response.status_code == 201, response.content
    assert IPCCollection.objects.filter(ipc=ipc).count() == 1
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.PAID


@pytest.mark.django_db
def test_deleted_collection_releases_payable_capacity(finance_client, ipc, user):
    ipc.status = IPCStatus.APPROVED
    ipc.gross_amount = Decimal('100')
    ipc.net_amount = Decimal('100')
    ipc.save()
    row = add_collection(ipc=ipc, amount=Decimal('70'), collected_at=date.today(), user=user)
    base = f'/api/v1/projects/{ipc.project_id}/ipcs/{ipc.id}/collections/'

    assert finance_client.delete(f'{base}{row.pk}/').status_code == 204
    row.refresh_from_db()
    assert row.is_deleted
    response = finance_client.post(
        base, {'amount': '100', 'collected_at': '2024-06-01'}, format='json',
    )

    assert response.status_code == 201, response.content
    assert IPCCollection.objects.filter(ipc=ipc).count() == 1
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.APPROVED
    assert ipc.net_amount == Decimal('100')

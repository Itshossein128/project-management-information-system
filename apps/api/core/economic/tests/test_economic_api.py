"""Economic API endpoint tests."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost, CostCategory
from economic.models import EconomicSnapshot, InflationIndex


BASE = '/api/v1/projects/{project_id}/'


@pytest.fixture
def inflation_indices(db):
    InflationIndex.objects.create(
        index_name='CPI',
        index_date=date(2024, 1, 1),
        index_value=Decimal('100'),
    )
    InflationIndex.objects.create(
        index_name='CPI',
        index_date=date(2024, 6, 1),
        index_value=Decimal('110'),
    )


@pytest.mark.django_db
class TestEconomicSnapshotAPI:
    def test_snapshot_generates_on_demand(self, auth_client, project, contract, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        IPC.objects.create(
            project=project,
            contract=contract,
            ipc_number=1,
            status=IPCStatus.PAID,
            net_amount=Decimal('5000'),
            actual_payment_date=date(2024, 2, 1),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}economic/snapshot/?as_of=2024-06-01'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['revenue_to_date'] == '5000.00'
        assert 'inflation_detail' in resp.data
        assert len(resp.data['inflation_detail']) >= 1


@pytest.mark.django_db
class TestEconomicHistoryAPI:
    def test_history_lists_snapshots(self, auth_client, project, user):
        EconomicSnapshot.objects.create(
            project=project,
            snapshot_date=date(2024, 1, 1),
            actual_cost=Decimal('100'),
            revenue_to_date=Decimal('200'),
            accounting_profit=Decimal('100'),
        )
        url = f'{BASE.format(project_id=project.id)}economic/history/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1


@pytest.mark.django_db
class TestFinancingCostAPI:
    def test_financing_cost_endpoint(self, auth_client, project, contract, user):
        IPC.objects.create(
            project=project,
            contract=contract,
            ipc_number=1,
            status=IPCStatus.PAID,
            net_amount=Decimal('365000'),
            planned_payment_date=date(2024, 1, 1),
            actual_payment_date=date(2024, 1, 31),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}economic/financing-cost/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_financing_cost'] > 0
        assert len(resp.data['details']) == 1
        assert 'annual_financing_rate' in resp.data

    def test_payment_delay_alias(self, auth_client, project):
        url = f'{BASE.format(project_id=project.id)}economic/payment-delay/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_financing_cost' in resp.data


@pytest.mark.django_db
class TestSnapshotRefreshAPI:
    def test_refresh_regenerates_snapshot(self, auth_client, project, activity, user, inflation_indices):
        EconomicSnapshot.objects.create(
            project=project,
            snapshot_date=date(2024, 6, 1),
            actual_cost=Decimal('1'),
            inflation_adj_cost=Decimal('1'),
            financing_cost=Decimal('0'),
            revenue_to_date=Decimal('0'),
            accounting_profit=Decimal('-1'),
            real_profit=Decimal('-1'),
            economic_profit=Decimal('-1'),
            working_capital=Decimal('0'),
            avg_payment_delay_days=0,
        )
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}economic/snapshot/?as_of=2024-06-01&refresh=1'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert float(resp.data['actual_cost']) == pytest.approx(1000.0)

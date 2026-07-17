"""Economic engine service tests."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost, CostCategory
from economic.models import EconomicSnapshot, InflationIndex
from economic.services.financing_service import ANNUAL_FINANCING_RATE, compute_financing_cost
from economic.services.inflation_service import (
    adjust_cost_for_inflation,
    compute_total_inflation_adjusted_cost,
    get_index_value,
    inflation_detail_by_category,
)
from economic.services.monte_carlo_service import run_monte_carlo
from economic.services.snapshot_service import generate_snapshot


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
class TestInflationService:
    def test_get_index_value_uses_latest_on_or_before(self, inflation_indices):
        assert get_index_value('CPI', date(2024, 3, 15)) == pytest.approx(100.0)
        assert get_index_value('CPI', date(2024, 6, 1)) == pytest.approx(110.0)

    def test_get_index_value_defaults_when_missing(self, db):
        assert get_index_value('unknown', date.today()) == pytest.approx(100.0)

    def test_adjust_cost_for_inflation(self, project, inflation_indices):
        amount = adjust_cost_for_inflation(
            Decimal('1000'),
            CostCategory.OTHER,
            date(2024, 1, 1),
            date(2024, 6, 1),
            project_id=project.id,
        )
        assert amount == pytest.approx(1100.0)

    def test_compute_total_inflation_adjusted_cost(self, project, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        total = compute_total_inflation_adjusted_cost(project.id, date(2024, 6, 1))
        assert total == pytest.approx(1100.0)

    def test_inflation_detail_by_category(self, project, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        rows = inflation_detail_by_category(project.id, date(2024, 6, 1))
        assert len(rows) == 1
        assert rows[0]['cost_category'] == CostCategory.OTHER
        assert rows[0]['nominal_cost'] == pytest.approx(1000.0)
        assert rows[0]['adjusted_cost'] == pytest.approx(1100.0)
        assert rows[0]['inflation_factor'] == pytest.approx(1.1)


@pytest.mark.django_db
class TestFinancingService:
    def test_compute_financing_cost_for_delayed_payment(self, project, contract, user):
        ipc = IPC.objects.create(
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
        result = compute_financing_cost(project.id)
        expected = float(ipc.net_amount) * ANNUAL_FINANCING_RATE * 30 / 365
        assert result['total_financing_cost'] == pytest.approx(expected)
        assert result['avg_payment_delay_days'] == pytest.approx(30)
        assert len(result['details']) == 1

    def test_compute_financing_cost_ignores_on_time_payment(self, project, contract, user):
        IPC.objects.create(
            project=project,
            contract=contract,
            ipc_number=2,
            status=IPCStatus.PAID,
            net_amount=Decimal('100000'),
            planned_payment_date=date(2024, 2, 1),
            actual_payment_date=date(2024, 1, 15),
            created_by=user,
            updated_by=user,
        )
        result = compute_financing_cost(project.id)
        assert result['total_financing_cost'] == pytest.approx(0.0)
        assert result['details'] == []


@pytest.mark.django_db
class TestSnapshotService:
    def test_generate_snapshot_computes_profit_metrics(self, project, contract, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('500000'),
            cost_date=date(2024, 3, 1),
            created_by=user,
            updated_by=user,
        )
        IPC.objects.create(
            project=project,
            contract=contract,
            ipc_number=1,
            status=IPCStatus.PAID,
            net_amount=Decimal('800000'),
            actual_payment_date=date(2024, 3, 15),
            created_by=user,
            updated_by=user,
        )
        snapshot = generate_snapshot(project.id, date(2024, 3, 31))
        assert snapshot.actual_cost == pytest.approx(500000.0)
        assert snapshot.revenue_to_date == pytest.approx(800000.0)
        assert snapshot.accounting_profit == pytest.approx(300000.0)
        assert snapshot.inflation_adj_cost >= snapshot.actual_cost
        assert EconomicSnapshot.objects.filter(project=project, snapshot_date=date(2024, 3, 31)).exists()

    def test_generate_snapshot_is_idempotent(self, project, user):
        first = generate_snapshot(project.id, date(2024, 1, 1))
        second = generate_snapshot(project.id, date(2024, 1, 1))
        assert first.id == second.id


@pytest.mark.django_db
class TestMonteCarloService:
    def test_run_monte_carlo_returns_percentiles(self, project, contract, activity, user):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.LABOR,
            amount=Decimal('100000'),
            cost_date=date.today() - timedelta(days=30),
            created_by=user,
            updated_by=user,
        )
        result = run_monte_carlo(project.id, iterations=200, scenario_params={'inflation_rate_std': 0.01})
        assert 'p10' in result
        assert 'p50' in result
        assert 'p90' in result
        assert 0 <= result['prob_of_loss'] <= 1
        assert result['iterations'] == 200

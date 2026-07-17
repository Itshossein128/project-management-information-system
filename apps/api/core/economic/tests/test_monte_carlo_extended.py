"""Extended Monte Carlo service tests."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from cost_control.models import ActualCost, CostCategory
from economic.services.monte_carlo_service import run_monte_carlo


@pytest.mark.django_db
def test_productivity_factor_affects_profit(project, activity, user):
    ActualCost.objects.create(
        project=project,
        activity=activity,
        cost_category=CostCategory.LABOR,
        amount=Decimal('100000'),
        cost_date=date.today() - timedelta(days=30),
        created_by=user,
        updated_by=user,
    )
    high_prod = run_monte_carlo(
        project.id,
        iterations=300,
        scenario_params={
            'productivity_factor_mean': 1.2,
            'productivity_factor_std': 0.01,
            'inflation_rate_std': 0.01,
        },
    )
    low_prod = run_monte_carlo(
        project.id,
        iterations=300,
        scenario_params={
            'productivity_factor_mean': 0.7,
            'productivity_factor_std': 0.01,
            'inflation_rate_std': 0.01,
        },
    )
    assert high_prod['p50'] > low_prod['p50']


@pytest.mark.django_db
def test_max_working_capital_positive(project, activity, user):
    ActualCost.objects.create(
        project=project,
        activity=activity,
        cost_category=CostCategory.LABOR,
        amount=Decimal('500000'),
        cost_date=date.today() - timedelta(days=30),
        created_by=user,
        updated_by=user,
    )
    result = run_monte_carlo(project.id, iterations=200)
    assert result['max_working_capital'] > 0

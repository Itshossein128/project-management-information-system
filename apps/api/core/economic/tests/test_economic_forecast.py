"""Economic forecast and curve API tests."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import ActualCost, CostCategory
from economic.models import InflationIndex

BASE = '/api/v1/projects/{project_id}/economic/'


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
class TestEconomicForecastAPI:
    def test_forecast_endpoint(self, auth_client, project, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}forecast/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'bac' in resp.data
        assert 'eac_nominal' in resp.data
        assert 'eac_inflation_adjusted' in resp.data
        assert 'cpi' in resp.data
        assert resp.data['inflation_factor'] >= 1.0

    def test_working_capital_curve(self, auth_client, project, contract, activity, user):
        from contracts.models import IPC, IPCStatus

        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.LABOR,
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
            net_amount=Decimal('200000'),
            actual_payment_date=date(2024, 4, 1),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}working-capital/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'points' in resp.data
        assert resp.data['peak_working_capital'] >= 0

    def test_cash_flow_real(self, auth_client, project, activity, user, inflation_indices):
        ActualCost.objects.create(
            project=project,
            activity=activity,
            cost_category=CostCategory.OTHER,
            amount=Decimal('1000'),
            cost_date=date(2024, 1, 1),
            created_by=user,
            updated_by=user,
        )
        url = f'{BASE.format(project_id=project.id)}cash-flow-real/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['points']) >= 1
        point = resp.data['points'][0]
        assert point['real_outflow'] >= point['nominal_outflow']

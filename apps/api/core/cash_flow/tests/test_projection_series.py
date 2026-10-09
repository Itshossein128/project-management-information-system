from datetime import date
from decimal import Decimal

import pytest

from cash_flow.models import CashFlowForecast, CashTransaction, CashTransactionType
from cash_flow.services.projection_service import build_projected_series


@pytest.mark.django_db
def test_ipc_remaining_maps_to_projected_inflow(project, approved_ipc):
    data = build_projected_series(project.id, '2026-10', '2026-10')
    month = next(m for m in data['months'] if m['month'] == '2026-10-01')
    assert month['projected_inflow'] == 1200000.0
    assert month['inflow_status'] == 'registered'


@pytest.mark.django_db
def test_commitment_open_maps_to_projected_outflow(project, approved_commitment):
    data = build_projected_series(project.id, '2026-10', '2026-10')
    month = next(m for m in data['months'] if m['month'] == '2026-10-01')
    assert month['projected_outflow'] == 800000.0
    assert month['net_need'] == month['projected_inflow'] - month['projected_outflow']


@pytest.mark.django_db
def test_ipc_and_commitment_net_need(project, approved_ipc, approved_commitment):
    data = build_projected_series(project.id, '2026-10', '2026-10')
    month = next(m for m in data['months'] if m['month'] == '2026-10-01')
    assert month['projected_inflow'] == 1200000.0
    assert month['projected_outflow'] == 800000.0
    assert month['net_need'] == 400000.0


@pytest.mark.django_db
def test_projected_and_actual_keys_remain_separate(project, approved_ipc, user):
    CashTransaction.objects.create(
        project=project,
        tx_date=date(2026, 9, 10),
        tx_type=CashTransactionType.IN,
        category='other_income',
        amount=Decimal('500000'),
        created_by=user,
        updated_by=user,
    )
    data = build_projected_series(project.id, '2026-09', '2026-10')
    assert 'months' in data
    assert 'actual_months' in data
    assert data['series'] == 'projected'
    # keys must not be merged into a single list
    for m in data['months']:
        assert 'actual_inflow' not in m
        assert 'projected_inflow' in m
    for m in data['actual_months']:
        assert 'projected_inflow' not in m
        assert 'actual_inflow' in m


@pytest.mark.django_db
def test_no_ipcs_inflow_unregistered(project):
    data = build_projected_series(project.id, '2026-10', '2026-10')
    month = data['months'][0]
    assert month['inflow_status'] == 'unregistered'
    assert month['projected_inflow'] == 0.0


@pytest.mark.django_db
def test_manual_forecast_does_not_overwrite_projection(project, approved_ipc, user):
    CashFlowForecast.objects.create(
        project=project,
        month=date(2026, 10, 1),
        expected_inflow=Decimal('999'),
        expected_outflow=Decimal('1'),
        created_by=user,
        updated_by=user,
    )
    data = build_projected_series(project.id, '2026-10', '2026-10')
    month = next(m for m in data['months'] if m['month'] == '2026-10-01')
    assert month['projected_inflow'] == 1200000.0
    assert any(f['expected_inflow'] == 999.0 for f in data['manual_forecast_months'])


@pytest.mark.django_db
def test_projection_api_endpoint(auth_client, project, approved_ipc, approved_commitment):
    url = f'/api/v1/projects/{project.id}/cash-flow/projection/?from=2026-10&to=2026-10'
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['series'] == 'projected'
    assert 'months' in resp.data
    assert 'actual_months' in resp.data

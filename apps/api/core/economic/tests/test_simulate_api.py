"""Simulation API tests."""

from unittest.mock import patch

import pytest
from rest_framework import status

from economic.models import SimulationResult

BASE = '/api/v1/projects/{project_id}/economic/'


@pytest.mark.django_db
def test_latest_simulation_includes_p10_aliases(auth_client, project):
    SimulationResult.objects.create(
        project=project,
        iterations=1000,
        p10_profit=100,
        p50_profit=200,
        p90_profit=300,
        prob_of_loss=0.1,
        max_working_capital=50000,
        sensitivity_json=[{
            'variable': 'تورم',
            'low_profit': 50,
            'high_profit': 250,
            'impact': 200,
        }],
    )
    url = f'{BASE.format(project_id=project.id)}simulate/latest/'
    resp = auth_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    result = resp.data['result']
    assert float(result['p10_profit']) == 100
    assert float(result['p10']) == 100
    assert float(result['p50']) == 200


@pytest.mark.django_db
@patch('economic.views.run_monte_carlo_task')
def test_simulate_returns_task_id(mock_task, auth_client, project):
    mock_task.delay.return_value.id = 'test-task-123'
    url = f'{BASE.format(project_id=project.id)}simulate/'
    resp = auth_client.post(url, {'iterations': 1000}, format='json')
    assert resp.status_code == status.HTTP_202_ACCEPTED
    assert resp.data['task_id'] == 'test-task-123'


@pytest.mark.django_db
def test_sensitivity_endpoint(auth_client, project):
    SimulationResult.objects.create(
        project=project,
        iterations=500,
        sensitivity_json=[{
            'variable': 'تورم',
            'low_profit': 1,
            'high_profit': 2,
            'impact': 1,
        }],
    )
    url = f'{BASE.format(project_id=project.id)}sensitivity/'
    resp = auth_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['sensitivity']) == 1

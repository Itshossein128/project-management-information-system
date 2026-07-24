"""Tests for unified project KPI endpoint (K-02)."""

import pytest
from django.utils import timezone
from rest_framework import status

from alerts.models import AlertLog, AlertRule, AlertType
from cash_flow.models import CashTransaction, CashTransactionType


@pytest.mark.django_db
class TestProjectKpisApi:
    def test_unauthenticated(self, api_client, project):
        resp = api_client.get(f'/api/v1/projects/{project.id}/kpis/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_kpis_shape(self, auth_client, project, user):
        CashTransaction.objects.create(
            project=project,
            tx_date=timezone.localdate(),
            tx_type=CashTransactionType.IN,
            amount=1_000_000,
            category='other_income',
            created_by=user,
            updated_by=user,
        )
        CashTransaction.objects.create(
            project=project,
            tx_date=timezone.localdate(),
            tx_type=CashTransactionType.OUT,
            amount=400_000,
            category='other_expense',
            created_by=user,
            updated_by=user,
        )
        rule = AlertRule.objects.create(
            project=project,
            alert_type=AlertType.BUDGET_OVERRUN,
            name='Budget',
            notify_roles='project_manager',
        )
        AlertLog.objects.create(
            rule=rule,
            project=project,
            trigger_reference='test',
            message='over',
        )

        resp = auth_client.get(f'/api/v1/projects/{project.id}/kpis/')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data
        assert 'as_of' in data
        assert 'physical_progress' in data
        assert 'spi' in data['physical_progress']
        assert 'cost' in data
        assert 'cpi' in data['cost']
        assert 'cash' in data
        assert float(data['cash']['total_received']) == 1_000_000
        assert float(data['cash']['total_paid_out']) == 400_000
        assert float(data['cash']['net_balance']) == 600_000
        assert 'schedule' in data
        assert 'critical_activities' in data['schedule']
        assert data['alerts']['unacknowledged_total'] == 1
        assert 'panel' in data
        assert data['panel']['open_alerts'] == 1
        assert data['panel']['net_cash'] == 600_000

    def test_health_alias(self, auth_client, project):
        kpis = auth_client.get(f'/api/v1/projects/{project.id}/kpis/')
        health = auth_client.get(f'/api/v1/projects/{project.id}/health/')
        assert health.status_code == status.HTTP_200_OK
        assert health.data['as_of'] == kpis.data['as_of']
        assert set(health.data.keys()) == set(kpis.data.keys())

    def test_force_refresh(self, auth_client, project):
        r1 = auth_client.get(f'/api/v1/projects/{project.id}/kpis/')
        r2 = auth_client.get(f'/api/v1/projects/{project.id}/kpis/?force_refresh=1')
        assert r1.status_code == 200
        assert r2.status_code == 200

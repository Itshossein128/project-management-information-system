"""Alert REST API tests."""

from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from alerts.models import AlertLog, AlertRule
from alerts.services.alert_engine import fire_alert


BASE = '/api/v1/projects/{project_id}/'


@pytest.fixture
def project_rule(db, project):
    return AlertRule.objects.create(
        project=project,
        alert_type='budget_overrun',
        name='بودجه پروژه',
        threshold=Decimal('80'),
        notify_roles='project_manager',
        is_active=True,
    )


@pytest.fixture
def alert_log(db, project, project_rule, user):
    return fire_alert(
        project_rule.id,
        'wbs:1',
        'بودجه WBS از ۸۰٪ گذشته',
        project.id,
    )


@pytest.mark.django_db
class TestAlertRuleAPI:
    def test_list_rules_includes_system_and_project(self, auth_client, project, project_rule):
        AlertRule.objects.create(
            project=None,
            alert_type='baseline_not_set',
            name='خط مبنا',
            threshold=0,
            is_active=True,
        )
        url = f'{BASE.format(project_id=project.id)}alert-rules/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        types = {r['alert_type'] for r in resp.data['results']}
        assert 'budget_overrun' in types
        assert 'baseline_not_set' in types

    def test_create_project_rule(self, auth_client, project):
        url = f'{BASE.format(project_id=project.id)}alert-rules/'
        resp = auth_client.post(
            url,
            {
                'alert_type': 'low_stock',
                'name': 'موجودی کم',
                'threshold_value': '0',
                'notify_roles': 'project_manager',
                'cooldown_hours': 12,
                'is_active': True,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['alert_type'] == 'low_stock'

    def test_patch_rule(self, auth_client, project, project_rule):
        url = f'{BASE.format(project_id=project.id)}alert-rules/{project_rule.id}/'
        resp = auth_client.patch(url, {'threshold_value': '95'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['threshold_value'] == '95.0000'

    def test_delete_project_rule_soft_deletes(self, auth_client, project, project_rule):
        url = f'{BASE.format(project_id=project.id)}alert-rules/{project_rule.id}/'
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        project_rule.refresh_from_db()
        assert project_rule.is_deleted is True

    def test_cannot_delete_system_rule(self, auth_client, project):
        system_rule = AlertRule.objects.filter(project__isnull=True).first()
        url = f'{BASE.format(project_id=project.id)}alert-rules/{system_rule.id}/'
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAlertLogAPI:
    def test_list_alerts(self, auth_client, project, alert_log):
        url = f'{BASE.format(project_id=project.id)}alerts/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1

    def test_list_unacknowledged_only(self, auth_client, project, project_rule):
        fire_alert(project_rule.id, 'ref:1', 'پیام اول', project.id)
        log2 = fire_alert(project_rule.id, 'ref:2', 'پیام دوم', project.id)
        log2.acknowledged_at = timezone.now()
        log2.save(update_fields=['acknowledged_at'])

        url = f'{BASE.format(project_id=project.id)}alerts/?acknowledged=false'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1

    def test_acknowledge_alert(self, auth_client, project, alert_log):
        url = f'{BASE.format(project_id=project.id)}alerts/{alert_log.id}/acknowledge/'
        resp = auth_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        alert_log.refresh_from_db()
        assert alert_log.acknowledged_at is not None

    def test_active_counts(self, auth_client, project, project_rule):
        fire_alert(project_rule.id, 'ref:a', 'A', project.id)
        fire_alert(project_rule.id, 'ref:b', 'B', project.id)
        url = f'{BASE.format(project_id=project.id)}alerts/active/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total'] == 2
        assert resp.data['counts']['budget_overrun'] == 2

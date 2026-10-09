"""Schedule status report + critical-path validity (US4)."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.services.critical_path_validity import evaluate_critical_path_validity
from wbs.services import create_wbs_node

BASE = '/api/v1/projects/{project_id}/'


@pytest.fixture
def activities_complete(project, user):
    wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    a1 = Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A-100',
        activity_name='Work',
        planned_start=date(2026, 4, 1),
        planned_finish=date(2026, 4, 10),
        forecast_finish=date(2026, 4, 15),
        duration_days=8,
        created_by=user,
        updated_by=user,
    )
    m1 = Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='M-1',
        activity_name='Foundation complete',
        is_milestone=True,
        duration_days=0,
        planned_finish=date(2026, 4, 10),
        forecast_finish=date(2026, 4, 12),
        created_by=user,
        updated_by=user,
    )
    bl = BaselineSchedule.objects.create(
        project=project,
        version_name='BL-1',
        is_current=True,
        is_locked=True,
        approved_at=date(2026, 1, 1),
        approved_by=user,
        created_by=user,
        updated_by=user,
    )
    BaselineActivity.objects.create(
        baseline=bl,
        activity=a1,
        planned_finish=date(2026, 4, 8),
        is_critical=True,
        total_float=0,
    )
    BaselineActivity.objects.create(
        baseline=bl,
        activity=m1,
        planned_finish=date(2026, 4, 10),
        is_critical=False,
        total_float=2,
    )
    return {'a1': a1, 'm1': m1, 'baseline': bl, 'wbs': wbs}


@pytest.mark.django_db
class TestScheduleStatus:
    def test_status_shape(self, auth_client, project, activities_complete):
        resp = auth_client.get(f'{BASE.format(project_id=project.id)}schedule-status/')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data
        assert 'as_of' in data
        assert 'forecast_project_finish' in data
        assert 'date_sets' in data
        assert data['date_sets']['has_planned'] is True
        assert data['date_sets']['has_forecast'] is True
        assert 'critical_path' in data
        assert isinstance(data['milestones'], list)
        assert len(data['milestones']) >= 1
        m = data['milestones'][0]
        assert 'planned_finish' in m
        assert 'forecast_finish' in m
        assert 'baseline_finish' in m
        assert 'actual_finish' in m
        assert isinstance(data['delays'], list)


@pytest.mark.django_db
class TestCriticalPathValidity:
    def test_incomplete_durations_invalid(self, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A1',
            activity_name='No duration',
            created_by=user,
            updated_by=user,
        )
        result = evaluate_critical_path_validity(project.id)
        assert result['valid'] is False
        assert 'incomplete_durations' in result['reason_codes']
        assert result['critical_activity_ids'] == []
        assert result['near_critical_activity_ids'] == []

        resp_api = None
        # also via status endpoint shape
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=user)
        resp_api = client.get(f'{BASE.format(project_id=project.id)}schedule-status/')
        assert resp_api.status_code == 200
        assert resp_api.data['critical_path']['valid'] is False
        assert resp_api.data['critical_path']['critical_activity_ids'] == []

    def test_complete_data_may_expose_critical(self, project, activities_complete):
        result = evaluate_critical_path_validity(project.id)
        assert result['valid'] is True
        assert str(activities_complete['a1'].id) in result['critical_activity_ids']
        # float 2 ≤ 5 and not critical → near-critical
        assert str(activities_complete['m1'].id) in result['near_critical_activity_ids']


@pytest.mark.django_db
class TestActivityNetworkCriticalGate:
    def test_network_clears_critical_when_invalid(self, auth_client, project, user):
        from schedule.services.activity_service import get_activity_network

        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        act = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A-X',
            activity_name='No duration',
            created_by=user,
            updated_by=user,
        )
        bl = BaselineSchedule.objects.create(
            project=project,
            version_name='BL',
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        BaselineActivity.objects.create(baseline=bl, activity=act, is_critical=True)

        data = get_activity_network(project.id)
        assert data['critical_path']['valid'] is False
        assert all(not n['is_critical'] for n in data['nodes'])

        resp = auth_client.get(f'{BASE.format(project_id=project.id)}activities/network/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['critical_path']['valid'] is False

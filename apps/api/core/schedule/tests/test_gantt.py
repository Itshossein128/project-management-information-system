"""Gantt chart service and API tests."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity, ActivityRelation
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule
from schedule.services.gantt_service import get_gantt_data


BASE = '/api/v1/projects/{project_id}/'


@pytest.mark.django_db
class TestGanttService:
    def test_get_gantt_data_includes_activity_and_baseline(self, project, activity, user, wbs):
        activity.planned_start = date(2024, 1, 1)
        activity.planned_finish = date(2024, 1, 31)
        activity.save(update_fields=['planned_start', 'planned_finish'])

        baseline = BaselineSchedule.objects.create(
            project=project,
            version_name='BL-1',
            is_current=True,
        )
        BaselineActivity.objects.create(
            baseline=baseline,
            activity=activity,
            planned_start=date(2024, 1, 5),
            planned_finish=date(2024, 1, 25),
            is_critical=True,
        )
        ActivityProgress.objects.create(
            activity=activity,
            report_date=date(2024, 1, 15),
            actual_progress=0.5,
        )

        data = get_gantt_data(project.id)
        assert data['baseline_name'] == 'BL-1'
        assert data['project_start'] == '2024-01-01'
        assert data['project_end'] == '2024-01-31'
        assert len(data['tasks']) == 1

        task = data['tasks'][0]
        assert task['id'] == activity.activity_code
        assert task['progress'] == 50
        assert task['is_critical'] is True
        assert task['baseline_start'] == '2024-01-05'
        assert task['wbs_code'] == wbs.wbs_code

    def test_get_gantt_data_resolves_dependencies(self, project, user, wbs):
        a1 = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A1',
            activity_name='First',
            planned_start=date(2024, 1, 1),
            planned_finish=date(2024, 1, 10),
            created_by=user,
            updated_by=user,
        )
        a2 = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A2',
            activity_name='Second',
            planned_start=date(2024, 1, 11),
            planned_finish=date(2024, 1, 20),
            created_by=user,
            updated_by=user,
        )
        ActivityRelation.objects.create(
            predecessor=a1,
            successor=a2,
            relation_type='FS',
            created_by=user,
            updated_by=user,
        )

        data = get_gantt_data(project.id)
        by_code = {t['id']: t for t in data['tasks']}
        assert by_code['A2']['dependencies'] == 'A1'


@pytest.mark.django_db
class TestGanttAPI:
    def test_gantt_data_endpoint(self, auth_client, project, activity):
        activity.planned_start = date(2024, 2, 1)
        activity.planned_finish = date(2024, 2, 28)
        activity.save(update_fields=['planned_start', 'planned_finish'])

        url = f'{BASE.format(project_id=project.id)}gantt/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'tasks' in resp.data
        assert 'baselines' in resp.data
        assert len(resp.data['tasks']) >= 1

    def test_gantt_pdf_endpoint(self, auth_client, project, activity):
        activity.planned_start = date(2024, 2, 1)
        activity.planned_finish = date(2024, 2, 28)
        activity.save(update_fields=['planned_start', 'planned_finish'])

        url = f'{BASE.format(project_id=project.id)}gantt/pdf/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp['Content-Type'] == 'application/pdf'
        assert len(resp.content) > 100

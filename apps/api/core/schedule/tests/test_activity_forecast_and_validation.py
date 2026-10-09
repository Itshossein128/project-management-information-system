"""Activity forecast fields + date/milestone/calendar validation (US1)."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity
from schedule.models import WorkingCalendar
from wbs.services import create_wbs_node

ACTIVITIES = '/api/v1/projects/{project_id}/activities/'


@pytest.fixture
def wbs_root(project):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    return node


@pytest.fixture
def default_calendar(project, user):
    return WorkingCalendar.objects.create(
        project=project,
        name='Default',
        is_default=True,
        work_monday=True,
        work_tuesday=True,
        work_wednesday=True,
        work_thursday=True,
        work_friday=True,
        work_saturday=False,
        work_sunday=False,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestActivityForecastFields:
    def test_model_fields_defaults(self, project, wbs_root, user):
        act = Activity.objects.create(
            project=project,
            wbs=wbs_root,
            activity_code='A1',
            activity_name='Act',
            created_by=user,
            updated_by=user,
        )
        assert act.duration_days is None
        assert act.is_milestone is False
        assert act.forecast_start is None
        assert act.forecast_finish is None
        assert act.working_calendar_id is None

    def test_create_persists_forecast_without_clearing_planned(self, auth_client, project, wbs_root):
        url = ACTIVITIES.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'A-100',
                'activity_name': 'Pour foundation',
                'planned_start': '2026-04-01',
                'planned_finish': '2026-04-10',
                'forecast_start': '2026-04-02',
                'forecast_finish': '2026-04-12',
                'duration_days': 8,
                'is_milestone': False,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content
        body = resp.data
        assert body['planned_start'] is not None
        assert body['forecast_start'] is not None
        assert body['duration_days'] == 8
        assert body['is_milestone'] is False

        # PATCH forecast only — planned stays
        act_id = body['activity_id']
        patch = auth_client.patch(
            f'{url}{act_id}/',
            {'forecast_finish': '2026-04-15'},
            format='json',
        )
        assert patch.status_code == status.HTTP_200_OK, patch.content
        assert patch.data['planned_start'] == body['planned_start']
        assert patch.data['planned_finish'] == body['planned_finish']
        assert patch.data['forecast_finish'] is not None

    def test_milestone_zero_duration(self, auth_client, project, wbs_root):
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'M-1',
                'activity_name': 'Foundation complete',
                'is_milestone': True,
                'duration_days': 0,
                'planned_start': '2026-04-10',
                'planned_finish': '2026-04-10',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content
        assert resp.data['is_milestone'] is True
        assert resp.data['duration_days'] == 0


@pytest.mark.django_db
class TestActivityValidation:
    def test_impossible_planned_dates(self, auth_client, project, wbs_root):
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'A1',
                'activity_name': 'Bad',
                'planned_start': '2026-04-10',
                'planned_finish': '2026-04-01',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'impossible_planned_dates'

    def test_impossible_forecast_dates(self, auth_client, project, wbs_root):
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'A1',
                'activity_name': 'Bad',
                'forecast_start': '2026-04-10',
                'forecast_finish': '2026-04-01',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'impossible_forecast_dates'

    def test_invalid_milestone(self, auth_client, project, wbs_root):
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'M1',
                'activity_name': 'Bad milestone',
                'is_milestone': True,
                'duration_days': 5,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'invalid_milestone'

    def test_milestone_null_duration_rejected(self, auth_client, project, wbs_root):
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'M2',
                'activity_name': 'Null duration milestone',
                'is_milestone': True,
                'duration_days': None,
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'invalid_milestone'

    def test_non_working_day(self, auth_client, project, wbs_root, default_calendar):
        # 2026-04-04 is Saturday
        resp = auth_client.post(
            ACTIVITIES.format(project_id=project.id),
            {
                'wbs_id': str(wbs_root.id),
                'activity_code': 'A1',
                'activity_name': 'Weekend start',
                'planned_start': '2026-04-04',
                'planned_finish': '2026-04-06',
                'working_calendar_id': str(default_calendar.id),
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'non_working_day'

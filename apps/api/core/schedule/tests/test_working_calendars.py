"""Working calendar CRUD + exceptions (US1)."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity
from schedule.models import CalendarException, WorkingCalendar
from schedule.services.calendar_service import is_working_day
from wbs.services import create_wbs_node

BASE = '/api/v1/projects/{project_id}/working-calendars/'


@pytest.mark.django_db
class TestWorkingCalendarModels:
    def test_working_calendar_fields(self, project, user):
        cal = WorkingCalendar.objects.create(
            project=project,
            name='Standard',
            is_default=True,
            created_by=user,
            updated_by=user,
        )
        assert cal.work_monday is True
        assert cal.work_saturday is False
        assert cal.is_default is True

    def test_calendar_exception_unique(self, project, user):
        cal = WorkingCalendar.objects.create(
            project=project,
            name='Std',
            created_by=user,
            updated_by=user,
        )
        CalendarException.objects.create(
            calendar=cal,
            exception_date=date(2026, 3, 21),
            is_working=False,
            name='Nowruz',
            created_by=user,
            updated_by=user,
        )
        with pytest.raises(Exception):
            CalendarException.objects.create(
                calendar=cal,
                exception_date=date(2026, 3, 21),
                is_working=False,
                created_by=user,
                updated_by=user,
            )


@pytest.mark.django_db
class TestWorkingCalendarAPI:
    def test_create_default_clears_other(self, auth_client, project, user):
        url = BASE.format(project_id=project.id)
        r1 = auth_client.post(
            url,
            {
                'name': 'Cal A',
                'is_default': True,
                'work_monday': True,
                'work_tuesday': True,
                'work_wednesday': True,
                'work_thursday': True,
                'work_friday': True,
                'work_saturday': False,
                'work_sunday': False,
            },
            format='json',
        )
        assert r1.status_code == status.HTTP_201_CREATED
        r2 = auth_client.post(
            url,
            {'name': 'Cal B', 'is_default': True},
            format='json',
        )
        assert r2.status_code == status.HTTP_201_CREATED
        assert WorkingCalendar.objects.filter(project=project, is_default=True).count() == 1
        assert WorkingCalendar.objects.get(pk=r2.data['id']).is_default is True

    def test_list_and_exception_crud(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        created = auth_client.post(url, {'name': 'Std', 'is_default': True}, format='json')
        cal_id = created.data['id']
        exc_url = f'{url}{cal_id}/exceptions/'
        resp = auth_client.post(
            exc_url,
            {'exception_date': '2026-03-21', 'is_working': False, 'name': 'Nowruz'},
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dup = auth_client.post(
            exc_url,
            {'exception_date': '2026-03-21', 'is_working': True},
            format='json',
        )
        assert dup.status_code == status.HTTP_409_CONFLICT
        assert dup.data['error']['code'] == 'calendar_exception_duplicate'

    def test_delete_blocked_when_in_use(self, auth_client, project, user):
        url = BASE.format(project_id=project.id)
        created = auth_client.post(url, {'name': 'Used', 'is_default': False}, format='json')
        cal_id = created.data['id']
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A1',
            activity_name='Act',
            working_calendar_id=cal_id,
            created_by=user,
            updated_by=user,
        )
        resp = auth_client.delete(f'{url}{cal_id}/')
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert resp.data['error']['code'] == 'calendar_in_use'

    def test_is_working_day_respects_exception(self, project, user):
        cal = WorkingCalendar.objects.create(
            project=project,
            name='Std',
            work_saturday=False,
            created_by=user,
            updated_by=user,
        )
        # 2026-04-04 is a Saturday
        sat = date(2026, 4, 4)
        assert is_working_day(cal, sat) is False
        CalendarException.objects.create(
            calendar=cal,
            exception_date=sat,
            is_working=True,
            name='Extra',
            created_by=user,
            updated_by=user,
        )
        assert is_working_day(cal, sat) is True

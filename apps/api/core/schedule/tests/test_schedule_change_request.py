"""Schedule change request workflow (US3)."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule, ScheduleChangeRequestStatus
from wbs.services import create_wbs_node

BASE = '/api/v1/projects/{project_id}/'


@pytest.fixture
def setup_locked(auth_client, project, user):
    wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    act = Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A1',
        activity_name='Act',
        planned_start=date(2026, 4, 1),
        planned_finish=date(2026, 4, 10),
        duration_days=8,
        created_by=user,
        updated_by=user,
    )
    url = BASE.format(project_id=project.id)
    create = auth_client.post(f'{url}baselines/', {'version_name': 'BL-1'}, format='json')
    bl_id = create.data['id']
    auth_client.post(f'{url}baselines/{bl_id}/approve-lock/')
    return {'activity': act, 'baseline_id': bl_id, 'url': url}


@pytest.mark.django_db
class TestScheduleChangeRequestSubmit:
    def test_submit_requires_impact_fields(self, auth_client, setup_locked):
        url = setup_locked['url']
        create = auth_client.post(
            f'{url}schedule-change-requests/',
            {'reason': '', 'milestone_impact': '', 'cost_impact': '', 'contract_impact': ''},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        scr_id = create.data['id']
        submit = auth_client.post(f'{url}schedule-change-requests/{scr_id}/submit/')
        assert submit.status_code == status.HTTP_400_BAD_REQUEST

    def test_only_one_submitted(self, auth_client, setup_locked):
        url = setup_locked['url']
        payload = {
            'reason': 'Delay',
            'milestone_impact': 'M1 slips',
            'cost_impact': 'None',
            'contract_impact': 'None',
        }
        first = auth_client.post(f'{url}schedule-change-requests/', payload, format='json')
        auth_client.post(f'{url}schedule-change-requests/{first.data["id"]}/submit/')
        second = auth_client.post(f'{url}schedule-change-requests/', payload, format='json')
        conflict = auth_client.post(f'{url}schedule-change-requests/{second.data["id"]}/submit/')
        assert conflict.status_code == status.HTTP_409_CONFLICT
        assert conflict.data['error']['code'] == 'schedule_change_in_flight'


@pytest.mark.django_db
class TestScheduleChangeRequestApproveReject:
    def test_approve_applies_items_and_creates_locked_baseline(self, auth_client, setup_locked):
        url = setup_locked['url']
        act = setup_locked['activity']
        prior_id = setup_locked['baseline_id']

        create = auth_client.post(
            f'{url}schedule-change-requests/',
            {
                'reason': 'Weather delay',
                'milestone_impact': 'Foundation slips 10d',
                'cost_impact': 'Low',
                'contract_impact': 'EOT request',
                'items': [
                    {
                        'activity_id': str(act.id),
                        'proposed_planned_start': '2026-05-01',
                        'proposed_planned_finish': '2026-05-20',
                        'proposed_duration_days': 15,
                        'proposed_forecast_finish': '2026-05-22',
                    }
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.content
        scr_id = create.data['id']
        assert len(create.data['items']) == 1

        submit = auth_client.post(f'{url}schedule-change-requests/{scr_id}/submit/')
        assert submit.status_code == status.HTTP_200_OK, submit.content
        assert submit.data['status'] == ScheduleChangeRequestStatus.SUBMITTED

        approve = auth_client.post(
            f'{url}schedule-change-requests/{scr_id}/approve/',
            {'decision_notes': 'Approved by PM'},
            format='json',
        )
        assert approve.status_code == status.HTTP_200_OK, approve.content
        assert approve.data['status'] == ScheduleChangeRequestStatus.APPROVED
        assert approve.data['resulting_baseline_id'] is not None

        act.refresh_from_db()
        assert act.planned_start == date(2026, 5, 1)
        assert act.planned_finish == date(2026, 5, 20)
        assert act.duration_days == 15

        new_bl = BaselineSchedule.objects.get(pk=approve.data['resulting_baseline_id'])
        assert new_bl.is_locked is True
        assert new_bl.is_current is True
        assert new_bl.source_change_request_id == approve.data['id'] or str(new_bl.source_change_request_id) == str(scr_id)

        prior = BaselineSchedule.objects.get(pk=prior_id)
        assert prior.is_locked is True
        assert prior.is_current is False
        assert BaselineActivity.objects.filter(baseline=prior).exists()

    def test_reject_creates_no_baseline(self, auth_client, setup_locked):
        url = setup_locked['url']
        before = BaselineSchedule.objects.filter(project_id=setup_locked['activity'].project_id).count()
        create = auth_client.post(
            f'{url}schedule-change-requests/',
            {
                'reason': 'No',
                'milestone_impact': 'n/a',
                'cost_impact': 'n/a',
                'contract_impact': 'n/a',
            },
            format='json',
        )
        scr_id = create.data['id']
        auth_client.post(f'{url}schedule-change-requests/{scr_id}/submit/')
        reject = auth_client.post(
            f'{url}schedule-change-requests/{scr_id}/reject/',
            {'decision_notes': 'Insufficient analysis'},
            format='json',
        )
        assert reject.status_code == status.HTTP_200_OK
        assert reject.data['status'] == ScheduleChangeRequestStatus.REJECTED
        assert reject.data['resulting_baseline_id'] is None
        assert BaselineSchedule.objects.filter(project_id=setup_locked['activity'].project_id).count() == before

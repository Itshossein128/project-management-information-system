"""Baseline approve-lock and snapshot immutability (US2)."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule
from wbs.services import create_wbs_node

BASE = '/api/v1/projects/{project_id}/'


@pytest.fixture
def live_activity(project, user):
    wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    return Activity.objects.create(
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


@pytest.mark.django_db
class TestBaselineLockFields:
    def test_baseline_lock_defaults(self, project, user):
        bl = BaselineSchedule.objects.create(
            project=project, version_name='BL-1', created_by=user, updated_by=user,
        )
        assert bl.is_locked is False
        assert bl.locked_at is None
        assert bl.locked_by_id is None
        assert bl.source_change_request_id is None
        assert bl.created_by_id == user.id
        assert bl.is_deleted is False


@pytest.mark.django_db
class TestBaselineApproveLock:
    def test_approve_lock_sets_flags_and_demotes_prior(self, auth_client, project, live_activity, user):
        url = BASE.format(project_id=project.id)
        prior = BaselineSchedule.objects.create(
            project=project,
            version_name='BL-0',
            is_current=True,
            is_locked=True,
            approved_at=date(2026, 1, 1),
            approved_by=user,
            created_by=user,
            updated_by=user,
        )
        create = auth_client.post(
            f'{url}baselines/',
            {'version_name': 'BL-1'},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        bl_id = create.data['id']
        assert create.data['is_locked'] is False

        lock = auth_client.post(f'{url}baselines/{bl_id}/approve-lock/')
        assert lock.status_code == status.HTTP_200_OK, lock.content
        assert lock.data['is_locked'] is True
        assert lock.data['is_current'] is True
        assert lock.data['locked_at'] is not None
        assert lock.data['approved_at'] is not None

        prior.refresh_from_db()
        assert prior.is_current is False
        assert BaselineSchedule.objects.filter(pk=prior.pk).exists()

        again = auth_client.post(f'{url}baselines/{bl_id}/approve-lock/')
        assert again.status_code == status.HTTP_409_CONFLICT
        assert again.data['error']['code'] == 'baseline_already_locked'

    def test_live_patch_does_not_mutate_locked_snapshot(self, auth_client, project, live_activity):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(f'{url}baselines/', {'version_name': 'BL-1'}, format='json')
        bl_id = create.data['id']
        auth_client.post(f'{url}baselines/{bl_id}/approve-lock/')

        ba = BaselineActivity.objects.get(baseline_id=bl_id, activity=live_activity)
        snap_start = ba.planned_start
        snap_finish = ba.planned_finish

        patch = auth_client.patch(
            f'{url}activities/{live_activity.id}/',
            {'planned_start': '2026-05-01', 'planned_finish': '2026-05-20'},
            format='json',
        )
        assert patch.status_code == status.HTTP_200_OK, patch.content
        ba.refresh_from_db()
        assert ba.planned_start == snap_start
        assert ba.planned_finish == snap_finish

    def test_mutate_locked_baseline_activity_rejected(self, auth_client, project, live_activity):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(f'{url}baselines/', {'version_name': 'BL-1'}, format='json')
        bl_id = create.data['id']
        auth_client.post(f'{url}baselines/{bl_id}/approve-lock/')
        ba = BaselineActivity.objects.get(baseline_id=bl_id, activity=live_activity)

        resp = auth_client.patch(
            f'{url}baselines/{bl_id}/activities/{ba.id}/',
            {'planned_finish': '2026-12-31'},
            format='json',
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert resp.data['error']['code'] == 'baseline_locked'

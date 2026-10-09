import pytest

from schedule.models import ActivityProgress


def _manual(client, project, activity, pct, date, **extra):
    return client.post(
        f'/api/v1/projects/{project.id}/progress/manual/',
        {'activity_id': str(activity.id), 'report_date': date, 'actual_progress': pct, **extra},
        format='json',
    )


def _row(client, project, activity, **params):
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    response = client.get(f'/api/v1/projects/{project.id}/progress/activities/?{query}')
    assert response.status_code == 200
    return next(r for r in response.data if r['activity_id'] == str(activity.id))


@pytest.mark.django_db
class TestProgressFourWay:
    @pytest.fixture(autouse=True)
    def _weighted(self, activity):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])

    def test_manual_sets_period_cumulative_and_not_approved(
        self, project, activity, approved_measurement, auth_client,
    ):
        first = _manual(auth_client, project, activity, 20, '2024-10-01')
        second = _manual(auth_client, project, activity, 35, '2024-10-03')
        assert first.status_code == second.status_code == 201
        assert first.data['period_progress'] == pytest.approx(0.2)
        assert second.data['period_progress'] == pytest.approx(0.15)
        assert second.data['cumulative_progress'] == pytest.approx(0.35)
        assert second.data['approved_progress'] is None
        assert second.data['measurement_version_id'] == str(approved_measurement.current_version_id)
        row = ActivityProgress.objects.get(activity=activity, report_date='2024-10-03')
        assert row.approved_progress is None
        assert row.technical_approved_at is None

    def test_breakdown_exposes_four_way_fields(self, project, activity, approved_measurement, auth_client):
        ActivityProgress.objects.create(activity=activity, report_date='2024-10-01', planned_progress=0.5)
        _manual(auth_client, project, activity, 20, '2024-10-02')
        _manual(auth_client, project, activity, 40, '2024-10-04')
        row = _row(
            auth_client, project, activity,
            as_of='2024-10-05', period_start='2024-10-03', period_end='2024-10-05',
        )
        assert row['cumulative_progress_pct'] == 40.0
        assert row['actual_progress_pct'] == 40.0
        assert row['period_progress_pct'] == 20.0
        assert row['approved_progress_pct'] == 0.0
        assert row['measurement_method'] == 'quantity'
        assert row['measurement_status'] == 'approved'
        assert row['measurement_version_id'] == str(approved_measurement.current_version_id)
        assert row['period_start'] == '2024-10-03'
        assert row['period_end'] == '2024-10-05'
        assert row['wbs_code'] == '1'

    def test_default_period_is_current_week(self, project, activity, approved_measurement, auth_client):
        _manual(auth_client, project, activity, 10, '2024-10-02')
        # 2024-10-04 is a Friday; week is Mon 2024-09-30 .. Sun 2024-10-06.
        row = _row(auth_client, project, activity, as_of='2024-10-04')
        assert row['period_start'] == '2024-09-30'
        assert row['period_end'] == '2024-10-06'
        assert row['period_progress_pct'] == 10.0

    def test_technical_approve_advances_approved_only(self, project, activity, approved_measurement, auth_client):
        _manual(auth_client, project, activity, 30, '2024-10-01')
        url = f'/api/v1/projects/{project.id}/progress/{activity.id}/technical-approve/'
        response = auth_client.post(url, {}, format='json')
        assert response.status_code == 200
        assert response.data['approved_progress_pct'] == 30.0
        _manual(auth_client, project, activity, 50, '2024-10-02')
        row = _row(auth_client, project, activity, as_of='2024-10-05')
        assert row['cumulative_progress_pct'] == 50.0
        assert row['approved_progress_pct'] == 30.0
        progress = ActivityProgress.objects.get(activity=activity, report_date='2024-10-01')
        assert progress.technical_approved_by_id is not None

    def test_photo_alone_is_not_technical_approval(self, project, activity, approved_measurement, auth_client):
        _manual(auth_client, project, activity, 30, '2024-10-01', evidence_refs={'photos': ['p1']})
        url = f'/api/v1/projects/{project.id}/progress/{activity.id}/technical-approve/'
        response = auth_client.post(url, {'basis': 'photo'}, format='json')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'photo_not_technical_approval'
        row = ActivityProgress.objects.get(activity=activity, report_date='2024-10-01')
        assert row.approved_progress is None
        assert row.evidence_refs == {'photos': ['p1']}

    def test_technical_approve_without_progress_404_like_400(self, project, activity, approved_measurement, auth_client):
        url = f'/api/v1/projects/{project.id}/progress/{activity.id}/technical-approve/'
        response = auth_client.post(url, {}, format='json')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'progress_not_found'

    def test_breakdown_without_measurement(self, project, activity, auth_client):
        row = _row(auth_client, project, activity, as_of='2024-10-05')
        assert row['measurement_method'] is None
        assert row['measurement_status'] == 'not_defined'
        assert row['measurement_version_id'] is None

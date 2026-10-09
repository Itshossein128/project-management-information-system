import pytest

from schedule.models import ActivityProgress
from schedule.services.measurement_service import (
    ProgressValidationError,
    approve_quantity_change,
    create_quantity_change,
    validate_progress_pct,
)


def _manual(client, project, activity, pct, date='2024-10-01', **extra):
    return client.post(
        f'/api/v1/projects/{project.id}/progress/manual/',
        {'activity_id': str(activity.id), 'report_date': date, 'actual_progress': pct, **extra},
        format='json',
    )


@pytest.mark.django_db
class TestProgressValidation:
    def test_progress_without_measurement_400(self, project, activity, auth_client):
        response = _manual(auth_client, project, activity, 40)
        assert response.status_code == 400
        assert response.data['error']['code'] == 'measurement_not_approved'
        assert not ActivityProgress.objects.filter(activity=activity).exists()

    def test_draft_measurement_without_approval_400(self, project, activity, auth_client):
        auth_client.get(f'/api/v1/projects/{project.id}/activities/{activity.id}/measurement/')
        response = _manual(auth_client, project, activity, 40)
        assert response.status_code == 400
        assert response.data['error']['code'] == 'measurement_not_approved'

    def test_over_100_rejected_not_clamped(self, project, activity, approved_measurement, auth_client):
        response = _manual(auth_client, project, activity, 150)
        assert response.status_code == 400
        assert response.data['error']['code'] == 'progress_exceeds_100'
        assert not ActivityProgress.objects.filter(activity=activity).exists()

    def test_exactly_100_accepted(self, project, activity, approved_measurement, auth_client):
        response = _manual(auth_client, project, activity, 100)
        assert response.status_code == 201
        assert response.data['actual_progress'] == pytest.approx(1.0)

    def test_over_100_allowed_with_approved_quantity_change(
        self, project, activity, approved_measurement, auth_client,
    ):
        base = f'/api/v1/projects/{project.id}/activities/{activity.id}/quantity-changes/'
        created = auth_client.post(base, {'new_total': 150, 'reason': 'Scope increase'}, format='json')
        assert created.status_code == 201
        assert created.data['previous_total'] == 100.0
        assert created.data['status'] == 'draft'
        # Still rejected while the change is only a draft.
        assert _manual(auth_client, project, activity, 120).status_code == 400

        approved = auth_client.post(f'{base}{created.data["id"]}/approve/', {}, format='json')
        assert approved.status_code == 200
        assert approved.data['status'] == 'approved'

        ok = _manual(auth_client, project, activity, 120)
        assert ok.status_code == 201
        # 120% of 100 = 120 units = 80% of the new 150 total.
        assert ok.data['actual_progress'] == pytest.approx(0.8)
        # Still rejected beyond the new total.
        assert _manual(auth_client, project, activity, 200, date='2024-10-02').status_code == 400

        listing = auth_client.get(base)
        assert listing.status_code == 200
        assert len(listing.data) == 1

    def test_quantity_change_requires_reason_and_increase(self, project, activity, approved_measurement, user):
        with pytest.raises(ProgressValidationError) as exc:
            create_quantity_change(activity, {'new_total': 150}, user)
        assert exc.value.code == 'quantity_change_reason_required'
        with pytest.raises(ProgressValidationError):
            create_quantity_change(activity, {'new_total': 50, 'reason': 'x'}, user)

    def test_validate_progress_pct_service(self, activity, approved_measurement, user):
        assert validate_progress_pct(activity, 0.5) == pytest.approx(0.5)
        with pytest.raises(ProgressValidationError) as exc:
            validate_progress_pct(activity, 1.2)
        assert exc.value.code == 'progress_exceeds_100'
        change = create_quantity_change(activity, {'new_total': 200, 'reason': 'r'}, user)
        approve_quantity_change(change, user)
        assert validate_progress_pct(activity, 1.5) == pytest.approx(0.75)

    def test_incomplete_basis_blocks_progress(self, project, activity, approved_measurement, auth_client):
        # Corrupt the approved snapshot to simulate an incomplete basis.
        version = approved_measurement.current_version
        version.basis_snapshot = {**version.basis_snapshot, 'total_quantity': None}
        version.save(update_fields=['basis_snapshot'])
        response = _manual(auth_client, project, activity, 10)
        assert response.status_code == 400
        assert response.data['error']['code'] == 'incomplete_measurement_basis'

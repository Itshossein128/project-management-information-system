import pytest
from rest_framework.test import APIClient

from master_data.models import ProjectMember, ProjectMemberRole

from schedule.models import (
    ActivityMeasurementDefinition,
    ActivityMeasurementVersion,
    ActivityProgress,
    MeasurementStatus,
)


def _base(project, activity):
    return f'/api/v1/projects/{project.id}/activities/{activity.id}/measurement/'


@pytest.mark.django_db
class TestMeasurementMethods:
    def test_get_creates_draft_defaulting_to_quantity(self, project, activity, auth_client):
        response = auth_client.get(_base(project, activity))
        assert response.status_code == 200
        assert response.data['method'] == 'quantity'
        assert response.data['status'] == 'draft'
        assert response.data['current_version_id'] is None

    def test_approve_quantity_method(self, project, activity, unit, auth_client):
        base = _base(project, activity)
        patch = auth_client.patch(
            base, {'method': 'quantity', 'total_quantity': 1000, 'unit_id': str(unit.id)}, format='json',
        )
        assert patch.status_code == 200
        response = auth_client.post(f'{base}approve/', {}, format='json')
        assert response.status_code == 200
        assert response.data['status'] == 'approved'
        assert response.data['current_version_id']
        assert [v['version_number'] for v in response.data['versions']] == [1]
        version = ActivityMeasurementVersion.objects.get(pk=response.data['current_version_id'])
        assert version.basis_snapshot['total_quantity'] == '1000.0000'
        assert version.basis_snapshot['unit_id'] == str(unit.id)

    def test_approve_quantity_without_unit_rejected(self, project, activity, auth_client):
        base = _base(project, activity)
        auth_client.patch(base, {'method': 'quantity', 'total_quantity': 10, 'unit_id': None}, format='json')
        response = auth_client.post(f'{base}approve/', {}, format='json')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'incomplete_measurement_basis'

    def test_incomplete_milestones_rejected(self, project, activity, auth_client):
        base = _base(project, activity)
        auth_client.patch(
            base,
            {
                'method': 'weighted_milestones',
                'milestones': [{'name': 'Formwork', 'weight': 0.3}, {'name': 'Pour', 'weight': 0.4}],
            },
            format='json',
        )
        response = auth_client.post(f'{base}approve/', {}, format='json')
        assert response.status_code == 400
        assert response.data['error']['code'] == 'incomplete_measurement_basis'

    def test_weighted_milestones_approve_within_tolerance(self, project, activity, auth_client):
        base = _base(project, activity)
        auth_client.patch(
            base,
            {
                'method': 'weighted_milestones',
                'milestones': [
                    {'name': 'Formwork', 'weight': 0.3},
                    {'name': 'Pour', 'weight': 0.5},
                    {'name': 'Cure', 'weight': 0.205},
                ],
            },
            format='json',
        )
        response = auth_client.post(f'{base}approve/', {}, format='json')
        assert response.status_code == 200

    def test_evidence_percent_requires_rules(self, project, activity, auth_client):
        base = _base(project, activity)
        auth_client.patch(base, {'method': 'evidence_percent'}, format='json')
        assert auth_client.post(f'{base}approve/', {}, format='json').status_code == 400
        auth_client.patch(base, {'evidence_rules': 'Engineer sign-off'}, format='json')
        assert auth_client.post(f'{base}approve/', {}, format='json').status_code == 200

    def test_approve_twice_conflicts(self, project, activity, approved_measurement, auth_client):
        response = auth_client.post(f'{_base(project, activity)}approve/', {}, format='json')
        assert response.status_code == 409
        assert response.data['error']['code'] == 'measurement_already_approved'

    def test_patch_on_approved_requires_change_endpoint(self, project, activity, approved_measurement, auth_client):
        response = auth_client.patch(_base(project, activity), {'total_quantity': 5}, format='json')
        assert response.status_code == 400

    def test_method_change_requires_reason(self, project, activity, approved_measurement, auth_client):
        response = auth_client.post(
            f'{_base(project, activity)}change/',
            {'method': 'evidence_percent', 'evidence_rules': 'rules'},
            format='json',
        )
        assert response.status_code == 400
        assert response.data['error']['code'] == 'method_change_reason_required'

    def test_method_change_versioning_keeps_old_progress_version(
        self, project, activity, approved_measurement, auth_client, user,
    ):
        v1_id = approved_measurement.current_version_id
        progress_url = f'/api/v1/projects/{project.id}/progress/manual/'
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        first = auth_client.post(
            progress_url,
            {'activity_id': str(activity.id), 'report_date': '2024-10-01', 'actual_progress': 30},
            format='json',
        )
        assert first.status_code == 201

        base = _base(project, activity)
        change = auth_client.post(
            f'{base}change/',
            {'method': 'evidence_percent', 'evidence_rules': 'Engineer sign-off', 'reason': 'Switch to evidence'},
            format='json',
        )
        assert change.status_code == 201
        assert change.data['status'] == MeasurementStatus.DRAFT
        # Old approved version remains usable for writes until re-approval.
        assert change.data['current_version_id'] == str(v1_id)
        during = auth_client.post(
            progress_url,
            {'activity_id': str(activity.id), 'report_date': '2024-10-02', 'actual_progress': 40},
            format='json',
        )
        assert during.status_code == 201
        assert during.data['measurement_version_id'] == str(v1_id)

        approve = auth_client.post(f'{base}approve/', {}, format='json')
        assert approve.status_code == 200
        v2_id = approve.data['current_version_id']
        assert v2_id != str(v1_id)
        assert [v['version_number'] for v in approve.data['versions']] == [1, 2]
        assert approve.data['versions'][1]['change_reason'] == 'Switch to evidence'

        after = auth_client.post(
            progress_url,
            {'activity_id': str(activity.id), 'report_date': '2024-10-03', 'actual_progress': 50},
            format='json',
        )
        assert after.data['measurement_version_id'] == v2_id
        # History is never rewritten.
        old = ActivityProgress.objects.get(activity=activity, report_date='2024-10-01')
        assert old.measurement_version_id == v1_id
        assert ActivityMeasurementDefinition.objects.get(activity=activity).versions.count() == 2

    def test_viewer_cannot_edit_measurement(self, project, activity, other_user, viewer_role):
        member = ProjectMember.objects.create(project=project, user=other_user, status='active')
        ProjectMemberRole.objects.create(member=member, role=viewer_role)
        client = APIClient()
        client.force_authenticate(user=other_user)
        assert client.get(_base(project, activity)).status_code == 200
        assert client.patch(_base(project, activity), {'total_quantity': 5}, format='json').status_code == 403

import pytest
from rest_framework import status

from field_reports.models import DailyReport, DailyReportActivity, ReportStatus


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportGapsStatusUnset:
    def test_approved_response_is_locked(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-01',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.get(f'{reports_url}{report.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_locked'] is True
        assert response.data['status'] == 'approved'
        assert response.data['report_date']
        assert response.data['created_at']
        assert 'approved_at' in response.data

    def test_submitted_denies_child_writes(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-02',
            status=ReportStatus.SUBMITTED,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/activities/',
            {
                'activity_description': 'x',
                'shift': 'shift_1',
                'quantity': '1',
                'quantity_measured': True,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejected_remains_editable(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-03',
            status=ReportStatus.REJECTED,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.patch(
            f'{reports_url}{report.id}/',
            {'general_notes': 'fixed', 'work_front': 'W1'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['work_front'] == 'W1'

    def test_material_quantity_not_coerced_from_null(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-11-04', created_by=user, updated_by=user,
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/materials/',
            {
                'material_description': 'Steel',
                'quantity': None,
                'unit': 'kg',
                'transaction_type': 'issue',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activity_measured_false_clears_quantity(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-11-05', created_by=user, updated_by=user,
        )
        row = DailyReportActivity.objects.create(
            report=report,
            activity_description='x',
            shift='shift_1',
            quantity=9,
            quantity_measured=True,
        )
        response = auth_client.patch(
            f'{reports_url}{report.id}/activities/{row.id}/',
            {'quantity_measured': False},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] is None
        assert response.data['quantity_measured'] is False

    def test_submit_soft_warns_when_work_front_empty(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-06',
            work_front='',
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_description='submit row',
            shift='shift_1',
            quantity=1,
            quantity_measured=True,
        )
        response = auth_client.post(f'{reports_url}{report.id}/submit/', format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == ReportStatus.SUBMITTED
        warnings = response.data.get('submit_warnings') or []
        assert any('جبهه' in w or 'work' in w.lower() for w in warnings)

    def test_submit_no_work_front_warning_when_set(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-07',
            work_front='North',
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_description='submit row',
            shift='shift_1',
            quantity=1,
            quantity_measured=True,
        )
        response = auth_client.post(f'{reports_url}{report.id}/submit/', format='json')
        assert response.status_code == status.HTTP_200_OK
        assert not response.data.get('submit_warnings')

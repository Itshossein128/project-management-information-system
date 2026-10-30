import pytest
from rest_framework import status

from field_reports.models import DailyReport, DailyReportActivity, ReportStatus


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportGapsHeader:
    def test_model_has_gap_fields(self, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-01',
            work_front='North axis',
            location_notes='Gate 2',
            created_by=user,
            updated_by=user,
        )
        report.refresh_from_db()
        assert report.work_front == 'North axis'
        assert report.location_notes == 'Gate 2'
        assert report.lineage_id == report.id
        assert report.version_number == 1
        assert report.is_current is True
        assert report.supersedes_id is None

    def test_create_with_work_front(self, auth_client, reports_url, project):
        by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
        ensured = auth_client.post(by_date, {'date': '1403/05/11'}, format='json')
        assert ensured.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        report_id = ensured.data['report_id']
        response = auth_client.patch(
            f'{reports_url}{report_id}/',
            {
                'work_front': 'جبهه شمالی',
                'location_notes': 'بلوک A',
                'weather_condition': 'clear',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['work_front'] == 'جبهه شمالی'
        assert response.data['location_notes'] == 'بلوک A'
        assert response.data['is_current'] is True
        assert response.data['version_number'] == 1
        assert response.data['lineage_id']

    def test_activity_responsible_and_unset_quantity(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-08-02', created_by=user, updated_by=user,
        )
        url = f'{reports_url}{report.id}/activities/'
        measured = auth_client.post(
            url,
            {
                'activity_description': 'Formwork',
                'shift': 'shift_1',
                'quantity': '10.5',
                'quantity_measured': True,
                'unit': 'm2',
                'responsible_name': 'Site lead',
            },
            format='json',
        )
        assert measured.status_code == status.HTTP_201_CREATED
        assert measured.data['responsible_name'] == 'Site lead'
        assert measured.data['quantity'] is not None

        unset = auth_client.post(
            url,
            {
                'activity_description': 'Pending measure',
                'shift': 'shift_1',
                'quantity': None,
                'quantity_measured': False,
                'unit': 'm2',
                'responsible_name': 'Lead 2',
            },
            format='json',
        )
        assert unset.status_code == status.HTTP_201_CREATED
        assert unset.data['quantity'] is None
        assert unset.data['quantity_measured'] is False

        bad = auth_client.post(
            url,
            {
                'activity_description': 'Bad',
                'shift': 'shift_1',
                'quantity': None,
                'quantity_measured': True,
                'unit': 'm2',
            },
            format='json',
        )
        # A measured-but-unset value may be saved in a draft, but cannot be submitted.
        assert bad.status_code == status.HTTP_201_CREATED
        assert bad.data['quantity_measured'] is True
        assert bad.data['quantity'] is None
        submit = auth_client.post(f'{reports_url}{report.id}/submit/', {}, format='json')
        assert submit.status_code == status.HTTP_400_BAD_REQUEST
        assert submit.data['error']['code'] == 'quantity_unset_invalid'
        report.refresh_from_db()
        assert report.status == ReportStatus.DRAFT

    def test_submit_rejects_measured_null_quantity(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-08-03', created_by=user, updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_description='x',
            shift='shift_1',
            quantity=None,
            quantity_measured=True,
        )
        response = auth_client.post(f'{reports_url}{report.id}/submit/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error']['code'] == 'quantity_unset_invalid'

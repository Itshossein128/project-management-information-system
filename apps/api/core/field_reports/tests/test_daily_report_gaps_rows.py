import pytest
from rest_framework import status

from field_reports.models import DailyReport, MaterialTransactionType


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportGapsRows:
    def test_material_return_and_location(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-01', created_by=user, updated_by=user,
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/materials/',
            {
                'material_description': 'Cement',
                'quantity': '3',
                'unit': 'bag',
                'transaction_type': MaterialTransactionType.RETURN,
                'consumption_location': 'Warehouse A',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['transaction_type'] == 'return'
        assert response.data['consumption_location'] == 'Warehouse A'

    def test_labor_absence_null_vs_zero(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-02', created_by=user, updated_by=user,
        )
        url = f'{reports_url}{report.id}/labor/'
        with_absence = auth_client.post(
            url,
            {
                'labor_category': 'direct',
                'job_title': 'بنا',
                'shift_1_count': 2,
                'absence_count': 1,
            },
            format='json',
        )
        assert with_absence.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        # batch returns list
        row = with_absence.data[0] if isinstance(with_absence.data, list) else with_absence.data
        assert row['absence_count'] == 1

        unset = auth_client.post(
            url,
            {
                'labor_category': 'direct',
                'job_title': 'بتن‌ریز',
                'shift_1_count': 1,
                'absence_count': None,
            },
            format='json',
        )
        assert unset.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        row2 = unset.data[0] if isinstance(unset.data, list) else unset.data
        assert row2['absence_count'] is None

    def test_site_event_owner_due(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-03', created_by=user, updated_by=user,
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/incidents/',
            {
                'incident_type': 'barrier',
                'description': 'Access blocked',
                'corrective_action': 'Reroute',
                'follow_up_owner_name': 'HSE lead',
                'due_date': '1403/07/13',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['incident_type'] == 'barrier'
        assert response.data['follow_up_owner_name'] == 'HSE lead'
        assert response.data['due_date']

    def test_materials_reconciliation_endpoint(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-04', created_by=user, updated_by=user,
        )
        auth_client.post(
            f'{reports_url}{report.id}/materials/',
            {
                'material_description': 'Sand',
                'quantity': '2',
                'unit': 'm3',
                'transaction_type': 'issue',
            },
            format='json',
        )
        response = auth_client.get(f'{reports_url}{report.id}/materials/reconciliation/')
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data
        assert response.data['items'][0]['status'] == 'insufficient_data'

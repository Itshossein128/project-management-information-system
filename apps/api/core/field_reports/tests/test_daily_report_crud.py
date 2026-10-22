import pytest
from rest_framework import status

from field_reports.models import DailyReport, ReportStatus


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportCrud:
    def test_unauthenticated_cannot_list(self, api_client, reports_url):
        assert api_client.get(reports_url).status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_rejected_use_by_date(self, auth_client, reports_url, project):
        response = auth_client.post(
            reports_url,
            {'report_date': '1403/03/12', 'weather_condition': 'sunny', 'site_status': 'active'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
        ensured = auth_client.post(by_date, {'date': '1403/03/12'}, format='json')
        assert ensured.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        assert ensured.data['report_date'] == '1403/03/12'
        assert ensured.data['activities'] == []
        assert ensured.data['is_auto_summary'] is True

    def test_by_date_idempotent_for_same_day(self, auth_client, project, user):
        DailyReport.objects.create(
            project=project, report_date='2024-06-01', created_by=user, updated_by=user,
            is_auto_summary=True,
        )
        by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
        response = auth_client.get(by_date, {'date': '1403/03/12'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['shift'] == 'full'

    def test_viewer_cannot_blank_create(self, api_client, other_user, viewer_member, reports_url):
        api_client.force_authenticate(user=other_user)
        viewer_member.member_roles.all().delete()
        response = api_client.post(
            reports_url, {'report_date': '1403/03/12'}, format='json',
        )
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_retrieve_includes_child_arrays(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-06-02', created_by=user, updated_by=user,
        )
        response = auth_client.get(f'{reports_url}{report.id}/')
        assert response.status_code == status.HTTP_200_OK
        for key in ('activities', 'labor', 'equipment', 'materials', 'concrete_logs',
                    'labor_camp', 'incidents'):
            assert key in response.data

    def test_cannot_edit_approved(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-06-03', status=ReportStatus.APPROVED,
            created_by=user, updated_by=user,
        )
        response = auth_client.patch(
            f'{reports_url}{report.id}/', {'general_notes': 'x'}, format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_soft_delete_only_draft(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-06-04', created_by=user, updated_by=user,
        )
        response = auth_client.delete(f'{reports_url}{report.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        report.refresh_from_db()
        assert report.is_deleted is True


@pytest.mark.django_db
class TestLaborBatchUpsert:
    def test_batch_upsert(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-07-01', created_by=user, updated_by=user,
        )
        url = f'{reports_url}{report.id}/labor/'
        payload = [
            {'labor_category': 'direct', 'job_title': 'بنا', 'shift_1_count': 2},
            {'labor_category': 'direct', 'job_title': 'بتن‌ریز', 'shift_1_count': 1},
        ]
        response = auth_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        # Upsert the same title: should update, not duplicate.
        response2 = auth_client.post(
            url, [{'labor_category': 'direct', 'job_title': 'بنا', 'shift_1_count': 5}],
            format='json',
        )
        assert response2.status_code == status.HTTP_200_OK
        assert report.labor_entries.filter(is_deleted=False, job_title='بنا').count() == 1
        assert report.labor_entries.get(job_title='بنا').shift_1_count == 5


@pytest.mark.django_db
class TestPdfExport:
    def test_pdf_download(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-11-01', weather_condition='clear',
            created_by=user, updated_by=user, prepared_by=user,
        )
        response = auth_client.get(f'{reports_url}{report.id}/pdf/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert response.content[:4] == b'%PDF'


@pytest.mark.django_db
class TestJobTitles:
    def test_list_job_titles(self, auth_client, project):
        url = f'/api/v1/projects/{project.id}/manpower/job-titles/'
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 65
        titles = {row['title'] for row in response.data}
        assert 'مدیرشعبه' in titles
        assert 'کارگر ساده' in titles
        assert 'اپراتور تاور' in titles

    def test_unauthenticated_cannot_list_job_titles(self, api_client, project):
        url = f'/api/v1/projects/{project.id}/manpower/job-titles/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

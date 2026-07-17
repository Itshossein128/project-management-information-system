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

    def test_create_with_jalali_date(self, auth_client, reports_url):
        response = auth_client.post(
            reports_url,
            {'report_date': '1403/03/12', 'weather_condition': 'sunny', 'site_status': 'active'},
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['report_date'] == '1403/03/12'
        assert response.data['activities'] == []
        assert response.data['status'] == 'draft'

    def test_duplicate_date_returns_409(self, auth_client, reports_url, project, user):
        DailyReport.objects.create(
            project=project, report_date='2024-06-01', created_by=user, updated_by=user,
        )
        response = auth_client.post(
            reports_url,
            {'report_date': '1403/03/12', 'site_status': 'active'},
            format='json',
        )
        # 1403/03/12 == 2024-06-01; default shift is full for both
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_same_date_different_shift_allowed(self, auth_client, reports_url, project, user):
        DailyReport.objects.create(
            project=project,
            report_date='2024-06-01',
            shift='day',
            created_by=user,
            updated_by=user,
        )
        response = auth_client.post(
            reports_url,
            {
                'report_date': '1403/03/12',
                'shift': 'night',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['shift'] == 'night'
    def test_viewer_cannot_create(self, api_client, other_user, viewer_member, reports_url):
        # site_supervisor has edit_reports; use plain viewer member instead
        api_client.force_authenticate(user=other_user)
        # viewer_member grants edit; downgrade by removing roles
        viewer_member.member_roles.all().delete()
        response = api_client.post(
            reports_url, {'report_date': '1403/03/12'}, format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

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
            project=project, report_date='2024-11-01', weather_condition='sunny',
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

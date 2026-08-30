import pytest
from rest_framework import status

from field_reports.models import DailyReportLabor


@pytest.fixture
def manpower_url(project):
    return f'/api/v1/projects/{project.id}/manpower/'


@pytest.mark.django_db
class TestStandaloneManpower:
    def test_unauthenticated_cannot_access(self, api_client, manpower_url):
        assert api_client.get(manpower_url).status_code == status.HTTP_401_UNAUTHORIZED
        assert api_client.post(manpower_url, [], format='json').status_code == status.HTTP_401_UNAUTHORIZED

    def test_viewer_cannot_create(self, api_client, other_user, viewer_member, manpower_url):
        api_client.force_authenticate(user=other_user)
        viewer_member.member_roles.all().delete()
        response = api_client.post(
            manpower_url,
            [
                {
                    'report_date': '1403/03/12',
                    'labor_category': 'direct',
                    'job_title': 'بنا',
                    'shift_1_count': 2,
                    'work_hours': 8.0,
                    'overtime_hours': 2.0,
                }
            ],
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_batch_upsert_standalone_manpower_with_hours_and_custom_title(
        self, auth_client, manpower_url, project
    ):
        payload = [
            {
                'report_date': '1403/03/12',
                'labor_category': 'direct',
                'job_title': 'بنا',
                'shift_1_count': 3,
                'shift_2_count': 1,
                'shift_3_count': 0,
                'work_hours': 8.0,
                'overtime_hours': 2.5,
            },
            {
                'report_date': '1403/03/12',
                'labor_category': 'direct',
                'job_title': 'عنوان سفارشی تست',
                'custom_title': 'عنوان سفارشی تست',
                'shift_1_count': 2,
                'shift_2_count': 0,
                'shift_3_count': 0,
                'work_hours': 7.5,
                'overtime_hours': 1.0,
            },
        ]
        response = auth_client.post(manpower_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.data.get('results', response.data)
        assert len(data) == 2

        # Verify DB records
        row1 = DailyReportLabor.objects.get(
            project=project, job_title='بنا', report__isnull=True, is_deleted=False
        )
        assert row1.shift_1_count == 3
        assert float(row1.work_hours) == 8.0
        assert float(row1.overtime_hours) == 2.5

        row2 = DailyReportLabor.objects.get(
            project=project, job_title='عنوان سفارشی تست', report__isnull=True, is_deleted=False
        )
        assert row2.custom_title == 'عنوان سفارشی تست'
        assert float(row2.work_hours) == 7.5
        assert float(row2.overtime_hours) == 1.0

    def test_update_existing_standalone_manpower_hours(self, auth_client, manpower_url, project):
        payload = [
            {
                'report_date': '1403/03/12',
                'labor_category': 'indirect',
                'job_title': 'مدیر پروژه',
                'shift_1_count': 1,
                'work_hours': 8.0,
                'overtime_hours': 0.0,
            }
        ]
        res1 = auth_client.post(manpower_url, payload, format='json')
        assert res1.status_code == status.HTTP_201_CREATED

        # Update existing record
        payload_update = [
            {
                'report_date': '1403/03/12',
                'labor_category': 'indirect',
                'job_title': 'مدیر پروژه',
                'shift_1_count': 1,
                'work_hours': 8.0,
                'overtime_hours': 4.0,
            }
        ]
        res2 = auth_client.post(manpower_url, payload_update, format='json')
        assert res2.status_code == status.HTTP_201_CREATED

        # Assert only one record exists and overtime_hours updated
        qs = DailyReportLabor.objects.filter(
            project=project, job_title='مدیر پروژه', report__isnull=True, is_deleted=False
        )
        assert qs.count() == 1
        obj = qs.first()
        assert float(obj.overtime_hours) == 4.0

    def test_list_standalone_manpower_by_date(self, auth_client, manpower_url):
        payload = [
            {
                'report_date': '1403/03/12',
                'labor_category': 'direct',
                'job_title': 'آرماتوربند',
                'shift_1_count': 5,
                'work_hours': 8.0,
                'overtime_hours': 3.0,
            }
        ]
        auth_client.post(manpower_url, payload, format='json')

        response = auth_client.get(f'{manpower_url}?date=1403/03/12')
        assert response.status_code == status.HTTP_200_OK
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        assert len(data) == 1
        item = data[0]
        assert item['job_title'] == 'آرماتوربند'
        assert float(item['work_hours']) == 8.0
        assert float(item['overtime_hours']) == 3.0

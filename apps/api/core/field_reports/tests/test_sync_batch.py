import pytest
from rest_framework import status

from field_reports.models import DailyReport, ReportStatus


@pytest.fixture
def sync_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-batch/'


@pytest.mark.django_db
class TestSyncBatch:
    def test_create_new_report_with_children(self, auth_client, sync_url, project):
        payload = [
            {
                'local_id': 'local-1',
                'report_date': '2024-09-01',
                'site_status': 'active',
                'activities': [
                    {'activity_description': 'بتن‌ریزی', 'shift': 'shift_1', 'quantity': '10'},
                ],
                'labor': [
                    {'labor_category': 'direct', 'job_title': 'بنا', 'shift_1_count': 3},
                ],
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['summary']['created'] == 1
        result = response.data['results'][0]
        assert result['status'] == 'created'
        report = DailyReport.objects.get(id=result['server_id'])
        assert report.synced_from_offline is True
        assert report.activities.count() == 1
        assert report.labor_entries.count() == 1

    def test_approved_existing_is_conflict(self, auth_client, sync_url, project, user):
        DailyReport.objects.create(
            project=project, report_date='2024-09-02', status=ReportStatus.APPROVED,
            created_by=user, updated_by=user,
        )
        payload = [{'local_id': 'l2', 'report_date': '2024-09-02', 'site_status': 'active'}]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['conflicts'] == 1
        assert response.data['results'][0]['status'] == 'conflict'

    def test_draft_existing_merges_children(self, auth_client, sync_url, project, user):
        existing = DailyReport.objects.create(
            project=project, report_date='2024-09-03', status=ReportStatus.DRAFT,
            created_by=user, updated_by=user,
        )
        payload = [
            {
                'local_id': 'l3',
                'report_date': '2024-09-03',
                'activities': [
                    {'activity_description': 'کار', 'shift': 'shift_2'},
                ],
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['merged'] == 1
        existing.refresh_from_db()
        assert existing.activities.count() == 1

    def test_body_must_be_list(self, auth_client, sync_url):
        response = auth_client.post(sync_url, {'report_date': '2024-09-04'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_local_id_in_batch_skipped(self, auth_client, sync_url):
        payload = [
            {'local_id': 'dup-1', 'report_date': '2024-09-05', 'site_status': 'active'},
            {'local_id': 'dup-1', 'report_date': '2024-09-06', 'site_status': 'active'},
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['skipped'] == 1
        assert response.data['summary']['created'] == 1

    def test_submitted_existing_is_conflict(self, auth_client, sync_url, project, user):
        DailyReport.objects.create(
            project=project, report_date='2024-09-07', status=ReportStatus.SUBMITTED,
            created_by=user, updated_by=user,
        )
        payload = [{'local_id': 'l4', 'report_date': '2024-09-07', 'activities': []}]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['conflicts'] == 1

    def test_invalid_header_returns_error_not_abort(self, auth_client, sync_url):
        payload = [
            {
                'local_id': 'bad-header',
                'report_date': '2024-09-08',
                'temp_min': 40,
                'temp_max': 10,
            },
            {'local_id': 'good-header', 'report_date': '2024-09-09', 'site_status': 'active'},
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['summary']['errors'] == 1
        assert response.data['summary']['created'] == 1

    def test_invalid_child_row_reported(self, auth_client, sync_url):
        payload = [
            {
                'local_id': 'child-err',
                'report_date': '2024-09-10',
                'site_status': 'active',
                'activities': [{'shift': 'shift_1'}],
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['created'] == 1
        child_errors = response.data['results'][0]['child_errors']
        assert child_errors
        assert child_errors[0]['section'] == 'activities'

    def test_resync_same_payload_no_duplicate_children(self, auth_client, sync_url, project, user):
        existing = DailyReport.objects.create(
            project=project,
            report_date='2024-09-11',
            status=ReportStatus.DRAFT,
            local_id='resync-1',
            created_by=user,
            updated_by=user,
        )
        payload = [
            {
                'local_id': 'resync-1',
                'report_date': '2024-09-11',
                'activities': [
                    {'activity_description': 'کار اول', 'shift': 'shift_1'},
                ],
            },
        ]
        first = auth_client.post(sync_url, payload, format='json')
        assert first.data['summary']['merged'] == 1
        existing.refresh_from_db()
        assert existing.activities.count() == 1

        second = auth_client.post(sync_url, payload, format='json')
        assert second.data['summary']['merged'] == 1
        existing.refresh_from_db()
        assert existing.activities.count() == 1

    def test_under_review_existing_is_conflict(self, auth_client, sync_url, project, user):
        DailyReport.objects.create(
            project=project,
            report_date='2024-09-12',
            status=ReportStatus.UNDER_REVIEW,
            created_by=user,
            updated_by=user,
        )
        payload = [{'local_id': 'l5', 'report_date': '2024-09-12', 'activities': []}]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['conflicts'] == 1
        assert response.data['results'][0]['status'] == 'conflict'

    def test_invalid_date_returns_error(self, auth_client, sync_url):
        payload = [{'local_id': 'bad-date', 'report_date': 'not-a-date', 'site_status': 'active'}]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['errors'] == 1
        assert response.data['results'][0]['status'] == 'error'

    def test_multi_shift_same_date_creates_independently(self, auth_client, sync_url, project, user):
        DailyReport.objects.create(
            project=project,
            report_date='2024-09-13',
            shift='day',
            status=ReportStatus.DRAFT,
            created_by=user,
            updated_by=user,
        )
        payload = [
            {
                'local_id': 'night-1',
                'report_date': '2024-09-13',
                'shift': 'night',
                'site_status': 'active',
                'activities': [
                    {'activity_description': 'کار شب', 'shift': 'shift_2'},
                ],
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['summary']['created'] == 1
        assert response.data['results'][0]['status'] == 'created'
        assert DailyReport.objects.filter(
            project=project, report_date='2024-09-13', is_deleted=False,
        ).count() == 2

    def test_draft_merge_applies_header_fields(self, auth_client, sync_url, project, user):
        existing = DailyReport.objects.create(
            project=project,
            report_date='2024-09-14',
            shift='full',
            status=ReportStatus.DRAFT,
            weather_condition='sunny',
            site_status='active',
            general_notes='قدیمی',
            created_by=user,
            updated_by=user,
        )
        payload = [
            {
                'local_id': 'hdr-merge',
                'report_date': '2024-09-14',
                'shift': 'full',
                'weather_condition': 'rainy',
                'site_status': 'inactive',
                'general_notes': 'به‌روز از آفلاین',
                'temp_min': 8,
                'temp_max': 18,
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['merged'] == 1
        existing.refresh_from_db()
        assert existing.weather_condition == 'rainy'
        assert existing.site_status == 'inactive'
        assert existing.general_notes == 'به‌روز از آفلاین'
        assert float(existing.temp_min) == 8.0
        assert float(existing.temp_max) == 18.0
        assert existing.synced_from_offline is True

    def test_conflict_includes_server_payload_and_fields(self, auth_client, sync_url, project, user):
        DailyReport.objects.create(
            project=project,
            report_date='2024-09-15',
            shift='full',
            status=ReportStatus.APPROVED,
            weather_condition='sunny',
            site_status='active',
            general_notes='سرور',
            created_by=user,
            updated_by=user,
        )
        payload = [
            {
                'local_id': 'conflict-snap',
                'report_date': '2024-09-15',
                'shift': 'full',
                'weather_condition': 'cloudy',
                'site_status': 'inactive',
                'general_notes': 'کلاینت',
            },
        ]
        response = auth_client.post(sync_url, payload, format='json')
        assert response.data['summary']['conflicts'] == 1
        result = response.data['results'][0]
        assert result['status'] == 'conflict'
        assert result['server_payload'] is not None
        assert result['server_payload']['weather_condition'] == 'sunny'
        assert result['server_payload']['general_notes'] == 'سرور'
        assert 'weather_condition' in result['conflict_fields']
        assert 'site_status' in result['conflict_fields']
        assert 'general_notes' in result['conflict_fields']

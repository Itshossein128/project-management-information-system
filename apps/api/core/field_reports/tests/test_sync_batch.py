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

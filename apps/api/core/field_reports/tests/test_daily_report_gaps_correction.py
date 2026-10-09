import pytest
from rest_framework import status

from field_reports.models import (
    CorrectionRequestStatus,
    DailyReport,
    DailyReportActivity,
    DailyReportCorrectionRequest,
    ReportStatus,
)
from field_reports.services import sync_batch


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportGapsCorrection:
    def test_unique_current_constraint_allows_historical(self, project, user):
        a = DailyReport.objects.create(
            project=project,
            report_date='2024-09-01',
            shift='day',
            status=ReportStatus.APPROVED,
            is_current=False,
            created_by=user,
            updated_by=user,
        )
        b = DailyReport.objects.create(
            project=project,
            report_date='2024-09-01',
            shift='day',
            status=ReportStatus.DRAFT,
            is_current=True,
            lineage_id=a.lineage_id or a.id,
            version_number=2,
            supersedes=a,
            created_by=user,
            updated_by=user,
        )
        assert b.is_current is True
        assert DailyReport.objects.filter(
            project=project, report_date='2024-09-01', shift='day', is_deleted=False,
        ).count() == 2

    def test_correction_request_model_fields(self, project, user):
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-02',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        corr = DailyReportCorrectionRequest.objects.create(
            project=project,
            source_report=source,
            reason='Need to fix measured quantity on wall',
            status=CorrectionRequestStatus.SUBMITTED,
            created_by=user,
            updated_by=user,
        )
        assert corr.reason.startswith('Need')
        assert corr.result_report_id is None

    def test_cannot_patch_approved(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-09-03',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.patch(
            f'{reports_url}{report.id}/',
            {'general_notes': 'hack'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_open_correction_clones_and_versions(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-09-04',
            shift='full',
            work_front='East',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_description='Pour',
            shift='shift_1',
            quantity=5,
            quantity_measured=True,
            responsible_name='Ali',
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/correction-requests/',
            {'reason': 'Correct quantity for pour section'},
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        result_id = response.data['result_report_id']
        assert result_id
        report.refresh_from_db()
        assert report.is_current is False
        assert report.status == ReportStatus.APPROVED

        detail = auth_client.get(f'{reports_url}{result_id}/')
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data['status'] == 'draft'
        assert detail.data['is_current'] is True
        assert detail.data['version_number'] == 2
        assert detail.data['work_front'] == 'East'
        assert len(detail.data['activities']) == 1

        versions = auth_client.get(f'{reports_url}{report.id}/versions/')
        assert versions.status_code == status.HTTP_200_OK
        assert len(versions.data) == 2

        again = auth_client.post(
            f'{reports_url}{report.id}/correction-requests/',
            {'reason': 'Another open correction attempt xx'},
            format='json',
        )
        # source is no longer current — should fail report_not_locked
        assert again.status_code == status.HTTP_400_BAD_REQUEST

        # open second from... actually result is draft current; try opening from approved non-current fails.
        # Open from result won't work (not approved). Create second open via lineage by approving... skip.
        # Test correction_already_open: make result approved then open; then try again from that.
        # Simpler: open using current approved after we re-approve — covered below.

    def test_correction_already_open(self, auth_client, reports_url, project, user):
        from field_reports.services.correction_service import open_correction

        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-05',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        r1 = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'First correction reason long'},
            format='json',
        )
        assert r1.status_code == status.HTTP_201_CREATED
        result = DailyReport.objects.get(id=r1.data['result_report_id'])
        # Simulate race: restore source as current while open correction remains
        result.is_current = False
        result.save(update_fields=['is_current'])
        source.is_current = True
        source.save(update_fields=['is_current'])
        with pytest.raises(Exception) as exc:
            open_correction(
                source_report=source,
                user=user,
                reason='Second correction reason long',
            )
        assert 'correction_already_open' in str(exc.value).lower() or getattr(
            exc.value, 'default_code', '',
        ) == 'correction_already_open'

        corr_id = r1.data['id']
        cancel = auth_client.post(
            f'/api/v1/projects/{project.id}/correction-requests/{corr_id}/cancel/',
            {},
            format='json',
        )
        assert cancel.status_code == status.HTTP_200_OK
        source.refresh_from_db()
        assert source.is_current is True
        r2 = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'Second correction reason long'},
            format='json',
        )
        assert r2.status_code == status.HTTP_201_CREATED

    def test_short_reason_rejected(self, auth_client, reports_url, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-09-06',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.post(
            f'{reports_url}{report.id}/correction-requests/',
            {'reason': 'short'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sync_batch_conflicts_on_approved_current(self, project, user):
        DailyReport.objects.create(
            project=project,
            report_date='2024-09-07',
            shift='full',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        summary = sync_batch(
            project_id=project.id,
            user=user,
            reports=[{
                'report_date': '2024-09-07',
                'shift': 'full',
                'general_notes': 'offline edit',
                'activities': [],
            }],
        )
        assert summary['results'][0]['status'] == 'conflict'

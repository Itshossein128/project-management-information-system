import pytest
from rest_framework import status

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    ReportStatus,
)


@pytest.fixture
def base_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.fixture
def draft_report(db, project, user):
    return DailyReport.objects.create(
        project=project, report_date='2024-08-01', created_by=user, updated_by=user,
        prepared_by=user,
    )


def _add_activity(report):
    return DailyReportActivity.objects.create(
        report=report,
        activity_description='کار اجرایی',
        shift=ActivityRowShift.SHIFT_1,
        quantity_measured=False,
    )


@pytest.mark.django_db
class TestApprovalWorkflow:
    def test_submit_requires_activity(self, auth_client, base_url, draft_report):
        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_full_flow(self, auth_client, base_url, draft_report):
        _add_activity(draft_report)
        submit = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == 'submitted'

        review = auth_client.post(f'{base_url}{draft_report.id}/review/')
        assert review.status_code == status.HTTP_200_OK
        assert review.data['status'] == 'under_review'

        approve = auth_client.post(f'{base_url}{draft_report.id}/approve/')
        assert approve.status_code == status.HTTP_200_OK
        assert approve.data['status'] == 'approved'
        draft_report.refresh_from_db()
        assert draft_report.approved_by is not None

    def test_reject_requires_reason(self, auth_client, base_url, draft_report):
        _add_activity(draft_report)
        auth_client.post(f'{base_url}{draft_report.id}/submit/')
        short = auth_client.post(
            f'{base_url}{draft_report.id}/reject/', {'reason': 'no'}, format='json',
        )
        assert short.status_code == status.HTTP_400_BAD_REQUEST

        ok = auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'اطلاعات ناقص است و باید اصلاح شود'},
            format='json',
        )
        assert ok.status_code == status.HTTP_200_OK
        assert ok.data['status'] == 'rejected'

    def test_non_approver_cannot_approve(
        self, api_client, other_user, viewer_member, base_url, draft_report,
    ):
        # site_supervisor (viewer_member) has edit_reports but NOT approve_reports
        _add_activity(draft_report)
        draft_report.status = ReportStatus.SUBMITTED
        draft_report.save(update_fields=['status'])
        api_client.force_authenticate(user=other_user)
        response = api_client.post(f'{base_url}{draft_report.id}/approve/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_submit_blocks_measured_activity_without_quantity(
        self, auth_client, base_url, draft_report,
    ):
        DailyReportActivity.objects.create(
            report=draft_report,
            activity_description='بتن‌ریزی',
            shift=ActivityRowShift.SHIFT_1,
            quantity_measured=True,
            quantity=None,
        )
        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'submit_validation' in response.data

    def test_submit_blocks_incomplete_equipment_times(
        self, auth_client, base_url, draft_report,
    ):
        _add_activity(draft_report)
        draft_report.equipment_entries.create(
            equipment_name='جرثقیل',
            shift='day',
            status='active',
            ownership_type='owned',
            work_start='08:00',
        )
        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'submit_validation' in response.data

    def test_submit_blocks_invalid_labor_camp_totals(
        self, auth_client, base_url, draft_report,
    ):
        _add_activity(draft_report)
        draft_report.labor_camp_entries.create(
            connex_number='C-01',
            subcontractor_name='پیمانکار الف',
            total_residents=10,
            present_count=7,
            on_leave_count=1,
            capacity=12,
        )
        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'submit_validation' in response.data

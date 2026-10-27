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

    def test_resubmit_clears_rejection_reason(self, auth_client, base_url, draft_report):
        _add_activity(draft_report)
        auth_client.post(f'{base_url}{draft_report.id}/submit/')
        auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'اطلاعات ناقص است و باید اصلاح شود'},
            format='json',
        )
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason

        resubmit = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert resubmit.status_code == status.HTTP_200_OK
        assert resubmit.data['status'] == 'submitted'
        assert resubmit.data['rejection_reason'] == ''
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason == ''

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
        assert response.data['error']['code'] == 'quantity_unset_invalid'
        assert response.data['error']['message'] == 'مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود'

    def test_workflow_validation_codes_and_explicit_zero(self, auth_client, base_url, draft_report):
        DailyReportActivity.objects.create(
            report=draft_report,
            activity_description='صفر معتبر',
            shift=ActivityRowShift.SHIFT_1,
            quantity_measured=True,
            quantity=0,
        )
        assert auth_client.post(f'{base_url}{draft_report.id}/submit/').status_code == status.HTTP_200_OK

        submitted = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert submitted.status_code == status.HTTP_400_BAD_REQUEST
        assert submitted.data['error']['code'] == 'report_not_in_submittable_state'

        missing = auth_client.post(f'{base_url}{draft_report.id}/reject/', {'reason': '  '}, format='json')
        assert missing.status_code == status.HTTP_400_BAD_REQUEST
        assert missing.data['error']['code'] == 'rejection_reason_required'

        short = auth_client.post(f'{base_url}{draft_report.id}/reject/', {'reason': ' کوتاه '}, format='json')
        assert short.status_code == status.HTTP_400_BAD_REQUEST
        assert short.data['error']['code'] == 'rejection_reason_min_length_10'

    def test_lifecycle_validation_errors_accept_language_bilingual(
        self, auth_client, base_url, draft_report,
    ):
        """Lifecycle errors return English messages when Accept-Language: en is sent."""
        # 1. Unset quantity error in English and Persian
        activity = DailyReportActivity.objects.create(
            report=draft_report,
            activity_description='بتن‌ریزی',
            shift=ActivityRowShift.SHIFT_1,
            quantity_measured=True,
            quantity=None,
        )
        # English
        res_en = auth_client.post(
            f'{base_url}{draft_report.id}/submit/',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert res_en.status_code == status.HTTP_400_BAD_REQUEST
        assert res_en.data['error']['code'] == 'quantity_unset_invalid'
        assert res_en.data['error']['message'] == 'Work quantity must be specified; enter zero if no work was performed.'

        # Persian
        res_fa = auth_client.post(
            f'{base_url}{draft_report.id}/submit/',
            HTTP_ACCEPT_LANGUAGE='fa,en;q=0.5',
        )
        assert res_fa.status_code == status.HTTP_400_BAD_REQUEST
        assert res_fa.data['error']['code'] == 'quantity_unset_invalid'
        assert res_fa.data['error']['message'] == 'مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود'

        # Fix quantity to zero
        activity.quantity = 0
        activity.save(update_fields=['quantity'])

        # 2. Submit success -> transitions to SUBMITTED
        sub_res = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert sub_res.status_code == status.HTTP_200_OK

        # 3. Report not in submittable state in English
        dup_sub_en = auth_client.post(
            f'{base_url}{draft_report.id}/submit/',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert dup_sub_en.status_code == status.HTTP_400_BAD_REQUEST
        assert dup_sub_en.data['error']['code'] == 'report_not_in_submittable_state'
        assert dup_sub_en.data['error']['message'] == 'Only draft or rejected reports can be submitted.'

        # 4. Rejection errors in English
        rej_missing_en = auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': '   '},
            format='json',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert rej_missing_en.status_code == status.HTTP_400_BAD_REQUEST
        assert rej_missing_en.data['error']['code'] == 'rejection_reason_required'
        assert 'Rejection reason is required.' in rej_missing_en.data['error']['message']

        rej_short_en = auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'short'},
            format='json',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert rej_short_en.status_code == status.HTTP_400_BAD_REQUEST
        assert rej_short_en.data['error']['code'] == 'rejection_reason_min_length_10'
        assert 'Rejection reason must be at least 10 characters.' in rej_short_en.data['error']['message']

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
        assert 'submit_validation' in str(response.data)

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
            capacity=20,
        )
        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'submit_validation' in str(response.data)

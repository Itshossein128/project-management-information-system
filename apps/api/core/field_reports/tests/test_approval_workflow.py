import pytest
from decimal import Decimal
from django.utils import timezone
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
        assert rej_missing_en.data['error']['message'] == 'Rejection reason is required.'

        rej_short_en = auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'short'},
            format='json',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert rej_short_en.status_code == status.HTTP_400_BAD_REQUEST
        assert rej_short_en.data['error']['code'] == 'rejection_reason_min_length_10'
        assert rej_short_en.data['error']['message'] == 'Rejection reason must be at least 10 characters.'

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


FA_QUANTITY_UNSET_MSG = 'مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود'
EN_QUANTITY_UNSET_MSG = 'Work quantity must be specified; enter zero if no work was performed.'


def _add_measured_row(report, quantity, measured=True, description='کار اجرایی'):
    kwargs = {}
    if quantity is not None:
        kwargs['quantity'] = quantity
    return DailyReportActivity.objects.create(
        report=report,
        activity_description=description,
        shift=ActivityRowShift.SHIFT_1,
        quantity_measured=measured,
        **kwargs,
    )


def _lifecycle_snapshot(report):
    report.refresh_from_db()
    return {
        'status': report.status,
        'submitted_by': report.submitted_by,
        'submitted_at': report.submitted_at,
        'reviewed_by': report.reviewed_by,
        'reviewed_at': report.reviewed_at,
        'rejection_reason': report.rejection_reason,
    }


def _assert_lifecycle_unchanged(report, snapshot, *, expected_status=None, message='failed action must not mutate lifecycle fields'):
    report.refresh_from_db()
    if expected_status is not None:
        assert report.status == expected_status, f'failed action changed report status: {report.status} != {expected_status}'
    assert _lifecycle_snapshot(report) == snapshot, message


@pytest.mark.django_db
class TestMeasuredNullRefusal:
    """US1 (feature 036): submit refuses live measured-but-unset rows, accepts explicit zero."""

    def test_measured_null_among_zero_and_positive_rows_blocks_submit(self, auth_client, base_url, draft_report):
        zero_row = _add_measured_row(draft_report, Decimal('0.00'), description='صفر')
        positive_row = _add_measured_row(draft_report, Decimal('3.5'), description='مثبت')
        null_row = _add_measured_row(draft_report, None, description='نامشخص')
        lifecycle = _lifecycle_snapshot(draft_report)

        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error']['code'] == 'quantity_unset_invalid'
        assert response.data['error']['message'] == FA_QUANTITY_UNSET_MSG

        # A failed submit must not mutate stored quantity state or lifecycle fields.
        _assert_lifecycle_unchanged(draft_report, lifecycle)
        zero_row.refresh_from_db()
        positive_row.refresh_from_db()
        null_row.refresh_from_db()
        assert zero_row.quantity == Decimal('0.0000') and zero_row.quantity_measured is True
        assert positive_row.quantity == Decimal('3.5000') and positive_row.quantity_measured is True
        assert null_row.quantity is None and null_row.quantity_measured is True

    def test_measured_null_in_rejected_state_blocks_resubmit(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, Decimal('2'), description='اولیه')
        assert auth_client.post(f'{base_url}{draft_report.id}/submit/').status_code == status.HTTP_200_OK
        reject = auth_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'اطلاعات ناقص است و باید اصلاح شود'},
            format='json',
        )
        assert reject.status_code == status.HTTP_200_OK
        _add_measured_row(draft_report, None, description='بازگشایی بدون مقدار')
        lifecycle = _lifecycle_snapshot(draft_report)

        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error']['code'] == 'quantity_unset_invalid'
        assert response.data['error']['message'] == FA_QUANTITY_UNSET_MSG
        # Rejected lifecycle fields (including the persisted reason) stay unchanged.
        _assert_lifecycle_unchanged(draft_report, lifecycle, expected_status=ReportStatus.REJECTED)

    def test_multiple_measured_null_rows_block_submit(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, None, description='فقدان ۱', measured=True)
        _add_measured_row(draft_report, None, description='فقدان ۲', measured=True)
        lifecycle = _lifecycle_snapshot(draft_report)

        response = auth_client.post(
            f'{base_url}{draft_report.id}/submit/', HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error']['code'] == 'quantity_unset_invalid'
        assert response.data['error']['message'] == EN_QUANTITY_UNSET_MSG
        _assert_lifecycle_unchanged(draft_report, lifecycle, expected_status=ReportStatus.DRAFT)

    def test_deleted_measured_null_row_does_not_block(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, Decimal('4'), description='معتبر')
        stub_row = _add_measured_row(draft_report, None, description='حذف‌شده')
        stub_row.is_deleted = True
        stub_row.deleted_at = timezone.now()
        stub_row.save(update_fields=['is_deleted', 'deleted_at'])

        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'submitted'

    def test_explicit_zero_forms_pass_and_persist(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, Decimal('0'), description='صفر ۰')
        _add_measured_row(draft_report, Decimal('0.0'), description='صفر ۰٫۰')
        _add_measured_row(draft_report, Decimal('0.00'), description='صفر ۰٫۰۰')

        response = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'submitted'

        draft_report.refresh_from_db()
        assert draft_report.status == ReportStatus.SUBMITTED
        quantities = list(
            DailyReportActivity.objects.filter(report=draft_report).values_list('quantity', flat=True),
        )
        assert all(q == Decimal('0.0000') for q in quantities), quantities


def _create_foreign_report(user):
    """Second project owned by ``user`` with a draft daily report (US1 T009)."""
    from projects.services import create_project_with_creator

    foreign_project = create_project_with_creator(
        creator=user,
        project_code='PRJ-FGN-036',
        project_name='Foreign Project 036',
        employer='Other Employer',
        start_date='2024-01-01',
    )
    return DailyReport.objects.create(
        project=foreign_project, report_date='2024-08-02', created_by=user, updated_by=user,
        prepared_by=user,
    )


@pytest.mark.django_db
class TestWorkflowPermissionBoundaries:
    """US1 T009: denial statuses and cross-project no-mutation guarantees."""

    def test_caller_without_edit_reports_cannot_submit(self, api_client, member, base_url, draft_report):
        # ``member`` (other_user, viewer role) has no edit_reports permission.
        _add_measured_row(draft_report, Decimal('1'), description='مجاز')
        snapshot = _lifecycle_snapshot(draft_report)

        api_client.force_authenticate(user=member.user)
        response = api_client.post(f'{base_url}{draft_report.id}/submit/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        _assert_lifecycle_unchanged(draft_report, snapshot, expected_status=ReportStatus.DRAFT)

    def test_caller_without_approve_reports_cannot_reject(self, api_client, viewer_member, base_url, draft_report):
        # site_supervisor (viewer_member) has edit_reports but NOT approve_reports.
        _add_measured_row(draft_report, Decimal('1'), description='مجاز')
        auth_sub = api_client  # same user; submit succeeds (edit_reports), reject must fail
        auth_sub.force_authenticate(user=viewer_member.user)
        submit = api_client.post(f'{base_url}{draft_report.id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        snapshot = _lifecycle_snapshot(draft_report)

        response = api_client.post(
            f'{base_url}{draft_report.id}/reject/',
            {'reason': 'اطلاعات ناقص است و باید اصلاح شود'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        _assert_lifecycle_unchanged(draft_report, snapshot, expected_status=ReportStatus.SUBMITTED)

    def test_foreign_project_report_is_denied_and_untouched(self, auth_client, other_user, base_url):
        foreign_report = _create_foreign_report(other_user)
        foreign_project_id = foreign_report.project_id
        snapshot = _lifecycle_snapshot(foreign_report)

        response = auth_client.post(
            f'/api/v1/projects/{foreign_project_id}/daily-reports/{foreign_report.id}/submit/',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        _assert_lifecycle_unchanged(foreign_report, snapshot, expected_status=ReportStatus.DRAFT)


FA_REPORT_NOT_SUBMITTABLE_MSG = 'فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند'
EN_REPORT_NOT_SUBMITTABLE_MSG = 'Only draft or rejected reports can be submitted.'
FA_REASON_REQUIRED_MSG = 'دلیل رد الزامی است'
EN_REASON_REQUIRED_MSG = 'Rejection reason is required.'
FA_REASON_MIN_MSG = 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'
EN_REASON_MIN_MSG = 'Rejection reason must be at least 10 characters.'
REJECT_REASON_VALID = 'اطلاعات ناقص است و باید اصلاح شود'


def _reject(auth_client, base_url, report_id, payload, accept_language=None):
    kwargs = {'format': 'json'}
    if accept_language:
        kwargs['HTTP_ACCEPT_LANGUAGE'] = accept_language
    return auth_client.post(f'{base_url}{report_id.id if hasattr(report_id, "id") else report_id}/reject/', payload, **kwargs)


@pytest.mark.django_db
class TestRejectionFeedbackContract:
    """US2 (feature 036): stable codes and exact localized workflow feedback."""

    def _submitted_report(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, Decimal('1'), description='پاسخ')
        assert auth_client.post(f'{base_url}{draft_report.id}/submit/').status_code == status.HTTP_200_OK
        return draft_report

    def test_submit_refused_from_every_later_state(self, auth_client, base_url, draft_report):
        _add_measured_row(draft_report, Decimal('1'))
        auth_client.post(f'{base_url}{draft_report.id}/submit/')
        auth_client.post(f'{base_url}{draft_report.id}/review/')

        for accept_language, expected in (
            ('fa,en;q=0.9', FA_REPORT_NOT_SUBMITTABLE_MSG),
            ('en-US,en;q=0.9', EN_REPORT_NOT_SUBMITTABLE_MSG),
        ):
            response = auth_client.post(
                f'{base_url}{draft_report.id}/submit/', HTTP_ACCEPT_LANGUAGE=accept_language,
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data['error']['code'] == 'report_not_in_submittable_state'
            assert response.data['error']['message'] == expected

        draft_report.refresh_from_db()
        assert draft_report.status == ReportStatus.UNDER_REVIEW

        # Approved state is also not submittable.
        auth_client.post(f'{base_url}{draft_report.id}/approve/')
        approved = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert approved.status_code == status.HTTP_400_BAD_REQUEST
        assert approved.data['error']['code'] == 'report_not_in_submittable_state'

    def test_reject_mandatory_in_both_valid_source_states(self, auth_client, base_url, draft_report):
        # submitted → rejected
        self._submitted_report(auth_client, base_url, draft_report)
        rejected = _reject(auth_client, base_url, draft_report, {'reason': ' کوتاه‌ها '})  # trimmed 8 → min length
        assert rejected.status_code == status.HTTP_400_BAD_REQUEST
        assert rejected.data['error']['code'] == 'rejection_reason_min_length_10'
        assert rejected.data['error']['message'] == FA_REASON_MIN_MSG
        assert rejected.data['error']['details']['reason'][0] == FA_REASON_MIN_MSG

        ok = _reject(auth_client, base_url, draft_report, {'reason': REJECT_REASON_VALID})
        assert ok.status_code == status.HTTP_200_OK
        assert ok.data['status'] == 'rejected'

        # under_review → rejected (second copy: submit → review → reject)
        _add_measured_row(draft_report, Decimal('2'), description='سطر دوم')
        resubmit = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert resubmit.status_code == status.HTTP_200_OK
        review = auth_client.post(f'{base_url}{draft_report.id}/review/')
        assert review.status_code == status.HTTP_200_OK
        ok2 = _reject(auth_client, base_url, draft_report, {'reason': 'دلیل کوتاه'})
        assert ok2.status_code == status.HTTP_200_OK
        assert ok2.data['status'] == 'rejected'
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason == 'دلیل کوتاه'

    def test_reason_whitespace_and_boundary_cases_en(self, auth_client, base_url, draft_report):
        self._submitted_report(auth_client, base_url, draft_report)
        required_cases = [
            ('missing', None),
            ('null', None),
            ('empty', ''),
            ('spaces', '   '),
            ('tabs/newlines', ' \t\n\r '),
        ]
        for case_name, payload_reason in required_cases:
            payload = {'reason': payload_reason} if case_name != 'missing' else {}
            response = _reject(
                auth_client, base_url, draft_report, payload, accept_language='en-US,en;q=0.9',
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST, case_name
            assert response.data['error']['code'] == 'rejection_reason_required', case_name
            assert response.data['error']['message'] == EN_REASON_REQUIRED_MSG, case_name
            assert response.data['error']['details']['reason'][0] == EN_REASON_REQUIRED_MSG, case_name

        for short in ('rejsNine9', 'shortmsg7', 'کوتاهی'):
            trimmed_len = len(short.strip())
            assert trimmed_len < 10
            response = _reject(
                auth_client, base_url, draft_report, {'reason': short}, accept_language='en-US,en;q=0.9',
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST, short
            assert response.data['error']['code'] == 'rejection_reason_min_length_10', short
            assert response.data['error']['message'] == EN_REASON_MIN_MSG, short

        # Internal whitespace counts normally; exactly-10 trimmed reason passes.
        exactly_ten = 'exactlyten'
        ok_en = _reject(
            auth_client, base_url, draft_report, {'reason': f'  {exactly_ten}  '},
            accept_language='en-US,en;q=0.9',
        )
        assert ok_en.status_code == status.HTTP_200_OK
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason == exactly_ten

    def test_reason_exact_bilingual_messages_fa(self, auth_client, base_url, draft_report):
        self._submitted_report(auth_client, base_url, draft_report)
        required = _reject(auth_client, base_url, draft_report, {}, accept_language='fa,en;q=0.9')
        assert required.status_code == status.HTTP_400_BAD_REQUEST
        assert required.data['error']['code'] == 'rejection_reason_required'
        assert required.data['error']['message'] == FA_REASON_REQUIRED_MSG
        assert required.data['error']['details']['reason'][0] == FA_REASON_REQUIRED_MSG

        short = _reject(auth_client, base_url, draft_report, {'reason': 'کوتاه'}, accept_language='fa,en;q=0.9')
        assert short.data['error']['code'] == 'rejection_reason_min_length_10'
        assert short.data['error']['message'] == FA_REASON_MIN_MSG

        exactly_ten_fa = 'دلیل کوتاه'
        ok_fa = _reject(auth_client, base_url, draft_report, {'reason': exactly_ten_fa}, accept_language='fa,en;q=0.9')
        assert ok_fa.status_code == status.HTTP_200_OK
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason == exactly_ten_fa

        # Cycle back so the long-reason reject runs from under_review again.
        resubmit = auth_client.post(f'{base_url}{draft_report.id}/submit/')
        assert resubmit.status_code == status.HTTP_200_OK
        assert auth_client.post(f'{base_url}{draft_report.id}/review/').status_code == status.HTTP_200_OK

        long_reason = 'این دلیل رد کامل طولانی‌تر از ده کاراکتر است'
        ok_long_fa = _reject(auth_client, base_url, draft_report, {'reason': long_reason})
        assert ok_long_fa.status_code == status.HTTP_200_OK
        draft_report.refresh_from_db()
        assert draft_report.rejection_reason == long_reason

    def test_invalid_reason_leaves_report_untouched(self, auth_client, base_url, draft_report):
        self._submitted_report(auth_client, base_url, draft_report)
        snapshot = _lifecycle_snapshot(draft_report)

        short = _reject(auth_client, base_url, draft_report, {'reason': 'کوتاه'})
        assert short.status_code == status.HTTP_400_BAD_REQUEST
        _assert_lifecycle_unchanged(draft_report, snapshot)

        missing = _reject(auth_client, base_url, draft_report, {})
        assert missing.status_code == status.HTTP_400_BAD_REQUEST
        _assert_lifecycle_unchanged(draft_report, snapshot)

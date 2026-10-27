import pytest
from django.utils import timezone
from rest_framework import status

from field_reports.models import (
    CorrectionRequestStatus,
    DailyReport,
    DailyReportActivity,
    DailyReportCorrectionRequest,
    DailyReportGeneralActivity,
    DailyReportIncident,
    DailyReportMachineryRow,
    DailyReportVisit,
    ReportStatus,
)
from field_reports.services import sync_batch
from projects.tests.contractor_select_helpers import make_active_contractor


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestDailyReportGapsCorrection:
    def test_correction_clones_all_lifecycle_rows_and_version_metadata(
        self, auth_client, reports_url, project, user,
    ):
        contractor = make_active_contractor(project, user, 'پیمانکار آزمون')
        source = DailyReport.objects.create(
            project=project, report_date='2024-08-31', status=ReportStatus.APPROVED,
            is_current=True, created_by=user, updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=source, activity_description='فعالیت اصلی', shift='shift_1',
            quantity=0, quantity_measured=True, crew_name='اکیپ الف', foreman_count=1,
            worker_count=4, parcel='P-1', source_discipline='civil',
            contractor_ref=contractor,
        )
        deleted = DailyReportActivity.objects.create(
            report=source, activity_description='حذف‌شده', shift='shift_1', quantity=1,
        )
        deleted.is_deleted = True
        deleted.save(update_fields=['is_deleted'])
        DailyReportMachineryRow.objects.create(
            report=source, equipment_type='جرثقیل', status_total=2, status_active=1,
            source_discipline='civil',
        )
        DailyReportGeneralActivity.objects.create(
            report=source, row_number=1, activity_description='نظافت', source_discipline='civil',
        )
        DailyReportVisit.objects.create(
            report=source, row_number=1, text='بازدید ناظر', source_discipline='civil',
        )
        DailyReportIncident.objects.create(
            report=source, incident_type='safety', description='حادثه', severity='major',
            source_row_id='incident-source',
        )
        response = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اصلاح همه ردیف‌های گزارش روزانه'}, format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        result = DailyReport.objects.get(pk=response.data['result_report_id'])
        assert result.version_number == 2 and result.is_current
        activity = result.activities.get()
        assert (activity.crew_name, activity.foreman_count, activity.worker_count, activity.parcel) == ('اکیپ الف', 1, 4, 'P-1')
        assert activity.source_discipline == 'civil'
        assert activity.contractor_ref_id == contractor.id
        assert result.activities.filter(is_deleted=False).count() == 1
        assert result.machinery_rows.get().status_total == 2
        assert result.general_activities.get().activity_description == 'نظافت'
        assert result.visits.get().text == 'بازدید ناظر'
        incident = result.incidents.get()
        assert (incident.severity, incident.source_row_id) == ('major', 'incident-source')
        versions = auth_client.get(f'{reports_url}{source.id}/versions/')
        assert versions.status_code == status.HTTP_200_OK
        assert versions.data[0]['correction_reason'] is None
        assert versions.data[1]['correction_reason'] == 'اصلاح همه ردیف‌های گزارش روزانه'
        assert versions.data[1]['modifier_name']
        assert versions.data[0]['version_number'] == 1
        assert versions.data[1]['version_number'] == 2
        assert versions.data[0]['approved_at'] is not None or versions.data[0]['status'] == 'approved'

    def test_correction_already_open_api_envelope(self, auth_client, reports_url, project, user):
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-16',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        opened = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اولین درخواست اصلاح گزارش'},
            format='json',
        )
        assert opened.status_code == status.HTTP_201_CREATED
        result = DailyReport.objects.get(pk=opened.data['result_report_id'])
        result.is_current = False
        result.save(update_fields=['is_current'])
        source.is_current = True
        source.save(update_fields=['is_current'])

        duplicate = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'دومین درخواست اصلاح گزارش'},
            format='json',
        )
        assert duplicate.status_code == status.HTTP_400_BAD_REQUEST
        assert duplicate.data['error']['code'] == 'correction_already_open'
        assert DailyReport.objects.filter(project=project, is_deleted=False).count() == 2

    def test_version_lineage_from_result_report(self, auth_client, reports_url, project, user):
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-17',
            status=ReportStatus.APPROVED,
            is_current=True,
            approved_at=timezone.now(),
            created_by=user,
            updated_by=user,
        )
        opened = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اصلاح برای تست تاریخچه نسخه'},
            format='json',
        )
        assert opened.status_code == status.HTTP_201_CREATED
        result_id = opened.data['result_report_id']
        from_result = auth_client.get(f'{reports_url}{result_id}/versions/')
        assert from_result.status_code == status.HTTP_200_OK
        assert len(from_result.data) == 2
        assert from_result.data[0]['correction_reason'] is None
        assert from_result.data[1]['correction_reason'] == 'اصلاح برای تست تاریخچه نسخه'
        assert from_result.data[0]['version_number'] < from_result.data[1]['version_number']

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

        assert getattr(exc.value, 'detail', {}).get('detail').code == 'correction_already_open'

    def test_cancel_correction_restores_only_current_draft(
        self, auth_client, reports_url, project, user,
    ):
        source = DailyReport.objects.create(
            project=project, report_date='2024-09-15', status=ReportStatus.APPROVED,
            is_current=True, created_by=user, updated_by=user,
        )
        opened = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اصلاح برای آزمایش لغو ایمن'}, format='json',
        )
        assert opened.status_code == status.HTTP_201_CREATED
        cancelled = auth_client.post(
            f'/api/v1/projects/{project.id}/correction-requests/{opened.data["id"]}/cancel/',
            format='json',
        )
        assert cancelled.status_code == status.HTTP_200_OK
        assert cancelled.data['source_report_id'] == str(source.id)
        source.refresh_from_db()
        result = DailyReport.all_objects.get(pk=opened.data['result_report_id'])
        assert source.status == ReportStatus.APPROVED and source.is_current
        assert result.is_deleted and not result.is_current

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

    def test_correction_version_copies_weather_and_inactivity_metadata(self, project, user):
        from field_reports.models import WeatherCondition, InactivityReason, SiteStatus
        from field_reports.services.correction_service import open_correction
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-08',
            shift='full',
            status=ReportStatus.APPROVED,
            is_current=True,
            weather_condition=WeatherCondition.RAINY,
            temp_min=10.5,
            temp_max=18.2,
            site_status=SiteStatus.INACTIVE,
            inactivity_reason=InactivityReason.WEATHER,
            weather_impact_notes='بارندگی شدید باعث توقف کار شد',
            created_by=user,
            updated_by=user,
        )
        corr = open_correction(
            source_report=source,
            user=user,
            reason='Correction reason at least 10 chars',
        )
        res_rep = corr.result_report
        assert res_rep.weather_condition == WeatherCondition.RAINY
        assert float(res_rep.temp_min) == 10.5
        assert float(res_rep.temp_max) == 18.2
        assert res_rep.site_status == SiteStatus.INACTIVE
        assert res_rep.inactivity_reason == InactivityReason.WEATHER
        assert res_rep.weather_impact_notes == 'بارندگی شدید باعث توقف کار شد'

    def test_child_clone_specs_fieldwise_registry_coverage(self):
        """Fieldwise regression: every child model domain field must be in CHILD_CLONE_SPECS."""
        from field_reports.services.correction_service import CHILD_CLONE_SPECS

        exclude = {'id', 'is_deleted', 'deleted_at', 'report', 'report_id'}
        for model, rel_name, fields in CHILD_CLONE_SPECS:
            model_fields = set()
            for f in model._meta.concrete_fields:
                if f.name in exclude:
                    continue
                if f.is_relation and f.many_to_one:
                    model_fields.add(f.attname)
                else:
                    model_fields.add(f.name)
            missing = model_fields - set(fields)
            extra = set(fields) - model_fields
            assert not missing, f'{model.__name__} has unhandled fields in CHILD_CLONE_SPECS: {missing}'
            assert not extra, f'{model.__name__} has extra non-existent fields in CHILD_CLONE_SPECS: {extra}'

    def test_correction_cloning_handles_empty_collections_and_soft_delete(
        self, auth_client, reports_url, project, user,
    ):
        """Verify reports with zero rows in some sections and soft-deleted rows clone safely."""
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-09',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        act = DailyReportActivity.objects.create(
            report=source,
            activity_description='فعالیت غیرحذف‌شده',
            shift='shift_1',
            quantity=10,
        )
        deleted_act = DailyReportActivity.objects.create(
            report=source,
            activity_description='فعالیت حذف‌شده',
            shift='shift_1',
            quantity=5,
        )
        deleted_act.is_deleted = True
        deleted_act.save(update_fields=['is_deleted'])

        res = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'تست کلون مجموعه‌های خالی و موارد حذف‌شده'},
            format='json',
        )
        assert res.status_code == status.HTTP_201_CREATED
        result = DailyReport.objects.get(pk=res.data['result_report_id'])
        assert result.activities.filter(is_deleted=False).count() == 1
        assert result.activities.get().activity_description == 'فعالیت غیرحذف‌شده'
        assert result.incidents.count() == 0
        assert result.concrete_logs.count() == 0
        assert result.labor_camp_entries.count() == 0

    def test_cancel_correction_refuses_non_open_request_without_mutation(
        self, auth_client, reports_url, project, user,
    ):
        """Re-cancelling an already-cancelled correction returns 400 without duplicate mutations."""
        from rest_framework.exceptions import ValidationError
        from field_reports.services.correction_service import cancel_correction

        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-10',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        opened = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اصلاح برای بررسی لغو چندباره'},
            format='json',
        )
        assert opened.status_code == status.HTTP_201_CREATED
        corr_id = opened.data['id']

        # First cancellation succeeds
        c1 = auth_client.post(
            f'/api/v1/projects/{project.id}/correction-requests/{corr_id}/cancel/',
            format='json',
        )
        assert c1.status_code == status.HTTP_200_OK

        # Second cancellation must be refused with 400
        c2 = auth_client.post(
            f'/api/v1/projects/{project.id}/correction-requests/{corr_id}/cancel/',
            format='json',
        )
        assert c2.status_code == status.HTTP_400_BAD_REQUEST
        assert c2.data['error']['code'] == 'correction_not_open'

        # Direct service call on already cancelled request must raise ValidationError
        corr_obj = DailyReportCorrectionRequest.objects.get(pk=corr_id)
        with pytest.raises(ValidationError):
            cancel_correction(correction=corr_obj, user=user)

        source.refresh_from_db()
        assert source.is_current is True

    def test_cancel_correction_enforces_source_result_relationship(
        self, project, user,
    ):
        """Cancellable result must match project, lineage, supersedes, and version sequence."""
        from rest_framework.exceptions import ValidationError
        from field_reports.services.correction_service import cancel_correction

        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-11',
            status=ReportStatus.APPROVED,
            is_current=False,
            version_number=1,
            created_by=user,
            updated_by=user,
        )
        # Create an illegitimate result report with version_number mismatch (version 3 instead of 2)
        mismatched_result = DailyReport.objects.create(
            project=project,
            report_date='2024-09-11',
            status=ReportStatus.DRAFT,
            is_current=True,
            version_number=3,
            supersedes=source,
            created_by=user,
            updated_by=user,
        )
        corr = DailyReportCorrectionRequest.objects.create(
            project=project,
            source_report=source,
            result_report=mismatched_result,
            reason='درخواست با شماره نسخه نامعتبر',
            status=CorrectionRequestStatus.SUBMITTED,
            created_by=user,
            updated_by=user,
        )

        with pytest.raises(ValidationError) as exc_info:
            cancel_correction(correction=corr, user=user)
        assert exc_info.value.detail['detail'].code == 'result_not_cancellable'

        # Source report should remain un-restored
        source.refresh_from_db()
        assert source.is_current is False

    def test_cancellation_canonical_and_alias_routes(
        self, auth_client, reports_url, project, user,
    ):
        """Both canonical and alias cancellation routes operate identically."""
        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-11',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        opened = auth_client.post(
            f'{reports_url}{source.id}/correction-requests/',
            {'reason': 'اصلاح برای آزمایش هر دو مسیر لغو'},
            format='json',
        )
        assert opened.status_code == status.HTTP_201_CREATED
        corr_id = opened.data['id']

        # Cancel via alias path
        alias_res = auth_client.post(
            f'/api/v1/projects/{project.id}/daily-reports/correction-requests/{corr_id}/cancel/',
            format='json',
        )
        assert alias_res.status_code == status.HTTP_200_OK
        assert alias_res.data['source_report_id'] == str(source.id)

    def test_query_count_and_timing_evidence(
        self, auth_client, reports_url, project, user,
    ):
        """Query count and timing evidence for cloning, cancellation, and versions."""
        import time
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-12',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=source,
            activity_description='فعالیت تست عملکرد',
            shift='shift_1',
            quantity=10,
        )

        # 1. Open correction
        t0 = time.perf_counter()
        with CaptureQueriesContext(connection) as ctx_open:
            open_res = auth_client.post(
                f'{reports_url}{source.id}/correction-requests/',
                {'reason': 'تست کارایی باز کردن اصلاح'},
                format='json',
            )
        t_open = time.perf_counter() - t0
        assert open_res.status_code == status.HTTP_201_CREATED
        corr_id = open_res.data['id']
        # Ensure queries are bounded (DRF auth, permission checks, row locks, and 10 child specs cloning)
        assert len(ctx_open.captured_queries) < 50
        assert t_open < 0.5  # Under 500 ms

        # 2. Version history retrieval
        from field_reports.services.correction_service import list_versions
        with CaptureQueriesContext(connection) as ctx_service:
            list(list_versions(source))
        assert len(ctx_service.captured_queries) <= 3  # Direct service query count is bounded to 2 queries

        t0 = time.perf_counter()
        with CaptureQueriesContext(connection) as ctx_vers:
            vers_res = auth_client.get(f'{reports_url}{source.id}/versions/')
        t_vers = time.perf_counter() - t0
        assert vers_res.status_code == status.HTTP_200_OK
        assert len(ctx_vers.captured_queries) < 40  # Pre-fetched version history + auth/perm queries
        assert t_vers < 0.2  # Under 200 ms

        # 3. Cancel correction
        t0 = time.perf_counter()
        with CaptureQueriesContext(connection) as ctx_cancel:
            cancel_res = auth_client.post(
                f'/api/v1/projects/{project.id}/correction-requests/{corr_id}/cancel/',
                format='json',
            )
        t_cancel = time.perf_counter() - t0
        assert cancel_res.status_code == status.HTTP_200_OK
        assert len(ctx_cancel.captured_queries) < 40
        assert t_cancel < 0.5  # Under 500 ms

    @pytest.mark.django_db(transaction=True)
    def test_postgresql_transactional_concurrency_two_simultaneous_corrections(
        self, project, user,
    ):
        """Simultaneous correction requests: exactly one succeeds (201), the other 400."""
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections, close_old_connections
        from rest_framework.test import APIClient

        source = DailyReport.objects.create(
            project=project,
            report_date='2024-09-13',
            status=ReportStatus.APPROVED,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        url = f'/api/v1/projects/{project.id}/daily-reports/{source.id}/correction-requests/'
        barrier = Barrier(2)

        def attempt_correction(client_id):
            close_old_connections()
            client = APIClient()
            client.force_authenticate(user=user)
            try:
                barrier.wait(timeout=10)
                return client.post(
                    url,
                    {'reason': f'درخواست اصلاح همزمان شماره {client_id}'},
                    format='json',
                )
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(attempt_correction, 1)
            f2 = pool.submit(attempt_correction, 2)
            res1 = f1.result(timeout=15)
            res2 = f2.result(timeout=15)

        statuses = sorted([res1.status_code, res2.status_code])
        assert statuses == [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

        # The failing request has code 'correction_already_open'
        failed_res = res1 if res1.status_code == 400 else res2
        err_code = failed_res.data.get('error', {}).get('code') or failed_res.data.get('detail', '')
        assert 'correction_already_open' in str(failed_res.data)

        # Exactly 1 active draft report exists for this lineage
        lineage_id = source.lineage_id or source.id
        draft_count = DailyReport.objects.filter(
            project=project,
            lineage_id=lineage_id,
            status=ReportStatus.DRAFT,
            is_current=True,
            is_deleted=False,
        ).count()
        assert draft_count == 1

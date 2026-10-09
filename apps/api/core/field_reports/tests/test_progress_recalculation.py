import pytest

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    ReportStatus,
)
from field_reports.tasks import recalculate_activity_progress
from schedule.models import ActivityProgress


@pytest.mark.django_db
class TestProgressRecalculation:
    def test_creates_progress_record(self, project, user, activity, approved_measurement):
        # activity.total_quantity == 100 (see conftest fixture)
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-01', status=ReportStatus.APPROVED,
            approved_by=user, created_by=user, updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='اجرا',
            shift=ActivityRowShift.SHIFT_1,
            quantity=25,
            quantity_measured=True,
        )

        result = recalculate_activity_progress(str(report.id))
        assert result['activities'] == 1

        progress = ActivityProgress.objects.get(activity=activity, report_date='2024-10-01')
        assert float(progress.cumulative_quantity) == 25.0
        assert float(progress.actual_progress) == pytest.approx(0.25)
        # Approved daily report advances approved progress + stamps the measurement version.
        assert float(progress.approved_progress) == pytest.approx(0.25)
        assert progress.technical_approved_at is not None
        assert progress.measurement_version_id == approved_measurement.current_version_id

    def test_progress_over_100_is_not_capped_or_written(self, project, user, activity, approved_measurement):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-02', status=ReportStatus.APPROVED,
            approved_by=user, created_by=user, updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='اجرا',
            shift=ActivityRowShift.SHIFT_1,
            quantity=250,
            quantity_measured=True,
        )
        result = recalculate_activity_progress(str(report.id))
        # Over-quantity must never be written as a capped 1.0 success.
        assert not ActivityProgress.objects.filter(activity=activity, report_date='2024-10-02').exists()
        assert result['applied'] == 0
        assert result['skipped'] == [{'activity_id': str(activity.id), 'code': 'progress_exceeds_100'}]

    def test_over_100_keeps_previous_progress(self, project, user, activity, approved_measurement):
        for day, qty in (('2024-10-01', 60), ('2024-10-02', 60)):
            report = DailyReport.objects.create(
                project=project, report_date=day, status=ReportStatus.APPROVED,
                approved_by=user, created_by=user, updated_by=user,
            )
            DailyReportActivity.objects.create(
                report=report, activity_ref=activity, activity_description='اجرا',
                shift=ActivityRowShift.SHIFT_1, quantity=qty, quantity_measured=True,
            )
            recalculate_activity_progress(str(report.id))
        assert float(ActivityProgress.objects.get(activity=activity, report_date='2024-10-01').actual_progress) == pytest.approx(0.6)
        assert not ActivityProgress.objects.filter(activity=activity, report_date='2024-10-02').exists()

    def test_skips_activity_without_approved_measurement(self, project, user, activity):
        report = DailyReport.objects.create(
            project=project, report_date='2024-10-03', status=ReportStatus.APPROVED,
            approved_by=user, created_by=user, updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report, activity_ref=activity, activity_description='اجرا',
            shift=ActivityRowShift.SHIFT_1, quantity=10, quantity_measured=True,
        )
        result = recalculate_activity_progress(str(report.id))
        assert result['applied'] == 0
        assert not ActivityProgress.objects.filter(activity=activity).exists()

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
    def test_creates_progress_record(self, project, user, activity):
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

    def test_progress_capped_at_one(self, project, user, activity):
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
        recalculate_activity_progress(str(report.id))
        progress = ActivityProgress.objects.get(activity=activity, report_date='2024-10-02')
        assert float(progress.actual_progress) == 1.0

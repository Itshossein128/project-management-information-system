import pytest
from django.db import IntegrityError

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    DailyReportLabor,
    LaborCategory,
    ReportShift,
    ReportStatus,
)


@pytest.fixture
def daily_report(db, project, user):
    return DailyReport.objects.create(
        project=project,
        report_date='2024-01-01',
        shift=ReportShift.DAY,
        prepared_by=user,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestDailyReportModel:
    def test_create_defaults(self, project, user):
        report = DailyReport.objects.create(
            project=project, report_date='2024-02-01', created_by=user, updated_by=user,
        )
        assert report.id is not None
        assert report.status == ReportStatus.DRAFT
        assert report.synced_from_offline is False
        assert report.is_deleted is False

    def test_unique_active_report_per_date(self, project, user):
        DailyReport.objects.create(
            project=project, report_date='2024-03-01', created_by=user, updated_by=user,
        )
        with pytest.raises(IntegrityError):
            DailyReport.objects.create(
                project=project, report_date='2024-03-01', created_by=user, updated_by=user,
            )


@pytest.mark.django_db
class TestChildRows:
    def test_activity_row(self, daily_report, activity):
        row = DailyReportActivity.objects.create(
            report=daily_report,
            activity_ref=activity,
            activity_description='بتن‌ریزی فونداسیون',
            shift=ActivityRowShift.SHIFT_1,
            quantity=15.5,
            unit='m3',
        )
        assert row.id is not None
        assert row.quantity_measured is True

    def test_labor_total_is_computed(self, daily_report):
        row = DailyReportLabor.objects.create(
            report=daily_report,
            labor_category=LaborCategory.DIRECT,
            job_title='بنا',
            shift_1_count=3,
            shift_2_count=2,
            shift_3_count=1,
        )
        assert row.total_count == 6

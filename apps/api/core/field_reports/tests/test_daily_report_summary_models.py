import pytest

from field_reports.models import DailyReport, ReportShift
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import SUMMARY_DATE


@pytest.mark.django_db
def test_ensure_creates_full_shift_auto_summary(project, user):
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert report.shift == ReportShift.FULL
    assert report.is_auto_summary is True
    assert report.aggregated_at is not None
    assert report.management_opinion == ''
    assert report.weather_override is False
    assert report.site_status_override is False
    assert DailyReport.objects.filter(
        project=project, report_date=SUMMARY_DATE, shift=ReportShift.FULL, is_current=True,
    ).count() == 1


@pytest.mark.django_db
def test_ensure_is_idempotent(project, user):
    a = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    b = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert a.id == b.id

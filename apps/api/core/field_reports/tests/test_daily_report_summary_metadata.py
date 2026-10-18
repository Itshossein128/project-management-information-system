import pytest

from field_reports.models import WeatherCondition
from field_reports.services.daily_report_aggregation import (
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_management_opinion_and_weather_override_survive_rebuild(project, user):
    sr = make_sub_report(
        project, user, status=SubReportStatus.SUBMITTED, weather_condition='rainy',
    )
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.management_opinion = 'نظر مدیریت'
    report.weather_override = True
    report.weather_condition = WeatherCondition.SUNNY
    report.save()

    sr.weather_condition = 'stormy'
    sr.save(update_fields=['weather_condition', 'updated_at'])
    rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.refresh_from_db()
    assert report.management_opinion == 'نظر مدیریت'
    assert report.weather_condition == WeatherCondition.SUNNY

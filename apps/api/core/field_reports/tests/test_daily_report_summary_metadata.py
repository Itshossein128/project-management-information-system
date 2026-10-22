import pytest

from field_reports.models import InactivityReason, WeatherCondition
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
    report.weather_condition = WeatherCondition.CLEAR
    report.save()

    sr.weather_condition = 'stormy'
    sr.save(update_fields=['weather_condition', 'updated_at'])
    rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.refresh_from_db()
    assert report.management_opinion == 'نظر مدیریت'
    assert report.weather_condition == WeatherCondition.CLEAR


@pytest.mark.django_db
def test_aggregation_inactivity_reason_behavior(project, user):
    d = SUMMARY_DATE
    sr = make_sub_report(
        project, user, status=SubReportStatus.SUBMITTED, site_status='inactive', report_date=d
    )
    summary = ensure_daily_report_summary(project.id, d, user=user)
    assert summary.site_status == 'inactive'
    # Without human selection, inactivity_reason remains '' (no invented fake reason)
    assert summary.inactivity_reason == ''

    # User manually assigns a valid reason
    summary.inactivity_reason = InactivityReason.WEATHER
    summary.save()

    # Rebuild when derived inactive preserves the existing valid reason
    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.site_status == 'inactive'
    assert rebuilt.inactivity_reason == InactivityReason.WEATHER

    # When specialty reports transition to active, rebuild sets active and clears inactivity_reason
    sr.site_status = 'active'
    sr.save(update_fields=['site_status', 'updated_at'])
    rebuilt_active = rebuild_daily_report_summary(project.id, d, user=user, report=rebuilt)
    assert rebuilt_active.site_status == 'active'
    assert rebuilt_active.inactivity_reason == ''

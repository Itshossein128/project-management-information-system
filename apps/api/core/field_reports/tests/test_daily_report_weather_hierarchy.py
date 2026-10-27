import pytest
from rest_framework import status
from django.utils import timezone

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport, WeatherCondition
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import make_sub_report
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_weather_severity_hierarchy_selection(project, user):
    """Verify that daily rollup selects the highest severity weather:
    clear < cloudy < rainy < snowy < stormy.
    """
    today = timezone.localdate()
    # Civil reports cloudy
    make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
        weather_condition=WeatherCondition.CLOUDY,
    )
    # Electrical reports stormy
    make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.ELECTRICAL,
        discipline='electrical',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
        weather_condition=WeatherCondition.STORMY,
    )
    # Mechanical reports rainy
    make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.MECHANICAL,
        discipline='mechanical',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
        weather_condition=WeatherCondition.RAINY,
    )

    summary = ensure_daily_report_summary(project.id, today, user=user)
    assert summary.weather_condition == WeatherCondition.STORMY
    meta = build_aggregation_meta(project.id, today, summary)
    assert meta['weather_source'] == 'derived'


@pytest.mark.django_db
def test_weather_override_preserves_manager_values_and_sets_source(project, user):
    """FR-013: weather_override=True must not be replaced by rollup,
    and metadata must record weather_source='overridden_by_manager'.
    """
    today = timezone.localdate()
    make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
        weather_condition=WeatherCondition.STORMY,
    )

    summary = ensure_daily_report_summary(project.id, today, user=user)
    # Manager manually sets weather to clear and temp
    summary.weather_condition = WeatherCondition.CLEAR
    summary.weather_override = True
    summary.temp_min = 18.0
    summary.temp_max = 30.0
    summary.save()

    # Rebuild rollup
    rebuilt = rebuild_daily_report_summary(project.id, today, user=user)
    assert rebuilt.weather_condition == WeatherCondition.CLEAR
    assert rebuilt.weather_override is True
    assert rebuilt.temp_min == 18.0
    assert rebuilt.temp_max == 30.0

    meta = build_aggregation_meta(project.id, today, rebuilt)
    assert meta['weather_source'] == 'overridden_by_manager'

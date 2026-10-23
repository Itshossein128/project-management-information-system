"""Tests for legacy weather normalization and schema migration (0018_daily_header_weather and 0004_standardize_weather)."""
import importlib
import pytest
from common.reporting_units import SpecialtyUnit
from django.apps import apps
from django.core.validators import MinValueValidator, MaxValueValidator

from field_reports.models import DailyReport, WeatherLog
from sub_reports.models import DisciplineSubReport, Discipline

migration_0018 = importlib.import_module('field_reports.migrations.0018_daily_header_weather')
normalize_weather_conditions = migration_0018.normalize_weather_conditions

migration_0004 = importlib.import_module('sub_reports.migrations.0004_standardize_weather')
normalize_discipline_weather_conditions = migration_0004.normalize_discipline_weather_conditions


@pytest.mark.django_db
def test_normalize_weather_conditions_daily_report_and_weather_log(project, user):
    """Verify normalize_weather_conditions maps sunny->clear, partly_cloudy->cloudy, foggy->cloudy."""
    r1 = DailyReport.objects.create(project=project, report_date='2026-08-01', created_by=user, updated_by=user)
    r2 = DailyReport.objects.create(project=project, report_date='2026-08-02', created_by=user, updated_by=user)
    r3 = DailyReport.objects.create(project=project, report_date='2026-08-03', created_by=user, updated_by=user)
    r4 = DailyReport.objects.create(project=project, report_date='2026-08-04', created_by=user, updated_by=user)

    DailyReport.objects.filter(id=r1.id).update(weather_condition='sunny')
    DailyReport.objects.filter(id=r2.id).update(weather_condition='partly_cloudy')
    DailyReport.objects.filter(id=r3.id).update(weather_condition='foggy')
    DailyReport.objects.filter(id=r4.id).update(weather_condition='rainy')

    w1 = WeatherLog.objects.create(project=project, log_date='2026-08-01', weather_condition='clear', created_by=user, updated_by=user)
    w2 = WeatherLog.objects.create(project=project, log_date='2026-08-02', weather_condition='clear', created_by=user, updated_by=user)
    w3 = WeatherLog.objects.create(project=project, log_date='2026-08-03', weather_condition='clear', created_by=user, updated_by=user)
    WeatherLog.objects.filter(id=w1.id).update(weather_condition='sunny')
    WeatherLog.objects.filter(id=w2.id).update(weather_condition='partly_cloudy')
    WeatherLog.objects.filter(id=w3.id).update(weather_condition='foggy')

    normalize_weather_conditions(apps, None)

    r1.refresh_from_db()
    r2.refresh_from_db()
    r3.refresh_from_db()
    r4.refresh_from_db()
    assert r1.weather_condition == 'clear'
    assert r2.weather_condition == 'cloudy'
    assert r3.weather_condition == 'cloudy'
    assert r4.weather_condition == 'rainy'

    w1.refresh_from_db()
    w2.refresh_from_db()
    w3.refresh_from_db()
    assert w1.weather_condition == 'clear'
    assert w2.weather_condition == 'cloudy'
    assert w3.weather_condition == 'cloudy'


@pytest.mark.django_db
def test_normalize_discipline_weather_conditions(project, user):
    """Verify normalize_discipline_weather_conditions maps sunny->clear, partly_cloudy->cloudy, foggy->cloudy."""
    s1 = DisciplineSubReport.objects.create(
        project=project,
        unit=SpecialtyUnit.BUILDINGS,
        discipline=Discipline.CIVIL,
        report_date='2026-08-10',
        weather_condition='clear',
        created_by=user,
        updated_by=user,
    )
    s2 = DisciplineSubReport.objects.create(
        project=project,
        unit=SpecialtyUnit.ELECTRICAL,
        discipline=Discipline.ELECTRICAL,
        report_date='2026-08-10',
        weather_condition='clear',
        created_by=user,
        updated_by=user,
    )
    s3 = DisciplineSubReport.objects.create(
        project=project,
        unit=SpecialtyUnit.MECHANICAL,
        discipline=Discipline.MECHANICAL,
        report_date='2026-08-10',
        weather_condition='clear',
        created_by=user,
        updated_by=user,
    )

    DisciplineSubReport.objects.filter(id=s1.id).update(weather_condition='sunny')
    DisciplineSubReport.objects.filter(id=s2.id).update(weather_condition='partly_cloudy')
    DisciplineSubReport.objects.filter(id=s3.id).update(weather_condition='foggy')

    normalize_discipline_weather_conditions(apps, None)

    s1.refresh_from_db()
    s2.refresh_from_db()
    s3.refresh_from_db()
    assert s1.weather_condition == 'clear'
    assert s2.weather_condition == 'cloudy'
    assert s3.weather_condition == 'cloudy'


@pytest.mark.django_db
def test_migration_schema_validators_and_fields():
    """Verify field_reports schema has weather_impact_notes and decimal bounds on temp_min/temp_max."""
    dr_fields = {f.name: f for f in DailyReport._meta.fields}
    assert 'weather_impact_notes' in dr_fields
    assert dr_fields['weather_impact_notes'].default == ''

    temp_min = dr_fields['temp_min']
    temp_max = dr_fields['temp_max']

    min_validators = [v for v in temp_min.validators if isinstance(v, MinValueValidator)]
    max_validators = [v for v in temp_max.validators if isinstance(v, MaxValueValidator)]
    assert min_validators, "temp_min must have MinValueValidator"
    assert max_validators, "temp_max must have MaxValueValidator"
    assert min_validators[0].limit_value == -40
    assert max_validators[0].limit_value == 60

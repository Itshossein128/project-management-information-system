from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_b01_migrations_preserve_legacy_and_enforce_uniqueness():
    previous = [('projects', '0021_project_measurement_unit'),
                ('field_reports', '0025_material_unknown_type')]
    current = [('projects', '0022_project_coordinates'),
               ('field_reports', '0026_daily_report_b01_contract')]
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    actor = get_user_model().objects.create_user(username='b01-migration-test')
    try:
        executor.migrate(previous)
        old_apps = executor.loader.project_state(previous).apps
        project = old_apps.get_model('projects', 'Project').objects.create(
            project_code='B01-MIGRATION', project_name='Migration test',
        )
        report_date = date(2027, 5, 22)
        old_reports = old_apps.get_model('field_reports', 'DailyReport').objects
        legacy_ids = {
            old_reports.create(project_id=project.pk, report_date=report_date, shift=shift, created_by_id=actor.pk).pk
            for shift in ('day', 'night')
        }
        for repeat in range(2):
            executor = MigrationExecutor(connection)
            executor.migrate(current)
            apps = executor.loader.project_state(current).apps
            assert apps.get_model('projects', 'Project').objects.get(pk=project.pk).latitude is None
            reports = apps.get_model('field_reports', 'DailyReport').objects.filter(project_id=project.pk)
            assert set(reports.filter(contract_version='').values_list('pk', flat=True)) == legacy_ids
            if repeat == 0:
                executor = MigrationExecutor(connection)
                executor.migrate(previous)
        args = dict(project_id=project.pk, report_date=date(2027, 5, 23),
                    contract_version='1.0.0', created_by_id=actor.pk)
        report = reports.create(shift='full', **args)
        with pytest.raises(IntegrityError, match='unique_current_contract_daily_report_per_date'), transaction.atomic():
            reports.create(shift='day', **args)
        reports.create(shift='full', is_current=False, **args)
        reports.create(shift='full', is_deleted=True, **args)
        shifts = apps.get_model('field_reports', 'DailyReportWorkedShift').objects
        shifts.create(report_id=report.pk, shift_id=1)
        for values, constraint in (
            ({'shift_id': 1}, 'unique_worked_shift_per_report'),
            ({'shift_id': 4}, 'daily_report_worked_shift_id_valid'),
            ({'shift_id': 2, 'actual_duration_hours': 0}, 'daily_report_worked_shift_duration_valid'),
            ({'shift_id': 3, 'actual_duration_hours': 25}, 'daily_report_worked_shift_duration_valid'),
        ):
            with pytest.raises(IntegrityError, match=constraint), transaction.atomic():
                shifts.create(report_id=report.pk, **values)
    finally:
        MigrationExecutor(connection).migrate(latest)


def test_published_contract_covers_reference_form_fields_and_governance():
    from field_reports.services.data_contract import get_scope_decisions, load_daily_report_contract

    contract = load_daily_report_contract()
    assert contract['contract_version'] == '1.0.0'
    assert contract['reference_form_version'] == 'shiraz-file4-v1'
    assert {row['section_number'] for row in contract['broader_sections']} == set(range(1, 19))
    assert {row['section_number'] for row in contract['field_mappings']} == set(range(1, 19))
    assert all(row['drill_down_path'] and (row['print_location'] or row['omission_reason'])
               for row in contract['field_mappings'])
    decisions = get_scope_decisions()
    assert set(decisions) == {f'C{i:02}' for i in range(1, 11)} | {'GOV-01'}
    for key in ('C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'GOV-01'):
        decision = decisions[key]
        assert decision['ratified_date'] == '2026-11-19'
        assert decision['observed_behavior'] != decision['decision_text']
        assert decision['actor_or_source']
    governance = contract['governance']
    assert governance['employer_acceptance_representative'] is None
    assert governance['employer_acceptance_date'] is None
    assert governance['employer_acceptance_owner_package'] == 'B06'
    assert len(contract['deliverables_scope']) == 4
    assert set(row['id'] for row in contract['cross_phase_boundaries']) == {
        'X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X08', 'X09', 'X10',
    }


@pytest.fixture
def reference_report(db):
    from django.core.management import call_command
    from field_reports.models import DailyReport

    call_command('seed_a1_reference_fixture')
    return DailyReport.objects.get(project__project_code='SIM-A1-001')


def test_seed_is_idempotent_and_scoped(reference_report, project):
    from django.core.management import call_command
    from field_reports.models import DailyReport, WeatherLog

    report = reference_report
    assert report.is_synthetic_reference
    assert report.shift == 'full'
    assert report.project.project_name.startswith('[SYNTHETIC A.1 REFERENCE]')
    assert report.project.start_date == date(2027, 5, 11)
    assert report.report_date == date(2027, 5, 22)
    activity_ids = set(report.activities.values_list('pk', flat=True))
    labor_ids = set(report.labor_entries.values_list('pk', flat=True))
    call_command('seed_a1_reference_fixture')
    assert DailyReport.objects.filter(project=report.project).count() == 1
    assert not DailyReport.objects.filter(project=project).exists()
    assert len(activity_ids) == 5 and set(report.activities.values_list('pk', flat=True)) == activity_ids
    assert len(labor_ids) == 68 and set(report.labor_entries.values_list('pk', flat=True)) == labor_ids
    assert WeatherLog.objects.filter(project=report.project).count() == 1
    report.activities.filter(quantity='12.50').update(quantity='100')
    call_command('seed_a1_reference_fixture', reset=True)
    assert report.activities.filter(quantity='12.50').exists()


def test_seed_refuses_existing_non_fixture_project(db):
    from django.core.management import call_command
    from django.core.management.base import CommandError
    from projects.models import Project

    project = Project.objects.create(project_code='SIM-A1-001', project_name='Existing project')
    with pytest.raises(CommandError):
        call_command('seed_a1_reference_fixture', reset=True)
    project.refresh_from_db()
    assert project.project_name == 'Existing project'
    assert not project.daily_reports.exists()


def test_contract_permissions_and_query_params(api_client, user, other_user, project):
    path = f'/api/v1/projects/{project.pk}/daily-reports/contract/'
    assert api_client.get(path).status_code == 401
    api_client.force_authenticate(other_user)
    assert api_client.get(path).status_code == 403
    from master_data.models import ProjectMember

    ProjectMember.objects.create(project=project, user=other_user, status='active')
    assert api_client.get(path).status_code == 403
    api_client.force_authenticate(user)
    response = api_client.get(path, {'include_mappings': 'false', 'profile': 'shiraz-34-32-v1'})
    assert response.status_code == 200
    assert 'field_mappings' not in response.data
    assert len(response.data['scope_decisions']) == 11
    assert list(response.data['form_profiles']) == ['shiraz-34-32-v1']
    assert api_client.get(path, {'profile': 'missing'}).status_code == 400
    assert api_client.get(path, {'include_mappings': 'perhaps'}).status_code == 400
    assert api_client.post(path).status_code == 405


def test_measured_zero_and_unknown_are_distinct(reference_report):
    from decimal import Decimal
    from django.core.exceptions import ValidationError
    from field_reports.services.data_contract import summarize_activity_quantities, validate_positive_only_metric

    rows = reference_report.activities.all()
    assert rows.filter(quantity=0, quantity_measured=True).count() == 2
    assert rows.filter(quantity__isnull=True, quantity_measured=True).count() == 1
    assert rows.filter(quantity_measured=False).count() == 1
    assert summarize_activity_quantities(rows) == {
        'total': Decimal('12.50'), 'unrecorded_count': 2,
    }
    assert summarize_activity_quantities(rows.filter(quantity__isnull=True)) == {
        'total': None, 'unrecorded_count': 2,
    }
    for invalid in (0, -1):
        with pytest.raises(ValidationError):
            validate_positive_only_metric(invalid)


def test_canonical_shifts_and_actual_duration(reference_report):
    from decimal import Decimal
    from django.core.exceptions import ValidationError
    from field_reports.models import DailyReportWorkedShift
    from field_reports.services.data_contract import normalize_canonical_shift_id, validate_labor_metric_label
    from field_reports.services.man_hours import compute_actual_person_hours

    for number in range(1, 4):
        assert normalize_canonical_shift_id(number) == number
        assert normalize_canonical_shift_id(str(number)) == number
        assert normalize_canonical_shift_id(f'shift_{number}') == number
    for invalid in ('4', 'day', True, 1.5, None, ['1']):
        with pytest.raises(ValidationError):
            normalize_canonical_shift_id(invalid)
    assert reference_report.canonical_worked_shift_ids == [1, 3]
    assert compute_actual_person_hours(2, Decimal('8.50')) == Decimal('17.00')
    assert compute_actual_person_hours(2, None) is None
    assert compute_actual_person_hours(None, Decimal('8.50')) is None
    for invalid in (0, -1, 25):
        with pytest.raises(ValidationError):
            DailyReportWorkedShift(report=reference_report, shift_id=2, actual_duration_hours=invalid).full_clean()
    for label in ('headcount', 'person_days'):
        with pytest.raises(ValidationError):
            validate_labor_metric_label(label, has_unique_attendance_proof=False)
    assert validate_labor_metric_label('person_shifts', has_unique_attendance_proof=False)['label_fa'] == 'نفر-شیفت'


def test_form_profile_has_fixed_slots_and_preserves_appendix(reference_report):
    from field_reports.services.form_profiles import resolve_labor_rows_for_profile
    from project_templates.models import LaborTitleCatalog

    before = list(reference_report.labor_entries.order_by('pk').values())
    catalogs = list(LaborTitleCatalog.objects.order_by('pk').values())
    result = resolve_labor_rows_for_profile(reference_report.labor_entries.all())
    assert len(result['standard_indirect']) == 34
    assert len(result['standard_direct']) == 32
    assert all(slot['rows'] for slot in result['standard_indirect'] + result['standard_direct'])
    assert [row.custom_title for row in result['appendix_indirect']] == ['هماهنگ‌کننده پایش کارگاه']
    assert [row.job_title for row in result['appendix_direct']] == ['کمک راننده قدیمی']
    assert list(reference_report.labor_entries.order_by('pk').values()) == before
    assert list(LaborTitleCatalog.objects.order_by('pk').values()) == catalogs


def test_numbering_observed_weather_and_summary(reference_report, api_client, user, other_user, project, monkeypatch):
    from field_reports.models import DailyReport
    from field_reports.services import weather_forecast
    from field_reports.services.data_contract import compute_official_report_number
    from master_data.models import ProjectMember, ProjectMemberRole

    report = reference_report
    assert report.project_day_number == 12
    assert report.official_report_number == 'SIM-A1-001-12-1406-03-01'
    for start in (None, date(2027, 5, 23)):
        result = compute_official_report_number('SIM-A1-001', start, report.report_date)
        assert result['status'] == 'unknown'
        assert result['project_day'] is None and result['official_report_number'] is None
    own_member = ProjectMember.objects.get(project=project, user=user)
    reference_member = ProjectMember.objects.create(project=report.project, user=user, status='active')
    for role_id in own_member.member_roles.values_list('role_id', flat=True):
        ProjectMemberRole.objects.create(member=reference_member, role_id=role_id)
    path = f'/api/v1/projects/{report.project_id}/daily-reports/{report.pk}/contract-summary/'
    assert api_client.get(path).status_code == 401
    api_client.force_authenticate(other_user)
    assert api_client.get(path).status_code == 403
    api_client.force_authenticate(user)
    wrong_path = f'/api/v1/projects/{project.pk}/daily-reports/{report.pk}/contract-summary/'
    assert api_client.get(wrong_path).status_code == 404
    monkeypatch.setattr(weather_forecast, '_today', lambda: date(2026, 11, 19))
    monkeypatch.setattr(weather_forecast, 'urlopen', lambda *args, **kwargs: pytest.fail('No forecast for fixture date'))
    response = api_client.get(path)
    assert response.status_code == 200
    data = response.data
    assert data['contract_version'] == '1.0.0'
    assert data['official_numbering']['official_report_number'] == report.official_report_number
    assert data['worked_shifts'] == [
        {'shift_id': 1, 'actual_duration_hours': '8.50', 'duration_status': 'recorded',
         'actual_start_at': None, 'actual_end_at': None},
        {'shift_id': 3, 'actual_duration_hours': None, 'duration_status': 'unknown',
         'actual_start_at': None, 'actual_end_at': None},
    ]
    assert data['labor_profile_resolution']['appendix_indirect_count'] == 1
    assert data['labor_profile_resolution']['appendix_direct_count'] == 1
    assert data['weather']['wind_speed'] == '12 km/h NW'
    assert data['weather']['soil_condition'] == 'خشک / Dry'
    assert data['weather']['forecast_status'] == 'unknown'
    assert not data['signature_scope']['pki_digital_signature_claimed']
    assert not data['signature_scope']['whole_body_tamper_seal_claimed']

    by_date = f'/api/v1/projects/{report.project_id}/daily-reports/by-date/'
    assert api_client.get(by_date, {'date': '2027-05-22', 'shift': 'shift_3'}).data['report_id'] == str(report.pk)
    assert api_client.get(by_date, {'date': '2027-05-22', 'shift': '2'}).status_code == 404
    assert api_client.get(by_date, {'date': '2027-05-22', 'shift': '4'}).status_code == 400
    assert DailyReport.objects.filter(project=report.project).count() == 1


def test_forecast_uses_local_days_caches_and_degrades(monkeypatch, settings):
    import io
    import json
    from urllib.error import URLError
    from field_reports.services import weather_forecast

    test_date = date(2027, 5, 22)
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    monkeypatch.setattr(weather_forecast, '_today', lambda: test_date)
    calls = []

    def success(request, timeout):
        assert timeout <= 3
        assert request.headers['User-agent'].startswith('Velora')
        assert 'lat=29.5918' in request.full_url
        calls.append(request.full_url)
        data = {'properties': {'timeseries': [
            {'time': f'2027-05-{day:02}T21:00:00Z', 'data': {
                'instant': {'details': {'air_temperature': day}},
                'next_1_hours': {'summary': {'symbol_code': 'clearsky_night'}},
            }}
            for day in (22, 23, 24)
        ]}}
        response = io.BytesIO(json.dumps(data).encode())
        response.headers = {}
        return response

    monkeypatch.setattr(weather_forecast, 'urlopen', success)
    result = weather_forecast.get_three_day_forecast('29.591899', '52.583700', report_date=test_date)
    assert result['status'] == 'ok'
    assert [day['date'] for day in result['days']] == ['2027-05-23', '2027-05-24', '2027-05-25']
    assert weather_forecast.get_three_day_forecast('29.591899', '52.583700', report_date=test_date) == result
    assert len(calls) == 1
    assert weather_forecast.get_three_day_forecast(None, 1, report_date=test_date)['status'] == 'unknown'

    def offline(*args, **kwargs):
        raise URLError('offline')

    monkeypatch.setattr(weather_forecast, 'urlopen', offline)
    result = weather_forecast.get_three_day_forecast(0, 0, report_date=test_date)
    assert result['status'] == 'unknown' and result['days'] == []


def test_legacy_summary_warns_without_merging_reports(auth_client, user, project):
    from field_reports.models import DailyReport

    reports = [
        DailyReport.objects.create(project=project, created_by=user, report_date=date(2027, 5, 22), shift=shift)
        for shift in ('day', 'night')
    ]
    for report in reports:
        path = f'/api/v1/projects/{project.pk}/daily-reports/{report.pk}/contract-summary/'
        response = auth_client.get(path)
        assert response.status_code == 200
        assert response.data['warnings'] == ['multiple_current_legacy_reports_for_date']
        assert response.data['official_numbering']['official_report_number'] is None
        assert response.data['worked_shifts'] == []
        assert response.data['weather']['observed_status'] == 'unknown'
        assert response.data['weather']['wind_speed'] is None
    assert list(DailyReport.objects.filter(project=project).order_by('shift').values_list('pk', flat=True)) == [
        report.pk for report in reports
    ]

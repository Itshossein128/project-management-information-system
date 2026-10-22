"""Focused test suite for GAP-SPEC-01 / Spec 030 Daily Report Header and Weather Controls."""
import pytest
from decimal import Decimal
from rest_framework import status

from field_reports.models import (
    DailyReport,
    WeatherCondition,
    SiteStatus,
    InactivityReason,
    WeatherLog,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    make_sub_report,
)
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary, rebuild_daily_report_summary
from sub_reports.models import Discipline, DisciplineSubReport, SubReportStatus


@pytest.fixture
def by_date_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/by-date/'


@pytest.fixture
def detail_url_factory(project):
    def _url(report_id):
        return f'/api/v1/projects/{project.id}/daily-reports/{report_id}/'
    return _url


@pytest.mark.django_db
def test_weather_condition_five_standard_choices_accepted(auth_client, by_date_url, detail_url_factory):
    # Ensure report
    res = auth_client.post(by_date_url, {'date': '2026-09-01'}, format='json')
    report_id = res.data['report_id']

    for condition in ('clear', 'cloudy', 'rainy', 'snowy', 'stormy'):
        patch_res = auth_client.patch(detail_url_factory(report_id), {'weather_condition': condition}, format='json')
        assert patch_res.status_code == status.HTTP_200_OK
        assert patch_res.data['weather_condition'] == condition


@pytest.mark.django_db
def test_retired_weather_conditions_rejected(auth_client, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-02'}, format='json')
    report_id = res.data['report_id']

    for retired in ('sunny', 'partly_cloudy', 'foggy', 'tornado'):
        patch_res = auth_client.patch(detail_url_factory(report_id), {'weather_condition': retired}, format='json')
        assert patch_res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_temperature_inclusive_boundaries_accepted(auth_client, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-03'}, format='json')
    report_id = res.data['report_id']

    patch_res = auth_client.patch(
        detail_url_factory(report_id),
        {'temp_min': -40.0, 'temp_max': 60.0},
        format='json',
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert float(patch_res.data['temp_min']) == -40.0
    assert float(patch_res.data['temp_max']) == 60.0


@pytest.mark.django_db
def test_temperature_out_of_bounds_rejected(auth_client, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-04'}, format='json')
    report_id = res.data['report_id']

    low_res = auth_client.patch(detail_url_factory(report_id), {'temp_min': -40.1}, format='json')
    assert low_res.status_code == status.HTTP_400_BAD_REQUEST

    high_res = auth_client.patch(detail_url_factory(report_id), {'temp_max': 60.1}, format='json')
    assert high_res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_daily_report_full_clean_temperature_bounds(project, user):
    from django.core.exceptions import ValidationError as DjangoValidationError
    report = DailyReport(
        project=project,
        report_date='2026-09-08',
        temp_min=Decimal('-40.5'),
        temp_max=Decimal('60.5'),
        created_by=user,
        updated_by=user,
    )
    with pytest.raises(DjangoValidationError) as exc:
        report.full_clean()
    err_dict = exc.value.message_dict
    assert 'temp_min' in err_dict
    assert 'temp_max' in err_dict


@pytest.mark.django_db
def test_temp_max_less_than_temp_min_full_and_partial_patch_rejected(auth_client, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-05'}, format='json')
    report_id = res.data['report_id']

    # Full payload: temp_max < temp_min
    bad_res = auth_client.patch(
        detail_url_factory(report_id),
        {'temp_min': 20.0, 'temp_max': 10.0},
        format='json',
    )
    assert bad_res.status_code == status.HTTP_400_BAD_REQUEST
    err = bad_res.data.get('error', {})
    code = bad_res.data.get('code') or err.get('code')
    details = bad_res.data.get('details') or err.get('details', {})
    assert code == 'temp_max_must_be_gte_temp_min'
    assert 'temp_max' in details

    # Save valid initial values
    good_res = auth_client.patch(
        detail_url_factory(report_id),
        {'temp_min': 15.0, 'temp_max': 25.0},
        format='json',
    )
    assert good_res.status_code == status.HTTP_200_OK

    # Partial patch: update only temp_max to lower than stored temp_min (15.0)
    partial_max_res = auth_client.patch(
        detail_url_factory(report_id),
        {'temp_max': 10.0},
        format='json',
    )
    assert partial_max_res.status_code == status.HTTP_400_BAD_REQUEST
    err = partial_max_res.data.get('error', {})
    code = partial_max_res.data.get('code') or err.get('code')
    details = partial_max_res.data.get('details') or err.get('details', {})
    assert code == 'temp_max_must_be_gte_temp_min'
    assert 'temp_max' in details

    # Partial patch: update only temp_min to higher than stored temp_max (25.0)
    partial_min_res = auth_client.patch(
        detail_url_factory(report_id),
        {'temp_min': 30.0},
        format='json',
    )
    assert partial_min_res.status_code == status.HTTP_400_BAD_REQUEST
    err = partial_min_res.data.get('error', {})
    code = partial_min_res.data.get('code') or err.get('code')
    details = partial_min_res.data.get('details') or err.get('details', {})
    assert code == 'temp_max_must_be_gte_temp_min'
    assert 'temp_max' in details


@pytest.mark.django_db
def test_aggregation_weather_severity_order(project, user):
    d = SUMMARY_DATE
    # Specialty reports with varying weather: rainy, stormy, cloudy
    make_sub_report(project, user, discipline=Discipline.CIVIL, weather_condition='rainy', status=SubReportStatus.SUBMITTED, report_date=d)
    make_sub_report(project, user, discipline=Discipline.ELECTRICAL, weather_condition='stormy', status=SubReportStatus.SUBMITTED, report_date=d)
    make_sub_report(project, user, discipline=Discipline.MECHANICAL, weather_condition='cloudy', status=SubReportStatus.SUBMITTED, report_date=d)

    summary = ensure_daily_report_summary(project.id, d, user=user)
    # Most severe is stormy
    assert summary.weather_condition == 'stormy'

    # Project override preserves explicit project value
    summary.weather_override = True
    summary.weather_condition = 'clear'
    summary.save()

    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.weather_condition == 'clear'


@pytest.mark.django_db
def test_aggregation_weather_blanks_and_unknowns_ignored(project, user):
    d = SUMMARY_DATE
    make_sub_report(project, user, discipline=Discipline.CIVIL, weather_condition='', status=SubReportStatus.SUBMITTED, report_date=d)
    make_sub_report(project, user, discipline=Discipline.ELECTRICAL, weather_condition='unknown_tornado', status=SubReportStatus.SUBMITTED, report_date=d)
    make_sub_report(project, user, discipline=Discipline.MECHANICAL, weather_condition='clear', status=SubReportStatus.SUBMITTED, report_date=d)

    summary = ensure_daily_report_summary(project.id, d, user=user)
    assert summary.weather_condition == 'clear'


@pytest.mark.django_db
def test_aggregation_weather_no_valid_contributors_clears_derived(project, user):
    d = SUMMARY_DATE
    sub = make_sub_report(project, user, discipline=Discipline.CIVIL, weather_condition='clear', status=SubReportStatus.SUBMITTED, report_date=d)

    summary = ensure_daily_report_summary(project.id, d, user=user)
    assert summary.weather_condition == 'clear'

    # Now sub-report weather is cleared
    sub.weather_condition = ''
    sub.save()

    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.weather_condition is None


@pytest.mark.django_db
def test_aggregation_weather_all_severity_pairs(project, user):
    d = SUMMARY_DATE
    sub1 = make_sub_report(project, user, discipline=Discipline.CIVIL, weather_condition='clear', status=SubReportStatus.SUBMITTED, report_date=d)
    sub2 = make_sub_report(project, user, discipline=Discipline.ELECTRICAL, weather_condition='cloudy', status=SubReportStatus.SUBMITTED, report_date=d)

    summary = ensure_daily_report_summary(project.id, d, user=user)
    assert summary.weather_condition == 'cloudy'

    sub1.weather_condition = 'rainy'
    sub1.save()
    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.weather_condition == 'rainy'

    sub2.weather_condition = 'snowy'
    sub2.save()
    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.weather_condition == 'snowy'

    sub1.weather_condition = 'stormy'
    sub1.save()
    rebuilt = rebuild_daily_report_summary(project.id, d, user=user, report=summary)
    assert rebuilt.weather_condition == 'stormy'


@pytest.mark.django_db
def test_inactivity_reason_validation_and_clearing(auth_client, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-05'}, format='json')
    report_id = res.data['report_id']

    # Inactive without reason -> 400 with inactivity_reason_required
    for bad_reason in ('', None):
        fail_res = auth_client.patch(
            detail_url_factory(report_id),
            {'site_status': 'inactive', 'inactivity_reason': bad_reason},
            format='json',
        )
        assert fail_res.status_code == status.HTTP_400_BAD_REQUEST
        err = fail_res.data.get('error', {})
        code = fail_res.data.get('code') or err.get('code')
        details = fail_res.data.get('details') or err.get('details', {})
        assert code == 'inactivity_reason_required' or 'inactivity_reason' in details

    # Invalid reason string -> 400
    bad_val_res = auth_client.patch(
        detail_url_factory(report_id),
        {'site_status': 'inactive', 'inactivity_reason': 'alien_invasion'},
        format='json',
    )
    assert bad_val_res.status_code == status.HTTP_400_BAD_REQUEST

    # All five valid reasons accepted
    for reason in ('weather', 'holiday', 'strike_or_dispute', 'client_stop_order', 'safety_incident'):
        ok_res = auth_client.patch(
            detail_url_factory(report_id),
            {'site_status': 'inactive', 'inactivity_reason': reason},
            format='json',
        )
        assert ok_res.status_code == status.HTTP_200_OK
        assert ok_res.data['site_status'] == 'inactive'
        assert ok_res.data['inactivity_reason'] == reason

    # Active clears inactivity_reason
    active_res = auth_client.patch(
        detail_url_factory(report_id),
        {'site_status': 'active', 'inactivity_reason': 'weather'},
        format='json',
    )
    assert active_res.status_code == status.HTTP_200_OK
    assert active_res.data['site_status'] == 'active'
    assert active_res.data['inactivity_reason'] in ('', None)


@pytest.mark.django_db
def test_lifecycle_transitions_reject_inactive_without_reason(auth_client, project, by_date_url):
    res = auth_client.post(by_date_url, {'date': '2026-09-06'}, format='json')
    report_id = res.data['report_id']

    # Put in inactive with empty reason directly in DB
    DailyReport.objects.filter(id=report_id).update(
        site_status=SiteStatus.INACTIVE,
        inactivity_reason='',
    )

    base = f'/api/v1/projects/{project.id}/daily-reports/{report_id}'

    # Submit fails
    submit_res = auth_client.post(f'{base}/submit/', format='json')
    assert submit_res.status_code == status.HTTP_400_BAD_REQUEST
    err = submit_res.data.get('error', {})
    code = submit_res.data.get('code') or err.get('code')
    details = submit_res.data.get('details') or err.get('details', {})
    assert code == 'inactivity_reason_required' or 'inactivity_reason' in details

    # Transition to SUBMITTED directly
    from field_reports.models import ReportStatus
    DailyReport.objects.filter(id=report_id).update(status=ReportStatus.SUBMITTED)

    # Review fails
    review_res = auth_client.post(f'{base}/review/', format='json')
    assert review_res.status_code == status.HTTP_400_BAD_REQUEST
    err = review_res.data.get('error', {})
    code = review_res.data.get('code') or err.get('code')
    details = review_res.data.get('details') or err.get('details', {})
    assert code == 'inactivity_reason_required' or 'inactivity_reason' in details

    # Approve fails
    approve_res = auth_client.post(f'{base}/approve/', format='json')
    assert approve_res.status_code == status.HTTP_400_BAD_REQUEST
    err = approve_res.data.get('error', {})
    code = approve_res.data.get('code') or err.get('code')
    details = approve_res.data.get('details') or err.get('details', {})
    assert code == 'inactivity_reason_required' or 'inactivity_reason' in details


@pytest.mark.django_db
def test_weather_impact_notes_persistence_and_rebuild_preservation(auth_client, project, user, by_date_url, detail_url_factory):
    res = auth_client.post(by_date_url, {'date': '2026-09-10'}, format='json')
    report_id = res.data['report_id']

    notes = 'به علت بارندگی شدید و گل‌آلود بودن کارگاه، تردد ماشین‌آلات سنگین متوقف شد. Heavy rain halted heavy machinery.'
    patch_res = auth_client.patch(
        detail_url_factory(report_id),
        {'weather_impact_notes': notes},
        format='json',
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.data['weather_impact_notes'] == notes

    get_res = auth_client.get(detail_url_factory(report_id))
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.data['weather_impact_notes'] == notes

    # Summary rebuild preserves weather_impact_notes
    from datetime import date
    rebuilt = rebuild_daily_report_summary(
        project.id,
        date(2026, 9, 10),
        user=user,
        report=DailyReport.objects.get(id=report_id),
    )
    assert rebuilt.weather_impact_notes == notes


@pytest.mark.django_db
def test_pdf_export_contains_weather_impact_notes_and_inactivity_reason(project, user):
    import subprocess
    from field_reports.models import ReportStatus
    from field_reports.pdf import generate_daily_report_pdf

    report = DailyReport.objects.create(
        project=project,
        report_date='2026-09-11',
        shift='full',
        status=ReportStatus.APPROVED,
        site_status=SiteStatus.INACTIVE,
        inactivity_reason=InactivityReason.WEATHER,
        weather_impact_notes='Wind speed exceeded 70km/h causing crane stoppage',
        created_by=user,
        updated_by=user,
    )
    pdf_bytes, filename = generate_daily_report_pdf(report)
    assert pdf_bytes.startswith(b'%PDF')

    proc = subprocess.run(['pdftotext', '-', '-'], input=pdf_bytes, capture_output=True)
    import unicodedata
    text = unicodedata.normalize('NFKD', proc.stdout.decode('utf-8', errors='ignore'))
    assert 'Wind speed exceeded 70km/h causing crane stoppage' in text
    assert 'نامساعد بودن شرایط جوی' in text or 'غیرفعال' in text


@pytest.mark.django_db
def test_inactivity_reason_partial_update_edge_cases(auth_client, project, by_date_url, detail_url_factory):
    # Setup: create report and set inactive with weather reason
    res = auth_client.post(by_date_url, {'date': '2026-09-12'}, format='json')
    report_id = res.data['report_id']

    setup_res = auth_client.patch(
        detail_url_factory(report_id),
        {'site_status': 'inactive', 'inactivity_reason': 'weather'},
        format='json',
    )
    assert setup_res.status_code == status.HTTP_200_OK
    assert setup_res.data['site_status'] == 'inactive'
    assert setup_res.data['inactivity_reason'] == 'weather'

    # (a) PATCH changing only site_status to inactive without sending inactivity_reason -> passes using stored reason
    patch_status_res = auth_client.patch(
        detail_url_factory(report_id),
        {'site_status': 'inactive'},
        format='json',
    )
    assert patch_status_res.status_code == status.HTTP_200_OK
    assert patch_status_res.data['site_status'] == 'inactive'
    assert patch_status_res.data['inactivity_reason'] == 'weather'

    # (b) PATCH changing only inactivity_reason:
    # invalid/empty new value rejected with inactivity_reason_required
    for bad_val in ('', None):
        bad_reason_res = auth_client.patch(
            detail_url_factory(report_id),
            {'inactivity_reason': bad_val},
            format='json',
        )
        assert bad_reason_res.status_code == status.HTTP_400_BAD_REQUEST
        err = bad_reason_res.data.get('error', {})
        code = bad_reason_res.data.get('code') or err.get('code')
        details = bad_reason_res.data.get('details') or err.get('details', {})
        assert code == 'inactivity_reason_required' or 'inactivity_reason' in details

    # valid new value accepted
    valid_reason_res = auth_client.patch(
        detail_url_factory(report_id),
        {'inactivity_reason': 'holiday'},
        format='json',
    )
    assert valid_reason_res.status_code == status.HTTP_200_OK
    assert valid_reason_res.data['inactivity_reason'] == 'holiday'

    # (c) active-state clearing of a stale reason on partial update (SC-003)
    active_patch_res = auth_client.patch(
        detail_url_factory(report_id),
        {'site_status': 'active'},
        format='json',
    )
    assert active_patch_res.status_code == status.HTTP_200_OK
    assert active_patch_res.data['site_status'] == 'active'
    assert active_patch_res.data['inactivity_reason'] in ('', None)

    # Verify reload from DB
    report = DailyReport.objects.get(id=report_id)
    assert report.site_status == 'active'
    assert report.inactivity_reason == ''




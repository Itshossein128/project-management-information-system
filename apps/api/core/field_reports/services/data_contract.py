"""Versioned Phase A.1 daily report contract and decision register."""
from collections.abc import Mapping
from copy import deepcopy
from datetime import date
from functools import lru_cache
import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.unset import coerce_optional_decimal

CONTRACT_VERSION = '1.0.0'
CONTRACT_PATH = Path(__file__).resolve().parents[1] / 'contracts' / 'daily_report_contract_v1.json'
SCOPE_DECISIONS = {f'C{i:02}' for i in range(1, 11)} | {'GOV-01'}
RATIFIED_DECISIONS = {f'C{i:02}' for i in range(3, 9)} | {'GOV-01'}
INCIDENT_LABELS_FA = {
    'safety': 'ایمنی', 'quality': 'کیفیت', 'environmental': 'محیط زیست',
    'stoppage': 'توقف کار', 'visitor': 'بازدیدکننده', 'site_instruction': 'دستور کارگاهی',
    'barrier': 'مانع', 'issue': 'مسئله',
}
SEVERITY_LABELS_FA = {'minor': 'جزئی', 'moderate': 'متوسط', 'major': 'شدید'}
SECTION_NUMBERS = set(range(1, 19))
DISPOSITIONS = {
    'printed_in_a1', 'printed_in_a1_and_drill_down', 'printed_in_a1_and_deferred_owner',
    'deferred_to_owner_phase', 'drill_down_in_a1',
}
ZERO_UNSET_RULES = {
    'measured_zero_valid_null_unknown', 'positive_only_domain_rule', 'unknown_when_missing', 'text_optional',
}


def _require(condition, description):
    if not condition:
        raise ValueError(f'Invalid daily report contract: {description}')


def _index_scope_decisions(contract):
    rows = contract['scope_decisions']
    indexed = {row['id']: row for row in rows}
    _require(len(rows) == len(indexed) and indexed.keys() == SCOPE_DECISIONS, 'scope decision IDs')
    for code, row in indexed.items():
        _require(all(row[key] for key in (
            'topic', 'status', 'observed_behavior', 'decision_text', 'actor_or_source', 'linked_requirements',
        )) and row['observed_behavior'] != row['decision_text'], f'{code} decision provenance')
        if code in RATIFIED_DECISIONS:
            status = 'ratified_internal_scope' if code == 'GOV-01' else 'ratified'
            _require(row['status'] == status and row['ratified_date'] == '2026-11-19'
                     and row['actor_or_source'] == '385da9f5-52d9-4f26-bb09-fc125283cf94',
                     f'{code} ratification')
    for code, status in {'C01': 'baseline_recorded', 'C02': 'baseline_recorded',
                         'C09': 'baseline_preserved', 'C10': 'boundary_preserved'}.items():
        _require(indexed[code]['status'] == status, f'{code} baseline status')
    return indexed


def validate_daily_report_contract(contract):
    _require(contract['contract_version'] == CONTRACT_VERSION, 'contract version')
    _require(contract['reference_form_version'] == 'shiraz-file4-v1', 'reference form version')
    fixture = contract['reference_day_fixture']
    expected = {
        'project_code': 'SIM-A1-001', 'gregorian_date': '2027-05-22', 'jalali_date': '1406-03-01',
        'gregorian_actual_start_date': '2027-05-11', 'jalali_actual_start_date': '1406-02-21',
        'project_day': 12, 'official_report_number': 'SIM-A1-001-12-1406-03-01',
    }
    _require(all(fixture[key] == value for key, value in expected.items())
             and fixture['is_synthetic'] is True and fixture['legacy_unlabeled_samples_excluded'] is True
             and fixture['synthetic_label'], 'synthetic reference metadata')
    governance = contract['governance']
    _require(governance['employer_acceptance_representative'] is None
             and governance['employer_acceptance_date'] is None
             and governance['employer_acceptance_status'] == 'pending_b06_handoff'
             and governance['employer_acceptance_owner_package'] == 'B06'
             and governance['internal_decision_date'] == '2026-11-19'
             and governance['internal_decision_owner'] and governance['internal_verification_owner'],
             'GOV-01 and pending B06 handoff')
    history = contract['revision_history']
    _require(history and history[-1]['version'] == CONTRACT_VERSION and all(
        all(entry[key] for key in ('version', 'date', 'author', 'summary')) for entry in history
    ), 'revision history')
    sections = contract['broader_sections']
    _require(len(sections) == len(SECTION_NUMBERS)
             and {row['section_number'] for row in sections} == SECTION_NUMBERS
             and all(row['disposition'] in DISPOSITIONS and row['owner_phase']
                     and row['name_en'] and row['name_fa'] for row in sections), '18-section dispositions')
    mappings = contract['field_mappings']
    _require({row['section_number'] for row in mappings} == SECTION_NUMBERS
             and len({row['field_id'] for row in mappings}) == len(mappings), 'unique field mappings for all sections')
    for row in mappings:
        _require(all(row[key] for key in (
            'field_id', 'label_en', 'label_fa', 'source_document', 'source_field_or_cell',
            'conversion_rule', 'drill_down_path',
        )) and 'unit' in row and row['zero_unset_rule'] in ZERO_UNSET_RULES
                 and bool(row['print_location']) != bool(row['omission_reason']),
                 f"{row['field_id']} field mapping")
    profile = contract['form_profiles']['shiraz-34-32-v1']
    for category, count in (('indirect', 34), ('direct', 32)):
        slots = profile[f'{category}_slots']
        _require(len(slots) == len(set(slots)) == profile[f'{category}_slot_count'] == count
                 and all(slots), f'Shiraz {category} slots')
    _require(profile['appendix_heading_en'] and profile['appendix_heading_fa'], 'bilingual appendix headings')
    _index_scope_decisions(contract)


@lru_cache(maxsize=1)
def _read_contract():
    with CONTRACT_PATH.open(encoding='utf-8') as source:
        contract = json.load(source)
    validate_daily_report_contract(contract)
    return contract


def load_daily_report_contract(version=CONTRACT_VERSION):
    if version != CONTRACT_VERSION:
        raise ValidationError(_('Unsupported daily report contract version.'))
    return deepcopy(_read_contract())


def get_scope_decisions(version=CONTRACT_VERSION):
    return _index_scope_decisions(load_daily_report_contract(version))


def summarize_activity_quantities(activities):
    """Summarize rows of the same unit, keeping an entirely unknown total unset."""
    total = None
    unrecorded_count = 0
    for activity in activities:
        if isinstance(activity, Mapping):
            quantity, measured = activity.get('quantity'), activity.get('quantity_measured')
        else:
            quantity, measured = activity.quantity, activity.quantity_measured
        recorded = coerce_optional_decimal(quantity) if measured is not False else None
        if recorded is None or not recorded.is_finite():
            unrecorded_count += 1
        else:
            total = recorded if total is None else total + recorded
    return {'total': total, 'unrecorded_count': unrecorded_count}


def validate_positive_only_metric(value):
    try:
        metric = coerce_optional_decimal(value)
    except ValueError as exc:
        raise ValidationError(_('Enter a positive recorded measurement.')) from exc
    if metric is None or not metric.is_finite() or metric <= 0:
        raise ValidationError(_('Enter a positive recorded measurement.'))
    return metric


_CANONICAL_SHIFTS = {'1': 1, '2': 2, '3': 3, 'shift_1': 1, 'shift_2': 2, 'shift_3': 3}


def normalize_canonical_shift_id(raw_shift):
    if isinstance(raw_shift, (int, str)) and not isinstance(raw_shift, bool):
        shift = _CANONICAL_SHIFTS.get(str(raw_shift))
        if shift is not None:
            return shift
    raise ValidationError(_('Use shift 1, 2, or 3.'))


def validate_labor_metric_label(metric_key, *, has_unique_attendance_proof):
    """Validate a requested label for a sum of labor rows."""
    for metric in _read_contract()['labor_metrics']:
        if metric['key'] == metric_key:
            if metric['requires_unique_attendance_proof_for_sum'] and not has_unique_attendance_proof:
                raise ValidationError(_('This labor metric requires unique-worker attendance evidence.'))
            return deepcopy(metric)
    raise ValidationError(_('Unknown labor metric.'))


def compute_official_report_number(project_code, actual_start_date, report_date):
    from common.jalali import gregorian_to_jalali

    if isinstance(actual_start_date, str):
        actual_start_date = date.fromisoformat(actual_start_date) if actual_start_date else None
    jalali_date = gregorian_to_jalali(report_date).replace('/', '-')
    project_day = None
    if actual_start_date is not None and report_date >= actual_start_date:
        project_day = (report_date - actual_start_date).days + 1
    number = f'{project_code}-{project_day}-{jalali_date}' if project_code and project_day is not None else None
    return {
        'project_code': project_code or None,
        'actual_start_date': actual_start_date.isoformat() if actual_start_date is not None else None,
        'report_date_gregorian': report_date.isoformat(),
        'report_date_jalali': jalali_date,
        'project_day': project_day,
        'official_report_number': number,
        'status': 'ok' if number else 'unknown',
    }


def project_report_header(report, *, preview=False):
    """Project header facts and weather evidence for one selected report version."""
    from common.jalali import persian_day_of_week
    from field_reports.models import DailyReport
    from field_reports.services.weather_forecast import PROJECT_TIME_ZONE, report_weather_evidence

    report_date = date.fromisoformat(report.report_date) if isinstance(report.report_date, str) else report.report_date
    project = report.project
    numbering = compute_official_report_number(project.project_code, project.start_date, report_date)
    warnings = []
    if not report.contract_version:
        legacy_ids = DailyReport.objects.filter(
            project_id=report.project_id, report_date=report_date, is_current=True, contract_version='',
        ).values_list('pk', flat=True)[:2]
        if len(legacy_ids) > 1:
            numbering.update(official_report_number=None, status='unknown')
            warnings.append('multiple_current_legacy_reports_for_date')

    preparer = report.prepared_by
    return {
        'project_name': project.project_name,
        'contract_number': project.contract_number or None,
        'prepared_by_name': preparer.get_full_name() if preparer else None,
        'report_date': numbering['report_date_jalali'].replace('-', '/'),
        'day_of_week': persian_day_of_week(report_date),
        'official_numbering': numbering,
        'worked_shifts': [
            {
                'shift_id': shift.shift_id,
                'actual_start_at': _local_timestamp(shift.actual_start_at, PROJECT_TIME_ZONE),
                'actual_end_at': _local_timestamp(shift.actual_end_at, PROJECT_TIME_ZONE),
                'actual_duration_hours': (
                    str(shift.actual_duration_hours) if shift.actual_duration_hours is not None else None
                ),
                'duration_status': 'unknown' if shift.actual_duration_hours is None else 'recorded',
            }
            for shift in report.worked_shifts.all()
        ],
        'weather': report_weather_evidence(report, preview=preview),
        'weather_condition': report.weather_condition,
        'temp_min': report.temp_min,
        'temp_max': report.temp_max,
        'weather_override': report.weather_override,
        'weather_impact_notes': report.weather_impact_notes,
        'site_status': report.site_status,
        'inactivity_reason': report.inactivity_reason or None,
        'warnings': warnings,
    }


def _local_timestamp(value, timezone):
    return value.astimezone(timezone).isoformat() if value is not None else None


def format_worked_shift(shift, *, english=False):
    from datetime import datetime

    from common.jalali import gregorian_to_jalali

    def display_time(value):
        if value is None:
            return '—'
        timestamp = datetime.fromisoformat(value)
        return f"{gregorian_to_jalali(timestamp.date())} {timestamp:%H:%M}"

    start = display_time(shift['actual_start_at'])
    end = display_time(shift['actual_end_at'])
    hours = shift['actual_duration_hours'] or '—'
    if english:
        return f"Shift {shift['shift_id']}: start {start}, end {end}, duration {hours} h"
    return f"شیفت {shift['shift_id']}، شروع {start}، پایان {end}، مدت {hours} ساعت"


def format_forecast(weather):
    from common.jalali import gregorian_to_jalali

    return '\n'.join(
        f"{gregorian_to_jalali(date.fromisoformat(day['date']))}: {day['air_temperature_c']} °C"
        for day in weather['forecast_days']
    ) or '—'


def sampling_label(value, *, english=False):
    labels = (
        ('Taken', 'Not taken', 'Unknown') if english else ('نمونه‌گیری شده', 'نمونه‌گیری نشده', 'نامشخص')
    )
    return {'sampling_declared': labels[0], 'not_sampled': labels[1]}.get(value, labels[2])


def concrete_details_url(report):
    from django.conf import settings

    return (
        f"{settings.FRONTEND_URL.rstrip('/')}/projects/{report.project_id}/"
        f"daily-reports/{report.pk}/view#summary-section-concrete"
    )

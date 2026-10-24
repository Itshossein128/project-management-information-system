"""Ensure and rebuild project daily-report summaries from specialty sub-reports."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from common.reporting_units import CANONICAL_SPECIALTY_UNITS
from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportDerivedSource,
    DailyReportGeneralActivity,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportMachineryRow,
    DailyReportMaterial,
    DailyReportVisit,
    InactivityReason,
    MaterialTransactionType,
    ReportShift,
    SiteStatus,
    WeatherCondition,
)
from project_templates.models import ProjectReportingConfiguration
from sub_reports.models import (
    DEFAULT_EXPECTED_DISCIPLINES,
    DisciplineSubReport,
    SubReportNoteType,
    SubReportStatus,
)

INCLUDE_STATUSES = {SubReportStatus.SUBMITTED, SubReportStatus.APPROVED}

WEATHER_SEVERITY = {
    WeatherCondition.STORMY: 50,
    WeatherCondition.SNOWY: 40,
    WeatherCondition.RAINY: 30,
    WeatherCondition.CLOUDY: 20,
    WeatherCondition.CLEAR: 10,
}


def contributing_sub_reports(project_id, report_date: date):
    """Return eligible sub-reports contributing to a summary (feature 032, US3).

    Eligibility criteria:
    1. Same project and date.
    2. Valid canonical unit.
    3. is_current=True.
    4. is_deleted=False.
    5. status in {submitted, approved}.
    6. Not quarantined.
    """
    return (
        DisciplineSubReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            is_current=True,
            is_deleted=False,
            status__in=INCLUDE_STATUSES,
        )
        .exclude(migration_traces__quarantine__isnull=False)
        .prefetch_related(
            'activities',
            'labor_entries',
            'machinery_rows',
            'material_entries',
            'concrete_entries',
            'general_activities',
            'issues',
            'visits',
            'hse_incidents',
            'attachments',
            'notes',
            'activity_records',
        )
        .order_by('unit', 'version_number', 'id')
    )


def resolve_project_reporting_configuration(
    project_id, report_date: date,
) -> ProjectReportingConfiguration | None:
    """Resolve latest configuration effective on or before report_date."""
    return (
        ProjectReportingConfiguration.objects.filter(
            project_id=project_id,
            effective_from__lte=report_date,
        )
        .prefetch_related('required_units', 'source_template')
        .order_by('-effective_from')
        .first()
    )


def build_aggregation_meta(
    project_id, report_date: date, report: DailyReport | None = None,
) -> dict:
    config = None
    if report and report.reporting_configuration_id:
        config = report.reporting_configuration
    else:
        config = resolve_project_reporting_configuration(project_id, report_date)

    eligible_reports = list(contributing_sub_reports(project_id, report_date))
    contributing_units = sorted(
        set(sr.unit for sr in eligible_reports if sr.unit and sr.unit in CANONICAL_SPECIALTY_UNITS)
    )

    if config is None:
        completeness_state = 'configuration_incomplete'
        expected_units: list[str] = []
        source_template = None
        configuration_id = None
        missing_units: list[str] = []
    else:
        expected_units = [
            u.unit for u in config.required_units.all().order_by('display_order', 'id')
        ]
        source_template = {
            'id': str(config.source_template_id),
            'name': config.source_template_name_snapshot
            or (config.source_template.template_name if config.source_template else ''),
        }
        configuration_id = str(config.id)
        missing_units = [u for u in expected_units if u not in contributing_units]
        completeness_state = 'complete' if len(missing_units) == 0 else 'partial'

    completeness = {
        'state': completeness_state,
        'configuration_id': configuration_id,
        'source_template': source_template,
        'expected_units': expected_units,
        'contributing_units': contributing_units,
        'missing_units': missing_units,
    }

    # Backward compatibility with legacy disciplines
    expected_disciplines = (
        expected_units if expected_units else [d.value for d in DEFAULT_EXPECTED_DISCIPLINES]
    )
    contributing_disciplines = [
        sr.discipline for sr in eligible_reports if getattr(sr, 'discipline', None)
    ]
    contributing_disciplines = sorted(set(contributing_disciplines))
    missing_disciplines = [
        d for d in expected_disciplines if d not in contributing_disciplines
    ]

    return {
        'is_auto_summary': bool(report.is_auto_summary) if report else True,
        'aggregated_at': report.aggregated_at.isoformat().replace('+00:00', 'Z')
        if report and report.aggregated_at
        else None,
        'is_partial': completeness_state != 'complete',
        'expected_disciplines': expected_disciplines,
        'contributing_disciplines': contributing_disciplines,
        'missing_disciplines': missing_disciplines,
        'completeness': completeness,
        'weather_source': 'override' if report and report.weather_override else 'derived',
        'site_status_source': 'override' if report and report.site_status_override else 'derived',
    }


def _pick_weather(sub_reports) -> str | None:
    best = None
    best_score = -1
    for sr in sub_reports:
        cond = (sr.weather_condition or '').strip()
        if not cond or cond not in WEATHER_SEVERITY:
            continue
        score = WEATHER_SEVERITY[cond]
        if score > best_score:
            best_score = score
            best = cond
    return best


def compute_aggregation_fingerprint(config_id, sub_reports) -> str:
    """Compute a stable deterministic sha256 fingerprint over contributing unit report
    versions, source rows, configuration ID, and aggregation-owned inputs (data-model §7, T050).
    """
    payload = {
        'configuration_id': str(config_id) if config_id else '',
        'sub_reports': [],
    }
    for sr in sub_reports:
        sr_data = {
            'id': str(sr.id),
            'version_number': sr.version_number,
            'unit': sr.unit or sr.discipline or '',
            'status': sr.status,
            'weather_condition': sr.weather_condition or '',
            'site_status': sr.site_status or '',
            'activities': [
                (
                    str(a.id),
                    a.activity_description or '',
                    a.shift or '',
                    a.worker_count,
                    a.foreman_count,
                    a.headcount,
                    str(a.quantity) if a.quantity is not None else '',
                    a.unit or '',
                    str(a.execution_percentage) if a.execution_percentage is not None else '',
                    a.crew_name or '',
                    str(a.contractor_ref_id) if a.contractor_ref_id else '',
                    a.parcel or '',
                    a.zone or '',
                    a.block or '',
                    a.floor or '',
                    a.notes or '',
                )
                for a in sr.activities.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'department_activities': [
                (
                    str(d.id),
                    d.activity_description or '',
                    d.description or '',
                    str(d.quantity_in),
                    str(d.quantity_out),
                    d.unit or '',
                    d.location or '',
                    d.contractor or '',
                    str(d.contractor_ref_id) if d.contractor_ref_id else '',
                )
                for d in sr.activity_records.all().order_by('id')
            ],
            'labor': [
                (
                    str(l.id),
                    l.labor_category,
                    l.job_title,
                    l.present_count,
                    l.leave_count,
                    str(l.overtime_hours) if l.overtime_hours is not None else '0',
                    str(l.contractor_ref_id) if l.contractor_ref_id else '',
                )
                for l in sr.labor_entries.filter(is_deleted=False).order_by('id')
            ],
            'machinery': [
                (
                    str(m.id),
                    m.row_number,
                    m.equipment_type or '',
                    str(m.equipment_ref_id) if m.equipment_ref_id else '',
                    m.status_total,
                    m.status_active,
                    m.status_ready,
                    m.status_inactive,
                    m.status_under_repair,
                    str(m.operating_hours) if m.operating_hours is not None else '',
                    str(m.stoppage_hours) if m.stoppage_hours is not None else '',
                    str(m.repair_hours) if m.repair_hours is not None else '',
                    m.stoppage_reason_code or '',
                )
                for m in sr.machinery_rows.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'materials': [
                (
                    str(m.id),
                    m.transaction_type or '',
                    str(m.material_ref_id) if m.material_ref_id else '',
                    m.material_description,
                    str(m.quantity),
                    m.unit,
                    m.consumption_location or '',
                    m.supplier or '',
                    m.warehouse_document_reference or '',
                    m.notes or '',
                )
                for m in sr.material_entries.filter(is_deleted=False).order_by('id')
            ],
            'concrete': [
                (
                    str(c.id),
                    c.concrete_description,
                    str(c.volume_m3),
                    c.zone or '',
                    c.block or '',
                    c.floor or '',
                    c.notes or '',
                    c.structural_element or '',
                    c.parcel or '',
                    c.batching_plant or '',
                    c.truck_delivery_note_number or '',
                    c.lab_sample_code or '',
                    c.sampling_state or '',
                    c.test_sheet_count if c.test_sheet_count is not None else '',
                    str(c.qc_inspection_id) if c.qc_inspection_id else '',
                )
                for c in sr.concrete_entries.filter(is_deleted=False).order_by('id')
            ],
            'general_activities': [
                (
                    str(g.id),
                    g.row_number,
                    g.activity_description,
                    g.location or '',
                    str(g.quantity) if g.quantity is not None else '',
                    g.unit or '',
                    g.notes or '',
                )
                for g in sr.general_activities.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'issues': [
                (
                    str(i.id),
                    i.row_number,
                    i.kind,
                    i.text,
                    str(i.owner_user_id) if i.owner_user_id else '',
                    str(i.due_date) if i.due_date else '',
                )
                for i in sr.issues.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'visits': [
                (str(v.id), v.row_number, v.text)
                for v in sr.visits.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'hse_incidents': [
                (
                    str(h.id),
                    h.row_number,
                    h.text,
                    h.severity,
                    h.immediate_action,
                )
                for h in sr.hse_incidents.filter(is_deleted=False).order_by('row_number', 'id')
            ],
            'attachments': [
                (str(a.id), a.row_kind, a.row_id, a.checksum, a.size_bytes or 0)
                for a in sr.attachments.filter(is_deleted=False).order_by('id')
            ],
            'notes': [
                (
                    str(n.id),
                    n.note_type,
                    n.text,
                    n.row_number,
                )
                for n in sr.notes.filter(is_deleted=False).order_by('row_number', 'id')
            ],
        }
        payload['sub_reports'].append(sr_data)

    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


@transaction.atomic
def ensure_daily_report_summary(project_id, report_date: date, user=None) -> DailyReport:
    from projects.models import Project

    Project.objects.select_for_update().filter(id=project_id).first()
    report = (
        DailyReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            shift=ReportShift.FULL,
            is_deleted=False,
            is_current=True,
        )
        .order_by('-created_at')
        .first()
    )
    if report is None:
        config = resolve_project_reporting_configuration(project_id, report_date)
        kwargs = {
            'project_id': project_id,
            'report_date': report_date,
            'shift': ReportShift.FULL,
            'is_auto_summary': True,
            'is_current': True,
            'reporting_configuration': config,
        }
        if user is not None:
            kwargs['prepared_by'] = user
            kwargs['created_by'] = user
            kwargs['updated_by'] = user
        report = DailyReport.objects.create(**kwargs)
    elif not report.is_auto_summary:
        report.is_auto_summary = True
        report.save(update_fields=['is_auto_summary', 'updated_at'])
    return rebuild_daily_report_summary(project_id, report_date, user=user, report=report)


def _wash(value) -> str:
    import re
    return re.sub(r'<[^>]*>', '', '' if value is None else str(value)).strip()


def _upsert_provenance(report, sr, kind, derived_id, source_kind, source_id, ordinal, contribution=None):
    DailyReportDerivedSource.objects.update_or_create(
        daily_report=report,
        derived_kind=kind,
        derived_row_id=str(derived_id),
        source_report_id_snapshot=sr.id,
        source_row_kind=source_kind,
        source_row_id=str(source_id),
        defaults={
            'source_report': sr,
            'source_report_version': sr.version_number,
            'source_unit': sr.unit or sr.discipline,
            'contribution_value': contribution,
            'ordinal': ordinal,
        },
    )


def _rebuild_structured_narrative(report, sub_reports):
    """Replace text-encoded narrative with ordered structured rows."""
    from field_reports.services.hse_incident_notifications import ensure_hse_notification

    current_general = set()
    current_visits = set()
    current_incidents = set()

    for sr in sub_reports:
        for row in sr.general_activities.filter(is_deleted=False).order_by('row_number', 'id'):
            obj, _created = DailyReportGeneralActivity.objects.update_or_create(
                report=report,
                source_sub_report=sr,
                row_number=row.row_number,
                defaults={
                    'activity_description': _wash(row.activity_description),
                    'location': _wash(row.location),
                    'quantity': row.quantity,
                    'unit': row.unit,
                    'notes': _wash(row.notes),
                    'source_discipline': sr.unit or sr.discipline,
                    'is_derived': True,
                },
            )
            current_general.add(obj.id)
            _upsert_provenance(
                report, sr, 'general_activity', obj.id, 'general_activity', row.id, row.row_number,
            )

        for row in sr.visits.filter(is_deleted=False).order_by('row_number', 'id'):
            obj, _created = DailyReportVisit.objects.update_or_create(
                report=report,
                source_sub_report=sr,
                row_number=row.row_number,
                defaults={
                    'text': _wash(row.text),
                    'source_discipline': sr.unit or sr.discipline,
                    'is_derived': True,
                },
            )
            current_visits.add(obj.id)
            _upsert_provenance(report, sr, 'visit', obj.id, 'visit', row.id, row.row_number)

        for row in sr.issues.filter(is_deleted=False).order_by('row_number', 'id'):
            incident_type = 'barrier' if row.kind == 'barrier' else 'issue'
            obj, _created = DailyReportIncident.objects.update_or_create(
                report=report,
                source_report=sr,
                source_row_id=str(row.id),
                defaults={
                    'incident_type': incident_type,
                    'description': _wash(row.text),
                    'follow_up_owner_user': row.owner_user,
                    'due_date': row.due_date,
                    'row_number': row.row_number,
                    'severity': None,
                },
            )
            current_incidents.add(obj.id)
            _upsert_provenance(report, sr, 'issue', obj.id, 'issue', row.id, row.row_number)

        for row in sr.hse_incidents.filter(is_deleted=False).order_by('row_number', 'id'):
            note = ensure_hse_notification(row, user=sr.created_by)
            obj, _created = DailyReportIncident.objects.update_or_create(
                report=report,
                source_report=sr,
                source_row_id=str(row.id),
                defaults={
                    'incident_type': 'safety',
                    'description': _wash(row.text),
                    'corrective_action': _wash(row.immediate_action),
                    'severity': row.severity,
                    'row_number': row.row_number,
                    'notification_id': str(note.id) if note is not None else '',
                },
            )
            current_incidents.add(obj.id)
            _upsert_provenance(
                report, sr, 'hse_incident', obj.id, 'hse_incident', row.id, row.row_number,
            )

    for obs in report.general_activities.filter(is_derived=True).exclude(id__in=current_general):
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='general_activity', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()
    for obs in report.visits.filter(is_derived=True).exclude(id__in=current_visits):
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='visit', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()
    for obs in report.incidents.exclude(id__in=current_incidents):
        if obs.source_report_id:
            DailyReportDerivedSource.objects.filter(
                daily_report=report, derived_row_id=str(obs.id),
            ).delete()
            obs.delete()


@transaction.atomic
def rebuild_daily_report_summary(
    project_id,
    report_date: date,
    user=None,
    report: DailyReport | None = None,
) -> DailyReport:
    from projects.models import Project

    # 1. Lock Order: Project -> current unit report(s) -> full-shift DailyReport
    Project.objects.select_for_update().filter(id=project_id).first()

    sub_reports_qs = contributing_sub_reports(project_id, report_date).select_for_update()
    sub_reports = list(sub_reports_qs)

    if report is None:
        report = (
            DailyReport.objects.select_for_update()
            .filter(
                project_id=project_id,
                report_date=report_date,
                shift=ReportShift.FULL,
                is_deleted=False,
                is_current=True,
            )
            .first()
        )
        if report is None:
            return ensure_daily_report_summary(project_id, report_date, user=user)
    else:
        # Reload with lock
        report = DailyReport.objects.select_for_update().get(id=report.id)

    # Bind configuration if not yet bound
    config = None
    if not report.reporting_configuration_id:
        config = resolve_project_reporting_configuration(project_id, report_date)
        if config is not None:
            report.reporting_configuration = config

    fingerprint = compute_aggregation_fingerprint(
        report.reporting_configuration_id or (config.id if config else None),
        sub_reports,
    )

    if (
        report.aggregation_fingerprint
        and report.aggregation_fingerprint == fingerprint
    ):
        report.aggregated_at = timezone.now()
        update_fields = ['aggregated_at', 'updated_at']
        if user is not None:
            report.updated_by = user
            update_fields.append('updated_by')
        report.save(update_fields=update_fields)
        return report

    # Weather & site status derivation preserving overrides
    if not report.weather_override:
        report.weather_condition = _pick_weather(sub_reports)
    if not report.site_status_override:
        if any(
            (getattr(sr, 'site_status', None) or SiteStatus.ACTIVE) == SiteStatus.INACTIVE
            for sr in sub_reports
        ):
            report.site_status = SiteStatus.INACTIVE
            if report.inactivity_reason and report.inactivity_reason not in InactivityReason.values:
                report.inactivity_reason = ''
        elif sub_reports:
            report.site_status = SiteStatus.ACTIVE
            report.inactivity_reason = ''
    else:
        if report.site_status == SiteStatus.ACTIVE:
            report.inactivity_reason = ''

    # Mark link on sub-reports
    for sr in sub_reports:
        if sr.linked_daily_report_id != report.id:
            sr.linked_daily_report = report
            sr.save(update_fields=['linked_daily_report', 'updated_at'])

    # -------------------------------------------------------------------------
    # Activities (DisciplineSubReportActivity & DepartmentActivityRecord)
    # -------------------------------------------------------------------------
    current_derived_activity_ids = set()
    existing_act_sources = {
        (s.source_row_kind, s.source_row_id): s.derived_row_id
        for s in DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='activity',
        )
    }

    for sr in sub_reports:
        # 1. Standard activities
        for row in sr.activities.all().order_by('row_number', 'id'):
            if row.is_deleted:
                continue
            src_key = ('activity', str(row.id))
            existing_id = existing_act_sources.get(src_key)
            act_obj = None
            if existing_id:
                act_obj = DailyReportActivity.objects.filter(id=existing_id, report=report).first()

            if act_obj is None:
                act_obj = DailyReportActivity.objects.create(
                    report=report,
                    activity_description=row.activity_description,
                    # FR-003: shift passes through verbatim — save-time
                    # validation canonicalizes it; aggregation never coerces.
                    shift=row.shift,
                    headcount=row.headcount,
                    foreman_count=row.foreman_count,
                    worker_count=row.worker_count,
                    parcel=row.parcel,
                    zone=row.zone,
                    block=row.block,
                    floor=row.floor,
                    quantity=row.quantity,
                    quantity_measured=row.quantity is not None,
                    unit=row.unit,
                    execution_percentage=row.execution_percentage,
                    activity_ref=row.activity_ref,
                    crew_name=row.crew_name or '',
                    contractor_ref=row.contractor_ref,
                    notes=row.notes or '',
                    source_sub_report=sr,
                    source_discipline=sr.unit or sr.discipline,
                    is_derived=True,
                )
            else:
                act_obj.activity_description = row.activity_description
                act_obj.shift = row.shift
                act_obj.headcount = row.headcount
                act_obj.foreman_count = row.foreman_count
                act_obj.worker_count = row.worker_count
                act_obj.parcel = row.parcel
                act_obj.zone = row.zone
                act_obj.block = row.block
                act_obj.floor = row.floor
                act_obj.quantity = row.quantity
                act_obj.quantity_measured = row.quantity is not None
                act_obj.unit = row.unit
                act_obj.execution_percentage = row.execution_percentage
                act_obj.activity_ref = row.activity_ref
                act_obj.crew_name = row.crew_name or ''
                act_obj.contractor_ref = row.contractor_ref
                act_obj.notes = row.notes or ''
                act_obj.source_sub_report = sr
                act_obj.source_discipline = sr.unit or sr.discipline
                act_obj.save()

            current_derived_activity_ids.add(str(act_obj.id))
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='activity',
                derived_row_id=str(act_obj.id),
                source_report_id_snapshot=sr.id,
                source_row_kind='activity',
                source_row_id=str(row.id),
                defaults={
                    'source_report': sr,
                    'source_report_version': sr.version_number,
                    'source_unit': sr.unit or sr.discipline,
                    'contribution_value': row.quantity,
                    'ordinal': 0,
                },
            )

        # 2. Department activity records
        for dar in sr.activity_records.all().order_by('id'):
            src_key = ('department_activity', str(dar.id))
            existing_id = existing_act_sources.get(src_key)
            act_obj = None
            if existing_id:
                act_obj = DailyReportActivity.objects.filter(id=existing_id, report=report).first()

            desc = dar.activity_description or dar.description or dar.department
            qty = dar.quantity_in or dar.quantity_out or None
            if act_obj is None:
                act_obj = DailyReportActivity.objects.create(
                    report=report,
                    activity_description=desc,
                    shift=ActivityRowShift.SHIFT_1,
                    headcount=None,
                    zone=dar.location or '',
                    block='',
                    floor='',
                    quantity=qty,
                    quantity_measured=qty is not None,
                    unit=dar.unit,
                    execution_percentage=None,
                    activity_ref=None,
                    subcontractor_name=dar.contractor or '',
                    contractor_ref=dar.contractor_ref,
                    notes=dar.description or '',
                    source_sub_report=sr,
                    source_discipline=sr.unit or dar.department,
                    is_derived=True,
                )
            else:
                act_obj.activity_description = desc
                act_obj.quantity = qty
                act_obj.unit = dar.unit
                act_obj.subcontractor_name = dar.contractor or ''
                act_obj.contractor_ref = dar.contractor_ref
                act_obj.source_sub_report = sr
                act_obj.source_discipline = sr.unit or dar.department
                act_obj.save()

            current_derived_activity_ids.add(str(act_obj.id))
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='activity',
                derived_row_id=str(act_obj.id),
                source_report_id_snapshot=sr.id,
                source_row_kind='department_activity',
                source_row_id=str(dar.id),
                defaults={
                    'source_report': sr,
                    'source_report_version': sr.version_number,
                    'source_unit': sr.unit or dar.department,
                    'contribution_value': qty,
                    'ordinal': 0,
                },
            )

    # Remove obsolete derived activities and their sources
    obsolete_acts = report.activities.filter(is_derived=True).exclude(
        id__in=current_derived_activity_ids,
    )
    for obs in obsolete_acts:
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='activity', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()

    # -------------------------------------------------------------------------
    # Labor (Multi-source aggregation without last-source-wins, feature 033 T022)
    # -------------------------------------------------------------------------
    from field_reports.services.man_hours import compute_man_hours
    from project_templates.services import resolve_labor_title

    effective_config = report.reporting_configuration or config or resolve_project_reporting_configuration(
        project_id, report_date,
    )
    rule_code = effective_config.man_hours_rule_code if effective_config else None
    shift_hours = (
        effective_config.standard_shift_hours
        if (effective_config and effective_config.standard_shift_hours is not None)
        else Decimal('8')
    )
    has_catalog = bool(effective_config and effective_config.labor_titles.exists())

    labor_buckets: dict[tuple[str, str], dict] = defaultdict(
        lambda: {
            'present': 0,
            'leave': 0,
            'overtime': Decimal('0.00'),
            'canonical_title': '',
            'sources': [],
        },
    )

    for sr in sub_reports:
        for row in sr.labor_entries.all().order_by('id'):
            if row.is_deleted:
                continue
            raw_title = (row.job_title or '').strip()
            if not raw_title:
                continue

            resolved = (
                resolve_labor_title(effective_config, raw_title)
                if has_catalog
                else None
            )
            if resolved is not None:
                bucket_key = (row.labor_category, f"code:{resolved.title_code}")
                if raw_title in (resolved.title_label, resolved.title_label_fa):
                    display_title = raw_title
                else:
                    display_title = (
                        resolved.title_label_fa
                        or resolved.title_label
                        or raw_title
                    )
            else:
                bucket_key = (row.labor_category, raw_title)
                display_title = raw_title

            bucket = labor_buckets[bucket_key]
            if not bucket['canonical_title']:
                bucket['canonical_title'] = display_title
            bucket['present'] += row.present_count or 0
            bucket['leave'] += row.leave_count or 0
            bucket['overtime'] += Decimal(str(row.overtime_hours or 0))
            bucket['sources'].append({
                'sr': sr,
                'row': row,
            })

    current_derived_labor_ids = set()
    for (category, _bucket_id), bucket in labor_buckets.items():
        title = bucket['canonical_title']
        bucket_man_hours = compute_man_hours(
            rule_code,
            present_count=bucket['present'],
            overtime_person_hours=bucket['overtime'],
            standard_shift_hours=shift_hours,
        )

        # Stably order sources: unit, version, source_row_id (never last-source-wins)
        sorted_sources = sorted(
            bucket['sources'],
            key=lambda s: (s['sr'].unit or '', s['sr'].version_number, str(s['row'].id)),
        )

        primary_sr = sorted_sources[0]['sr'] if sorted_sources else None
        primary_disc = (
            (primary_sr.unit or primary_sr.discipline or '') if primary_sr else ''
        )

        labor_row = report.labor_entries.filter(
            is_derived=True,
            labor_category=category,
            job_title=title,
        ).first()

        if labor_row is None:
            labor_row = DailyReportLabor.objects.create(
                report=report,
                project_id=project_id,
                report_date=report_date,
                labor_category=category,
                job_title=title,
                shift_1_count=bucket['present'],
                shift_2_count=0,
                shift_3_count=0,
                absence_count=bucket['leave'],
                overtime_hours=bucket['overtime'],
                work_hours=bucket_man_hours,
                source_set_complete=True,
                source_sub_report=primary_sr,
                source_discipline=primary_disc,
                is_derived=True,
            )
        else:
            labor_row.shift_1_count = bucket['present']
            labor_row.absence_count = bucket['leave']
            labor_row.overtime_hours = bucket['overtime']
            labor_row.work_hours = bucket_man_hours
            labor_row.source_set_complete = True
            labor_row.source_sub_report = primary_sr
            labor_row.source_discipline = primary_disc
            labor_row.save()

        current_derived_labor_ids.add(str(labor_row.id))

        desired_source_keys = set()
        for idx, src in enumerate(sorted_sources):
            s_sr = src['sr']
            s_row = src['row']
            pres_count = Decimal(str(s_row.present_count or 0))
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='labor',
                derived_row_id=str(labor_row.id),
                source_report_id_snapshot=s_sr.id,
                source_row_kind='labor',
                source_row_id=str(s_row.id),
                defaults={
                    'source_report': s_sr,
                    'source_report_version': s_sr.version_number,
                    'source_unit': s_sr.unit or s_sr.discipline,
                    'contribution_value': pres_count,
                    'ordinal': idx,
                },
            )
            desired_source_keys.add(str(s_row.id))

        # Remove stale sources for this labor row
        DailyReportDerivedSource.objects.filter(
            daily_report=report,
            derived_kind='labor',
            derived_row_id=str(labor_row.id),
        ).exclude(source_row_id__in=desired_source_keys).delete()

    obsolete_labor = report.labor_entries.filter(is_derived=True).exclude(
        id__in=current_derived_labor_ids,
    )
    for obs in obsolete_labor:
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='labor', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()

    # -------------------------------------------------------------------------
    # Machinery (Feature 033 T029: 5-status derivation + identity dedupe)
    # -------------------------------------------------------------------------
    current_derived_machinery_ids = set()
    existing_mach_sources = {
        s.source_row_id: s.derived_row_id
        for s in DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='machinery',
        )
    }

    identity_buckets: dict[str, list[tuple]] = defaultdict(list)
    type_only_rows: list[tuple] = []

    for sr in sub_reports:
        for row in sr.machinery_rows.all().order_by('row_number', 'id'):
            if row.is_deleted:
                continue
            if row.equipment_ref_id:
                identity_buckets[str(row.equipment_ref_id)].append((sr, row))
            else:
                type_only_rows.append((sr, row))

    # 1. Item-level rows with declared equipment_ref (deduplicated per identity)
    for eq_ref_id, contribs in identity_buckets.items():
        primary_sr, primary_row = contribs[0]
        primary_disc = primary_sr.unit or primary_sr.discipline or ''

        mach_obj = report.machinery_rows.filter(
            is_derived=True, equipment_ref_id=eq_ref_id,
        ).first()

        if mach_obj is None:
            mach_obj = DailyReportMachineryRow.objects.create(
                report=report,
                equipment_type=primary_row.equipment_type,
                equipment_ref_id=eq_ref_id,
                status_total=primary_row.status_total,
                status_active=primary_row.status_active,
                status_ready=primary_row.status_ready,
                status_inactive=primary_row.status_inactive,
                status_under_repair=primary_row.status_under_repair,
                operating_hours=primary_row.operating_hours,
                stoppage_hours=primary_row.stoppage_hours,
                repair_hours=primary_row.repair_hours,
                stoppage_reason_code=primary_row.stoppage_reason_code or '',
                source_sub_report=primary_sr,
                source_discipline=primary_disc,
                is_derived=True,
            )
        else:
            mach_obj.equipment_type = primary_row.equipment_type
            mach_obj.status_total = primary_row.status_total
            mach_obj.status_active = primary_row.status_active
            mach_obj.status_ready = primary_row.status_ready
            mach_obj.status_inactive = primary_row.status_inactive
            mach_obj.status_under_repair = primary_row.status_under_repair
            mach_obj.operating_hours = primary_row.operating_hours
            mach_obj.stoppage_hours = primary_row.stoppage_hours
            mach_obj.repair_hours = primary_row.repair_hours
            mach_obj.stoppage_reason_code = primary_row.stoppage_reason_code or ''
            mach_obj.source_sub_report = primary_sr
            mach_obj.source_discipline = primary_disc
            mach_obj.save()

        current_derived_machinery_ids.add(str(mach_obj.id))
        desired_mach_source_ids = set()
        for idx, (s_sr, s_row) in enumerate(contribs):
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='machinery',
                derived_row_id=str(mach_obj.id),
                source_report_id_snapshot=s_sr.id,
                source_row_kind='machinery',
                source_row_id=str(s_row.id),
                defaults={
                    'source_report': s_sr,
                    'source_report_version': s_sr.version_number,
                    'source_unit': s_sr.unit or s_sr.discipline,
                    'contribution_value': Decimal(str(s_row.status_total or 0)),
                    'ordinal': idx,
                },
            )
            desired_mach_source_ids.add(str(s_row.id))

        DailyReportDerivedSource.objects.filter(
            daily_report=report,
            derived_kind='machinery',
            derived_row_id=str(mach_obj.id),
        ).exclude(source_row_id__in=desired_mach_source_ids).delete()

    # 2. Type-only rows (equipment_ref is None: preserved per source row)
    for sr, row in type_only_rows:
        existing_id = existing_mach_sources.get(str(row.id))
        mach_obj = None
        if existing_id:
            mach_obj = DailyReportMachineryRow.objects.filter(
                id=existing_id, report=report, equipment_ref__isnull=True,
            ).first()

        disc = sr.unit or sr.discipline or ''
        if mach_obj is None:
            mach_obj = DailyReportMachineryRow.objects.create(
                report=report,
                equipment_type=row.equipment_type,
                equipment_ref=None,
                status_total=row.status_total,
                status_active=row.status_active,
                status_ready=row.status_ready,
                status_inactive=row.status_inactive,
                status_under_repair=row.status_under_repair,
                operating_hours=row.operating_hours,
                stoppage_hours=row.stoppage_hours,
                repair_hours=row.repair_hours,
                stoppage_reason_code=row.stoppage_reason_code or '',
                source_sub_report=sr,
                source_discipline=disc,
                is_derived=True,
            )
        else:
            mach_obj.equipment_type = row.equipment_type
            mach_obj.status_total = row.status_total
            mach_obj.status_active = row.status_active
            mach_obj.status_ready = row.status_ready
            mach_obj.status_inactive = row.status_inactive
            mach_obj.status_under_repair = row.status_under_repair
            mach_obj.operating_hours = row.operating_hours
            mach_obj.stoppage_hours = row.stoppage_hours
            mach_obj.repair_hours = row.repair_hours
            mach_obj.stoppage_reason_code = row.stoppage_reason_code or ''
            mach_obj.source_sub_report = sr
            mach_obj.source_discipline = disc
            mach_obj.save()

        current_derived_machinery_ids.add(str(mach_obj.id))
        DailyReportDerivedSource.objects.update_or_create(
            daily_report=report,
            derived_kind='machinery',
            derived_row_id=str(mach_obj.id),
            source_report_id_snapshot=sr.id,
            source_row_kind='machinery',
            source_row_id=str(row.id),
            defaults={
                'source_report': sr,
                'source_report_version': sr.version_number,
                'source_unit': disc,
                'contribution_value': Decimal(str(row.status_total or 0)),
                'ordinal': 0,
            },
        )

    obsolete_machinery = report.machinery_rows.filter(is_derived=True).exclude(
        id__in=current_derived_machinery_ids,
    )
    for obs in obsolete_machinery:
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='machinery', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()

    # -------------------------------------------------------------------------
    # Materials (Feature 033 T036: receipt resolution + document reconciliation)
    # -------------------------------------------------------------------------
    from field_reports.services.material_reconciliation import reconcile_material_row

    current_derived_material_ids = set()
    existing_mat_sources = {
        s.source_row_id: s.derived_row_id
        for s in DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='material',
        )
    }
    checked_at = timezone.now()

    for sr in sub_reports:
        for row in sr.material_entries.all().order_by('id'):
            if row.is_deleted:
                continue
            existing_id = existing_mat_sources.get(str(row.id))
            mat_obj = None
            if existing_id:
                mat_obj = DailyReportMaterial.objects.filter(id=existing_id, report=report).first()

            tx_type = (
                MaterialTransactionType.ISSUE
                if row.transaction_type == 'consumption'
                else MaterialTransactionType.RECEIPT
            )
            rec_status, resolved_doc = reconcile_material_row(project_id, row)
            is_receipt_resolved = bool(
                row.transaction_type == 'receipt' and resolved_doc is not None
            )
            rec_doc_id = str(resolved_doc.id) if resolved_doc is not None else ''

            if mat_obj is None:
                mat_obj = DailyReportMaterial.objects.create(
                    report=report,
                    material_ref=row.material_ref,
                    material_description=row.material_description,
                    quantity=row.quantity,
                    unit=row.unit,
                    transaction_type=tx_type,
                    consumption_location=row.consumption_location or '',
                    supplier=row.supplier or '',
                    warehouse_document_reference=row.warehouse_document_reference or '',
                    receipt_resolved=is_receipt_resolved,
                    reconciliation_status=rec_status,
                    reconciliation_document_id=rec_doc_id,
                    reconciliation_checked_at=checked_at,
                    notes=row.notes or '',
                    source_sub_report=sr,
                    source_discipline=sr.unit or sr.discipline,
                    is_derived=True,
                )
            else:
                mat_obj.material_ref = row.material_ref
                mat_obj.material_description = row.material_description
                mat_obj.quantity = row.quantity
                mat_obj.unit = row.unit
                mat_obj.transaction_type = tx_type
                mat_obj.consumption_location = row.consumption_location or ''
                mat_obj.supplier = row.supplier or ''
                mat_obj.warehouse_document_reference = row.warehouse_document_reference or ''
                mat_obj.receipt_resolved = is_receipt_resolved
                mat_obj.reconciliation_status = rec_status
                mat_obj.reconciliation_document_id = rec_doc_id
                mat_obj.reconciliation_checked_at = checked_at
                mat_obj.notes = row.notes or ''
                mat_obj.source_sub_report = sr
                mat_obj.source_discipline = sr.unit or sr.discipline
                mat_obj.save()

            current_derived_material_ids.add(str(mat_obj.id))
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='material',
                derived_row_id=str(mat_obj.id),
                source_report_id_snapshot=sr.id,
                source_row_kind='material',
                source_row_id=str(row.id),
                defaults={
                    'source_report': sr,
                    'source_report_version': sr.version_number,
                    'source_unit': sr.unit or sr.discipline,
                    'contribution_value': row.quantity,
                    'ordinal': 0,
                },
            )

    obsolete_materials = report.material_entries.filter(is_derived=True).exclude(
        id__in=current_derived_material_ids,
    )
    for obs in obsolete_materials:
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='material', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()

    # -------------------------------------------------------------------------
    # Concrete Logs
    # -------------------------------------------------------------------------
    current_derived_concrete_ids = set()
    existing_cnc_sources = {
        s.source_row_id: s.derived_row_id
        for s in DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='concrete',
        )
    }

    for sr in sub_reports:
        for row in sr.concrete_entries.all().order_by('id'):
            if row.is_deleted:
                continue
            existing_id = existing_cnc_sources.get(str(row.id))
            cnc_obj = None
            if existing_id:
                cnc_obj = DailyReportConcreteLog.objects.filter(id=existing_id, report=report).first()

            if (
                row.sampling_state == 'sampling_declared'
                and (row.lab_sample_code or '').strip()
                and row.test_sheet_count is not None
                and not row.qc_inspection_id
                and sr.created_by_id
            ):
                from sub_reports.services.qc_linkage import link_declared_concrete_sampling
                from sub_reports.services.section_validation import SectionContractError

                try:
                    link_declared_concrete_sampling(sr, sr.created_by)
                    row.refresh_from_db()
                except SectionContractError:
                    pass

            concrete_fields = {
                'concrete_description': row.concrete_description,
                'volume_m3': row.volume_m3,
                'zone': row.zone,
                'block': row.block,
                'floor': row.floor,
                'notes': row.notes or '',
                'structural_element': row.structural_element or '',
                'parcel': row.parcel or '',
                'batching_plant': row.batching_plant or '',
                'truck_delivery_note_number': row.truck_delivery_note_number or '',
                'lab_sample_code': row.lab_sample_code or '',
                'sampling_state': row.sampling_state or '',
                'test_sheet_count': row.test_sheet_count,
                'qc_inspection': row.qc_inspection,
                'source_sub_report': sr,
                'source_discipline': sr.unit or sr.discipline,
            }
            if cnc_obj is None:
                cnc_obj = DailyReportConcreteLog.objects.create(
                    report=report,
                    is_derived=True,
                    **concrete_fields,
                )
            else:
                for attr, value in concrete_fields.items():
                    setattr(cnc_obj, attr, value)
                cnc_obj.save()

            current_derived_concrete_ids.add(str(cnc_obj.id))
            DailyReportDerivedSource.objects.update_or_create(
                daily_report=report,
                derived_kind='concrete',
                derived_row_id=str(cnc_obj.id),
                source_report_id_snapshot=sr.id,
                source_row_kind='concrete',
                source_row_id=str(row.id),
                defaults={
                    'source_report': sr,
                    'source_report_version': sr.version_number,
                    'source_unit': sr.unit or sr.discipline,
                    'contribution_value': row.volume_m3,
                    'ordinal': 0,
                },
            )

    obsolete_concrete = report.concrete_logs.filter(is_derived=True).exclude(
        id__in=current_derived_concrete_ids,
    )
    for obs in obsolete_concrete:
        DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='concrete', derived_row_id=str(obs.id),
        ).delete()
        obs.delete()

    # -------------------------------------------------------------------------
    # Structured narrative (issues, visits, HSE, general activities)
    # -------------------------------------------------------------------------
    _rebuild_structured_narrative(report, sub_reports)

    other_notes = []
    for sr in sub_reports:
        tag = sr.unit or sr.discipline
        for row in sr.notes.filter(is_deleted=False, note_type=SubReportNoteType.OTHER).order_by('row_number', 'id'):
            other_notes.append(f'[{tag}] {row.text}')
    marker_start = '<!--auto-summary-notes-->'
    marker_end = '<!--/auto-summary-notes-->'
    existing = report.general_notes or ''
    if marker_start in existing and marker_end in existing:
        before = existing.split(marker_start)[0].rstrip()
        after = existing.split(marker_end, 1)[1].lstrip()
        existing = (before + ('\n' if before and after else '') + after).strip()
    if other_notes:
        block = marker_start + '\n' + '\n'.join(other_notes) + '\n' + marker_end
        report.general_notes = (existing + '\n\n' + block).strip() if existing else block
    else:
        report.general_notes = existing

    report.is_auto_summary = True
    report.aggregated_at = timezone.now()
    report.aggregation_fingerprint = fingerprint
    if user is not None:
        report.updated_by = user

    report.save(
        update_fields=[
            'is_auto_summary',
            'aggregated_at',
            'reporting_configuration',
            'aggregation_fingerprint',
            'weather_condition',
            'site_status',
            'inactivity_reason',
            'general_notes',
            'updated_at',
            *(['updated_by'] if user is not None else []),
        ],
    )
    return report

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
    DailyReportLabor,
    DailyReportMaterial,
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
            'material_entries',
            'concrete_entries',
            'general_activities',
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
                )
                for l in sr.labor_entries.filter(is_deleted=False).order_by('id')
            ],
            'materials': [
                (
                    str(m.id),
                    m.material_description,
                    str(m.quantity),
                    m.unit,
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
                )
                for c in sr.concrete_entries.filter(is_deleted=False).order_by('id')
            ],
            'general_activities': [
                (
                    str(g.id),
                    g.activity_description,
                    g.location or '',
                    str(g.quantity) if g.quantity is not None else '',
                    g.unit or '',
                    g.notes or '',
                )
                for g in sr.general_activities.filter(is_deleted=False).order_by('id')
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
    # Labor (Multi-source aggregation without last-source-wins)
    # -------------------------------------------------------------------------
    labor_buckets: dict[tuple[str, str], dict] = defaultdict(
        lambda: {'present': 0, 'leave': 0, 'sources': []},
    )

    for sr in sub_reports:
        for row in sr.labor_entries.all().order_by('id'):
            if row.is_deleted:
                continue
            key = (row.labor_category, (row.job_title or '').strip())
            if not key[1]:
                continue
            bucket = labor_buckets[key]
            bucket['present'] += row.present_count or 0
            bucket['leave'] += row.leave_count or 0
            bucket['sources'].append({
                'sr': sr,
                'row': row,
            })

    current_derived_labor_ids = set()
    for (category, title), bucket in labor_buckets.items():
        labor_row = report.labor_entries.filter(
            is_derived=True,
            labor_category=category,
            job_title=title,
        ).first()

        primary_sr = bucket['sources'][0]['sr'] if bucket['sources'] else None
        primary_disc = (
            (primary_sr.unit or primary_sr.discipline or '') if primary_sr else ''
        )
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
                source_sub_report=primary_sr,
                source_discipline=primary_disc,
                is_derived=True,
            )
        else:
            labor_row.shift_1_count = bucket['present']
            labor_row.absence_count = bucket['leave']
            labor_row.source_sub_report = primary_sr
            labor_row.source_discipline = primary_disc
            labor_row.save(
                update_fields=[
                    'shift_1_count',
                    'absence_count',
                    'source_sub_report',
                    'source_discipline',
                ]
            )

        current_derived_labor_ids.add(str(labor_row.id))

        # Stably order sources: unit, version, source_row_id
        sorted_sources = sorted(
            bucket['sources'],
            key=lambda s: (s['sr'].unit or '', s['sr'].version_number, str(s['row'].id)),
        )

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
    # Materials
    # -------------------------------------------------------------------------
    current_derived_material_ids = set()
    existing_mat_sources = {
        s.source_row_id: s.derived_row_id
        for s in DailyReportDerivedSource.objects.filter(
            daily_report=report, derived_kind='material',
        )
    }

    for sr in sub_reports:
        for row in sr.material_entries.all().order_by('id'):
            if row.is_deleted:
                continue
            existing_id = existing_mat_sources.get(str(row.id))
            mat_obj = None
            if existing_id:
                mat_obj = DailyReportMaterial.objects.filter(id=existing_id, report=report).first()

            if mat_obj is None:
                mat_obj = DailyReportMaterial.objects.create(
                    report=report,
                    material_description=row.material_description,
                    quantity=row.quantity,
                    unit=row.unit,
                    transaction_type=MaterialTransactionType.RECEIPT,
                    notes=row.notes or '',
                    source_sub_report=sr,
                    source_discipline=sr.unit or sr.discipline,
                    is_derived=True,
                )
            else:
                mat_obj.material_description = row.material_description
                mat_obj.quantity = row.quantity
                mat_obj.unit = row.unit
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

            if cnc_obj is None:
                cnc_obj = DailyReportConcreteLog.objects.create(
                    report=report,
                    concrete_description=row.concrete_description,
                    volume_m3=row.volume_m3,
                    zone=row.zone,
                    block=row.block,
                    floor=row.floor,
                    notes=row.notes or '',
                    source_sub_report=sr,
                    source_discipline=sr.unit or sr.discipline,
                    is_derived=True,
                )
            else:
                cnc_obj.concrete_description = row.concrete_description
                cnc_obj.volume_m3 = row.volume_m3
                cnc_obj.zone = row.zone
                cnc_obj.block = row.block
                cnc_obj.floor = row.floor
                cnc_obj.source_sub_report = sr
                cnc_obj.source_discipline = sr.unit or sr.discipline
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
    # General activities & notes blocks
    # -------------------------------------------------------------------------
    general_parts: list[str] = []
    issue_parts: list[str] = []
    visit_parts: list[str] = []

    for sr in sub_reports:
        tag = sr.unit or sr.discipline
        for row in sr.general_activities.all().order_by('id'):
            if row.is_deleted:
                continue
            loc = row.location or ''
            general_parts.append(
                f'[{tag}] {row.activity_description}'
                + (f' @ {loc}' if loc else '')
                + (f' ({row.quantity} {row.unit})' if row.quantity is not None else ''),
            )

        for row in sr.notes.all().order_by('id'):
            if row.is_deleted:
                continue
            tagged = f'[{tag}] {row.text}'
            if row.note_type == SubReportNoteType.VISIT:
                visit_parts.append(tagged)
            elif row.note_type == SubReportNoteType.ISSUE:
                issue_parts.append(tagged)
            else:
                issue_parts.append(tagged)

    auto_block_parts = []
    if general_parts:
        auto_block_parts.append('فعالیت‌های عمومی:\n' + '\n'.join(general_parts))
    if issue_parts:
        auto_block_parts.append('ملاحظات:\n' + '\n'.join(issue_parts))
    if visit_parts:
        auto_block_parts.append('بازدیدها:\n' + '\n'.join(visit_parts))
    if auto_block_parts:
        marker_start = '<!--auto-summary-notes-->'
        marker_end = '<!--/auto-summary-notes-->'
        existing = report.general_notes or ''
        if marker_start in existing and marker_end in existing:
            before = existing.split(marker_start)[0].rstrip()
            after = existing.split(marker_end, 1)[1].lstrip()
            existing = (before + ('\n' if before and after else '') + after).strip()
        block = marker_start + '\n' + '\n\n'.join(auto_block_parts) + '\n' + marker_end
        report.general_notes = (existing + '\n\n' + block).strip() if existing else block

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

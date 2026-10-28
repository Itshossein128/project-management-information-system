"""Weekly / monthly project period report generation and figure overrides (FR-PRG)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import jdatetime
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from common.jalali import gregorian_to_jalali
from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost, Commitment, CommitmentStatus
from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportMaterial,
    ReportStatus,
)
from projects.models import Activity
from risk.models import BarrierStatus, EventType, Inspection, InspectionResult, RiskEvent
from schedule.models import (
    ActivityProgress,
    BaselineSchedule,
    FigureValueStatus,
    PeriodReportFigure,
    PeriodReportFigureOverride,
    PeriodReportFigureSourceItem,
    PeriodReportKind,
    PeriodReportStatus,
    ProjectPeriodReport,
    ScheduleChangeRequest,
    ScheduleChangeRequestStatus,
)
from schedule.services.evm_service import compute_evm, evm_number
from schedule.services.measurement_service import ProgressValidationError
from schedule.services.progress_service import get_progress_snapshot
from schedule.services.status_report_service import build_schedule_status

WEEKLY_SECTIONS = (
    'completed_activities',
    'critical_activities',
    'labor_machinery',
    'materials',
    'next_week_plan',
    'progress_summary',
    'barriers',
    'decisions_required',
)
MONTHLY_SECTIONS = (
    'progress_summary',
    'baseline_variance',
    'cost',
    'commitments',
    'ipc',
    'risks',
    'hse_summary',
    'qc_summary',
    'next_month_forecast',
)

_OPEN_RISK_STATUSES = (BarrierStatus.OPEN, BarrierStatus.IN_PROGRESS)


# ---------------------------------------------------------------- figure helpers

class _Figure:
    """Computed figure payload before persistence."""

    def __init__(
        self,
        section: str,
        source_type: str,
        source_path: str,
        *,
        value: Any = None,
        recorded: bool = False,
        source_id=None,
        approved: bool = False,
        last_updated_at=None,
        unit_of_measure: str = '',
        source_items: list[dict] | None = None,
    ):
        self.section = section
        self.source_type = source_type
        self.source_path = source_path
        self.value = value if recorded else None
        self.recorded = recorded
        self.source_id = source_id
        self.approved = approved if recorded else False
        self.last_updated_at = last_updated_at if recorded else None
        self.unit_of_measure = unit_of_measure
        self.source_items = source_items or []


def _not_recorded(section: str, source_type: str, source_path: str) -> _Figure:
    return _Figure(section, source_type, source_path)


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _path(project_id, suffix: str) -> str:
    return f'/projects/{project_id}/{suffix}'


def _check_daily_reports_coverage(project, start: date, end: date) -> tuple[list[DailyReport], list[str]]:
    warnings: list[str] = []
    daily_reports = list(
        DailyReport.objects.filter(
            project=project,
            report_date__gte=start,
            report_date__lte=end,
            is_current=True,
            is_deleted=False,
        ).select_related('prepared_by', 'approved_by')
    )

    approved_by_date: dict[date, list[DailyReport]] = {}
    for dr in daily_reports:
        if dr.status == ReportStatus.APPROVED:
            approved_by_date.setdefault(dr.report_date, []).append(dr)

    approved_reports: list[DailyReport] = []
    for day_reports in approved_by_date.values():
        approved_reports.extend(day_reports)

    curr = start
    missing_or_unapproved = []
    while curr <= end:
        if curr not in approved_by_date:
            missing_or_unapproved.append(curr)
        curr += timedelta(days=1)

    if not approved_reports:
        warnings.append('هیچ گزارش روزانه‌ای برای بازه انتخابی ثبت نشده است.')
    for d in missing_or_unapproved:
        try:
            jd_str = gregorian_to_jalali(d)
        except Exception:
            jd_str = d.isoformat()
        warnings.append(f'گزارش روز {jd_str} تأیید نشده است و احجام آن در این گزارش لحاظ نگردید.')

    return approved_reports, warnings


# ---------------------------------------------------------------- section builders

def _progress_summary(project_id, period_end: date) -> _Figure:
    path = _path(project_id, 'progress')
    rows = ActivityProgress.objects.filter(activity__project_id=project_id, activity__is_deleted=False)
    if not rows.filter(report_date__lte=period_end).exists():
        return _not_recorded('progress_summary', 'activity_progress', path)
    snapshot = get_progress_snapshot(project_id, period_end)
    approved = rows.filter(report_date__lte=period_end, approved_progress__isnull=False).exists()
    latest = rows.filter(report_date__lte=period_end).order_by('-report_date').first()
    return _Figure(
        'progress_summary', 'activity_progress', path,
        value=snapshot, recorded=True, approved=approved,
        last_updated_at=timezone.make_aware(
            timezone.datetime.combine(latest.report_date, timezone.datetime.min.time()),
        ) if latest else None,
    )


def _critical_activities(project_id, status_report: dict) -> _Figure:
    path = _path(project_id, 'schedule-status')
    critical_path = status_report['critical_path']
    critical_ids = critical_path.get('critical_activity_ids') or []
    delays = [d for d in status_report['delays'] if d.get('is_critical')]
    if not critical_ids and not delays:
        return _not_recorded('critical_activities', 'schedule_status', path)
    codes = dict(
        Activity.objects.filter(project_id=project_id, id__in=critical_ids).values_list('id', 'activity_code'),
    )
    return _Figure(
        'critical_activities', 'schedule_status', path,
        value={
            'critical_activity_ids': critical_ids,
            'critical_activity_codes': sorted(codes.values()),
            'delayed_critical_activities': delays,
        },
        recorded=True,
        approved=status_report['date_sets']['approved_baseline_id'] is not None,
        last_updated_at=timezone.now(),
    )


def _window_plan(project_id, start: date, end: date, section: str) -> _Figure:
    path = _path(project_id, 'schedule')
    activities = Activity.objects.filter(project_id=project_id, is_deleted=False)
    if not activities.filter(planned_start__isnull=False).exists():
        return _not_recorded(section, 'schedule_plan', path)
    planned = activities.filter(planned_start__lte=end, planned_finish__gte=start).order_by('planned_start')
    items = [
        {
            'activity_id': str(a.id),
            'activity_code': a.activity_code,
            'activity_name': a.activity_name,
            'planned_start': _iso(a.planned_start),
            'planned_finish': _iso(a.planned_finish),
        }
        for a in planned
    ]
    baseline_locked = BaselineSchedule.objects.filter(
        project_id=project_id, is_current=True, is_locked=True,
    ).exists()
    return _Figure(
        section, 'schedule_plan', path,
        value={'window_start': start.isoformat(), 'window_end': end.isoformat(), 'activities': items},
        recorded=True, approved=baseline_locked, last_updated_at=timezone.now(),
    )


def _barriers(project_id) -> _Figure:
    path = _path(project_id, 'barriers')
    events = RiskEvent.objects.filter(project_id=project_id)
    if not events.exists():
        return _not_recorded('barriers', 'risk_event', path)
    open_events = events.filter(
        event_type__in=(EventType.BARRIER, EventType.DELAY), status__in=_OPEN_RISK_STATUSES,
    ).order_by('-updated_at')
    items = [
        {
            'id': str(e.id),
            'event_type': e.event_type,
            'category': e.category,
            'description': e.description,
            'severity': e.severity,
            'status': e.status,
            'target_resolution_date': _iso(e.target_resolution_date),
        }
        for e in open_events
    ]
    latest = open_events.first()
    return _Figure(
        'barriers', 'risk_event', path,
        value={'open_barriers': items}, recorded=True, approved=True,
        last_updated_at=latest.updated_at if latest else None,
    )


def _decisions_required(project_id) -> _Figure:
    path = _path(project_id, 'schedule-change-requests')
    requests = ScheduleChangeRequest.objects.filter(project_id=project_id)
    if not requests.exists():
        return _not_recorded('decisions_required', 'schedule_change_request', path)
    pending = requests.filter(status=ScheduleChangeRequestStatus.SUBMITTED).order_by('-submitted_at')
    items = [
        {'id': str(r.id), 'reason': r.reason, 'submitted_at': _iso(r.submitted_at), 'status': r.status}
        for r in pending
    ]
    latest = pending.first()
    return _Figure(
        'decisions_required', 'schedule_change_request', path,
        value={'pending_schedule_changes': items}, recorded=True, approved=True,
        last_updated_at=latest.updated_at if latest else None,
    )


def _labor_machinery_rollup(project, approved_reports: list[DailyReport]) -> _Figure:
    path = _path(project.id, 'daily-reports')
    if not approved_reports:
        return _not_recorded('labor_machinery', 'daily_report', path)

    report_ids = [r.id for r in approved_reports]
    labor_rows = list(
        DailyReportLabor.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).select_related('contractor_ref', 'report')
    )
    equip_rows = list(
        DailyReportEquipment.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).select_related('equipment', 'report')
    )

    if not labor_rows and not equip_rows:
        return _not_recorded('labor_machinery', 'daily_report', path)

    labor_grouped: dict[tuple, dict] = {}
    total_labor_hours = 0.0
    total_overtime_hours = 0.0
    source_items: list[dict] = []

    for lr in labor_rows:
        dr = lr.report
        c_name = lr.contractor_name or (lr.contractor_ref.name if lr.contractor_ref else 'پیمانکار اصلی')
        key = (c_name, lr.job_title or lr.custom_title or 'عمومی', lr.labor_category or '')
        if key not in labor_grouped:
            labor_grouped[key] = {
                'contractor': key[0],
                'job_title': key[1],
                'labor_category': key[2],
                'regular_hours': 0.0,
                'overtime_hours': 0.0,
                'total_headcount': 0,
            }
        wh = float(lr.work_hours or 0)
        ot = float(lr.overtime_hours or 0)
        cnt = lr.total_count or ((lr.shift_1_count or 0) + (lr.shift_2_count or 0) + (lr.shift_3_count or 0))
        labor_grouped[key]['regular_hours'] += wh
        labor_grouped[key]['overtime_hours'] += ot
        labor_grouped[key]['total_headcount'] += cnt
        total_labor_hours += wh
        total_overtime_hours += ot

        source_items.append({
            'source_type': 'daily_labor',
            'daily_report': dr,
            'daily_labor': lr,
            'source_id': lr.id,
            'source_date': dr.report_date,
            'source_code': f'DR-{dr.report_date}',
            'contributed_quantity': {
                'regular_hours': wh,
                'overtime_hours': ot,
                'headcount': cnt,
                'contractor': key[0],
                'job_title': key[1],
            },
            'created_by': dr.prepared_by,
            'approved_by': dr.approved_by,
        })

    equip_grouped: dict[str, dict] = {}
    total_operating_hours = 0.0
    total_idle_hours = 0.0

    for er in equip_rows:
        dr = er.report
        eq_name = er.equipment_name or (er.equipment.name if er.equipment else 'ماشین‌آلات')
        if eq_name not in equip_grouped:
            equip_grouped[eq_name] = {
                'equipment_name': eq_name,
                'operating_hours': 0.0,
                'idle_hours': 0.0,
                'repair_hours': 0.0,
                'count': 0,
            }
        prod = float(er.productive_hours or 0)
        idle = float(er.idle_hours or 0)
        repair = float(er.repair_hours or 0)
        equip_grouped[eq_name]['operating_hours'] += prod
        equip_grouped[eq_name]['idle_hours'] += idle
        equip_grouped[eq_name]['repair_hours'] += repair
        equip_grouped[eq_name]['count'] += 1
        total_operating_hours += prod
        total_idle_hours += idle

        source_items.append({
            'source_type': 'daily_machinery',
            'daily_report': dr,
            'daily_equipment': er,
            'source_id': er.id,
            'source_date': dr.report_date,
            'source_code': f'DR-{dr.report_date}',
            'contributed_quantity': {
                'operating_hours': prod,
                'idle_hours': idle,
                'repair_hours': repair,
                'equipment_name': eq_name,
            },
            'created_by': dr.prepared_by,
            'approved_by': dr.approved_by,
        })

    payload = {
        'total_regular_hours': round(total_labor_hours, 2),
        'total_overtime_hours': round(total_overtime_hours, 2),
        'total_machinery_operating_hours': round(total_operating_hours, 2),
        'total_machinery_idle_hours': round(total_idle_hours, 2),
        'labor_breakdown': list(labor_grouped.values()),
        'machinery_breakdown': list(equip_grouped.values()),
    }
    latest = approved_reports[-1]
    return _Figure(
        'labor_machinery', 'daily_report', path,
        value=payload, recorded=True, approved=True,
        last_updated_at=latest.approved_at or timezone.now(),
        unit_of_measure='hours',
        source_items=source_items,
    )


def _materials_rollup(project, approved_reports: list[DailyReport]) -> _Figure:
    path = _path(project.id, 'daily-reports')
    if not approved_reports:
        return _not_recorded('materials', 'daily_material', path)

    report_ids = [r.id for r in approved_reports]
    mat_rows = list(
        DailyReportMaterial.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).select_related('material_ref', 'report')
    )
    if not mat_rows:
        return _not_recorded('materials', 'daily_material', path)

    materials_grouped: dict[tuple, dict] = {}
    source_items: list[dict] = []

    for mr in mat_rows:
        dr = mr.report
        desc = mr.material_description or (mr.material_ref.name if mr.material_ref else 'مصالح')
        unit = mr.unit or (mr.material_ref.unit if mr.material_ref else '')
        key = (desc, unit)
        if key not in materials_grouped:
            materials_grouped[key] = {
                'material_name': desc,
                'unit': unit,
                'delivered_quantity': 0.0,
                'consumed_quantity': 0.0,
            }
        qty = float(mr.quantity or 0)
        tt = (mr.transaction_type or '').lower()
        if tt in ('receipt', 'delivery', 'دریافت'):
            materials_grouped[key]['delivered_quantity'] += qty
        else:
            materials_grouped[key]['consumed_quantity'] += qty

        source_items.append({
            'source_type': 'daily_material',
            'daily_report': dr,
            'daily_material': mr,
            'source_id': mr.id,
            'source_date': dr.report_date,
            'source_code': f'DR-{dr.report_date}',
            'contributed_quantity': {
                'quantity': qty,
                'transaction_type': mr.transaction_type,
                'material_name': desc,
                'unit': unit,
            },
            'created_by': dr.prepared_by,
            'approved_by': dr.approved_by,
        })

    payload = {
        'items': [
            {
                'material_name': v['material_name'],
                'unit': v['unit'],
                'delivered_quantity': round(v['delivered_quantity'], 3),
                'consumed_quantity': round(v['consumed_quantity'], 3),
            }
            for v in materials_grouped.values()
        ],
    }
    latest = approved_reports[-1]
    return _Figure(
        'materials', 'daily_material', path,
        value=payload, recorded=True, approved=True,
        last_updated_at=latest.approved_at or timezone.now(),
        source_items=source_items,
    )


def _completed_activities_rollup(project, start: date, end: date, approved_reports: list[DailyReport]) -> _Figure:
    path = _path(project.id, 'schedule')
    completed_activities = list(
        Activity.objects.filter(
            project=project,
            is_deleted=False,
            actual_finish__gte=start,
            actual_finish__lte=end,
        ).order_by('actual_finish')
    )
    report_ids = [r.id for r in approved_reports]
    daily_act_rows = list(
        DailyReportActivity.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).select_related('activity_ref', 'report')
    )

    items: list[dict] = []
    source_items: list[dict] = []
    seen_activity_ids: set[Any] = set()

    for act in completed_activities:
        seen_activity_ids.add(act.id)
        items.append({
            'activity_id': str(act.id),
            'activity_code': act.activity_code,
            'activity_name': act.activity_name,
            'actual_finish': _iso(act.actual_finish),
            'final_volume': float(act.planned_quantity) if act.planned_quantity is not None else None,
            'unit': getattr(act, 'quantity_unit', ''),
        })

    for da in daily_act_rows:
        dr = da.report
        is_completed = (da.execution_percentage is not None and float(da.execution_percentage) >= 100.0)
        if da.activity_ref and da.activity_ref_id in seen_activity_ids:
            source_items.append({
                'source_type': 'daily_activity',
                'daily_report': dr,
                'daily_activity': da,
                'source_id': da.id,
                'source_date': dr.report_date,
                'source_code': f'DR-{dr.report_date}',
                'contributed_quantity': {
                    'activity_code': da.activity_ref.activity_code,
                    'quantity': float(da.quantity or 0),
                    'unit': da.unit or '',
                },
                'created_by': dr.prepared_by,
                'approved_by': dr.approved_by,
            })
        elif is_completed:
            code = da.activity_ref.activity_code if da.activity_ref else 'ACT'
            items.append({
                'activity_id': str(da.activity_ref_id) if da.activity_ref_id else str(da.id),
                'activity_code': code,
                'activity_name': da.activity_description or (da.activity_ref.activity_name if da.activity_ref else ''),
                'actual_finish': _iso(dr.report_date),
                'final_volume': float(da.quantity or 0) if da.quantity is not None else None,
                'unit': da.unit or '',
            })
            source_items.append({
                'source_type': 'daily_activity',
                'daily_report': dr,
                'daily_activity': da,
                'source_id': da.id,
                'source_date': dr.report_date,
                'source_code': f'DR-{dr.report_date}',
                'contributed_quantity': {
                    'activity_code': code,
                    'quantity': float(da.quantity or 0),
                    'unit': da.unit or '',
                },
                'created_by': dr.prepared_by,
                'approved_by': dr.approved_by,
            })

    if not items and not source_items:
        return _not_recorded('completed_activities', 'daily_activity', path)

    return _Figure(
        'completed_activities', 'daily_activity', path,
        value={'completed_activities': items, 'count': len(items)},
        recorded=True, approved=True,
        last_updated_at=timezone.now(),
        source_items=source_items,
    )


def _hse_summary(project, start: date, end: date, approved_reports: list[DailyReport]) -> _Figure:
    path = _path(project.id, 'daily-reports')
    report_ids = [r.id for r in approved_reports]
    incidents = list(
        DailyReportIncident.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).select_related('report').order_by('report__report_date')
    )
    if not incidents:
        return _not_recorded('hse_summary', 'daily_incident', path)

    items: list[dict] = []
    source_items: list[dict] = []
    lost_time = 0
    near_miss = 0
    environmental = 0
    safety = 0

    for inc in incidents:
        dr = inc.report
        t = (inc.incident_type or '').lower()
        if 'lost' in t or inc.severity == 'major':
            lost_time += 1
        elif 'near' in t:
            near_miss += 1
        elif 'env' in t:
            environmental += 1
        else:
            safety += 1

        items.append({
            'id': str(inc.id),
            'incident_type': inc.incident_type,
            'severity': inc.severity,
            'description': inc.description,
            'corrective_action': inc.corrective_action,
            'report_date': _iso(dr.report_date),
        })
        source_items.append({
            'source_type': 'daily_incident',
            'daily_report': dr,
            'daily_incident': inc,
            'source_id': inc.id,
            'source_date': dr.report_date,
            'source_code': f'DR-{dr.report_date}',
            'contributed_quantity': {'type': inc.incident_type, 'severity': inc.severity},
            'created_by': dr.prepared_by,
            'approved_by': dr.approved_by,
        })

    payload = {
        'total_incidents': len(items),
        'lost_time_injuries': lost_time,
        'near_misses': near_miss,
        'environmental_events': environmental,
        'incidents': items,
    }
    return _Figure(
        'hse_summary', 'daily_incident', path,
        value=payload, recorded=True, approved=True,
        last_updated_at=incidents[-1].report.approved_at or timezone.now(),
        source_items=source_items,
    )


def _qc_summary(project, start: date, end: date) -> _Figure:
    path = _path(project.id, 'inspections')
    inspections = Inspection.objects.filter(
        project_id=project.id,
        inspection_date__gte=start,
        inspection_date__lte=end,
        is_deleted=False,
    )
    if not inspections.exists():
        return _not_recorded('qc_summary', 'inspection', path)

    total = inspections.count()
    passed = inspections.filter(result=InspectionResult.PASSED).count()
    failed = inspections.filter(result=InspectionResult.FAILED).count()
    conditional = inspections.filter(result=InspectionResult.CONDITIONALLY_PASSED).count()
    ncrs = inspections.exclude(ncr_reference='').count()

    latest = inspections.order_by('-updated_at').first()
    return _Figure(
        'qc_summary', 'inspection', path,
        value={
            'total_inspections': total,
            'passed': passed,
            'failed': failed,
            'conditional': conditional,
            'non_conformance_reports': ncrs,
        },
        recorded=True, approved=True,
        last_updated_at=latest.updated_at if latest else timezone.now(),
    )


def _baseline_variance(project_id, period_end: date) -> _Figure:
    path = _path(project_id, 'progress')
    has_planned = ActivityProgress.objects.filter(
        activity__project_id=project_id,
        activity__is_deleted=False,
        planned_progress__isnull=False,
        report_date__lte=period_end,
    ).exists()
    if not has_planned:
        return _not_recorded('baseline_variance', 'baseline', path)

    snapshot = get_progress_snapshot(project_id, period_end)
    baseline = BaselineSchedule.objects.filter(project_id=project_id, is_current=True).first()

    evm = compute_evm(project_id, as_of_date=period_end)
    spi_val = evm_number(evm, 'spi')
    cpi_val = evm_number(evm, 'cpi')

    return _Figure(
        'baseline_variance', 'baseline', path,
        value={
            'planned_progress_pct': snapshot['planned_progress_pct'],
            'actual_progress_pct': snapshot['actual_progress_pct'],
            'schedule_variance_pct': snapshot['schedule_variance_pct'],
            'spi': spi_val if spi_val is not None else snapshot.get('spi'),
            'cpi': cpi_val,
            'evm_validity': evm.get('validity'),
        },
        recorded=True,
        source_id=baseline.id if baseline else None,
        approved=bool(baseline and baseline.is_locked),
        last_updated_at=baseline.updated_at if baseline else timezone.now(),
    )


def _cost(project_id, start: date, end: date) -> _Figure:
    path = _path(project_id, 'costs')
    costs = ActualCost.objects.filter(project_id=project_id, cost_date__gte=start, cost_date__lte=end)
    if not costs.exists():
        return _not_recorded('cost', 'cost', path)
    totals = costs.aggregate(total=Sum('amount'), count=Count('id'))
    unapproved = costs.filter(approved_by__isnull=True).exists()
    latest = costs.order_by('-updated_at').first()
    return _Figure(
        'cost', 'cost', path,
        value={'actual_cost_total': str(totals['total']), 'entries': totals['count']},
        recorded=True, approved=not unapproved,
        last_updated_at=latest.updated_at if latest else None,
    )


def _commitments(project_id, end: date) -> _Figure:
    path = _path(project_id, 'commitments')
    commitments = Commitment.objects.filter(
        project_id=project_id, status=CommitmentStatus.APPROVED, commitment_date__lte=end,
    )
    if not commitments.exists():
        return _not_recorded('commitments', 'commitment', path)
    totals = commitments.aggregate(total=Sum('amount'), count=Count('id'))
    latest = commitments.order_by('-updated_at').first()
    return _Figure(
        'commitments', 'commitment', path,
        value={'approved_commitment_total': str(totals['total']), 'count': totals['count']},
        recorded=True, approved=True,
        last_updated_at=latest.updated_at if latest else None,
    )


def _ipc(project_id, start: date, end: date) -> _Figure:
    path = _path(project_id, 'ipcs')
    ipcs = IPC.objects.filter(project_id=project_id, period_start__lte=end, period_end__gte=start)
    if not ipcs.exists():
        return _not_recorded('ipc', 'ipc', path)
    items = [
        {
            'id': str(i.id),
            'ipc_number': i.ipc_number,
            'status': i.status,
            'gross_amount': str(i.gross_amount),
            'net_amount': str(i.net_amount) if i.net_amount is not None else None,
        }
        for i in ipcs.order_by('ipc_number')
    ]
    all_approved = not ipcs.exclude(status__in=(IPCStatus.APPROVED, IPCStatus.PAID)).exists()
    latest = ipcs.order_by('-updated_at').first()
    return _Figure(
        'ipc', 'ipc', path,
        value={'ipcs': items}, recorded=True, approved=all_approved,
        last_updated_at=latest.updated_at if latest else None,
    )


def _risks(project_id) -> _Figure:
    path = _path(project_id, 'risk-events')
    risks = RiskEvent.objects.filter(
        project_id=project_id, event_type=EventType.RISK, status__in=_OPEN_RISK_STATUSES,
    )
    if not RiskEvent.objects.filter(project_id=project_id, event_type=EventType.RISK).exists():
        return _not_recorded('risks', 'risk_event', path)
    items = [
        {
            'id': str(r.id),
            'description': r.description,
            'severity': r.severity,
            'probability': str(r.probability) if r.probability is not None else None,
            'status': r.status,
        }
        for r in risks.order_by('-updated_at')
    ]
    latest = risks.order_by('-updated_at').first()
    return _Figure(
        'risks', 'risk_event', path,
        value={'open_risks': items}, recorded=True, approved=True,
        last_updated_at=latest.updated_at if latest else None,
    )


def _next_month_forecast(project_id, period_end: date, status_report: dict) -> _Figure:
    path = _path(project_id, 'schedule-status')
    forecast_finish = status_report.get('forecast_project_finish')
    window_start = period_end + timedelta(days=1)
    window_end = window_start + timedelta(days=30)
    planned = Activity.objects.filter(
        project_id=project_id, is_deleted=False,
        planned_start__lte=window_end, planned_finish__gte=window_start,
    )
    if not forecast_finish and not planned.exists():
        return _not_recorded('next_month_forecast', 'schedule_status', path)
    return _Figure(
        'next_month_forecast', 'schedule_status', path,
        value={
            'forecast_project_finish': forecast_finish,
            'activities_planned_next_30_days': planned.count(),
            'window_start': window_start.isoformat(),
            'window_end': window_end.isoformat(),
        },
        recorded=True,
        approved=status_report['date_sets']['approved_baseline_id'] is not None,
        last_updated_at=timezone.now(),
    )


def _compose_figures(project, kind: str, start: date, end: date, approved_daily: list[DailyReport]) -> list[_Figure]:
    pid = project.id
    status_report = build_schedule_status(pid, as_of=end)
    if kind == PeriodReportKind.WEEKLY:
        return [
            _completed_activities_rollup(project, start, end, approved_daily),
            _critical_activities(pid, status_report),
            _labor_machinery_rollup(project, approved_daily),
            _materials_rollup(project, approved_daily),
            _window_plan(pid, end + timedelta(days=1), end + timedelta(days=7), 'next_week_plan'),
            _progress_summary(pid, end),
            _barriers(pid),
            _decisions_required(pid),
        ]
    return [
        _progress_summary(pid, end),
        _baseline_variance(pid, end),
        _cost(pid, start, end),
        _commitments(pid, end),
        _ipc(pid, start, end),
        _risks(pid),
        _hse_summary(project, start, end, approved_daily),
        _qc_summary(project, start, end),
        _next_month_forecast(pid, end, status_report),
    ]


# ---------------------------------------------------------------- public API

@transaction.atomic
def generate_period_report(
    project, kind: str, period_start: date, period_end: date, user,
) -> ProjectPeriodReport:
    if kind not in PeriodReportKind.values:
        raise ProgressValidationError('نوع گزارش نامعتبر است.', 'invalid_report_kind')
    if period_end < period_start:
        raise ProgressValidationError('period_end باید بعد از period_start باشد.', 'invalid_period')
    if kind == PeriodReportKind.WEEKLY and (
        period_start.weekday() != 5
        or period_end.weekday() != 4
        or (period_end - period_start).days != 6
    ):
        raise ProgressValidationError(
            'گزارش هفتگی باید دقیقاً از شنبه تا جمعه باشد.', 'invalid_period_boundary',
        )
    if kind == PeriodReportKind.MONTHLY:
        start_j = jdatetime.date.fromgregorian(date=period_start)
        end_j = jdatetime.date.fromgregorian(date=period_end)
        next_month = jdatetime.date(
            start_j.year + (1 if start_j.month == 12 else 0),
            1 if start_j.month == 12 else start_j.month + 1,
            1,
        )
        expected_end = next_month.togregorian() - timedelta(days=1)
        if start_j.day != 1 or end_j.year != start_j.year or end_j.month != start_j.month or period_end != expected_end:
            raise ProgressValidationError(
                'گزارش ماهانه باید دقیقاً با مرزهای یک ماه شمسی منطبق باشد.',
                'invalid_period_boundary',
            )

    now = timezone.now()
    previous = list(
        ProjectPeriodReport.objects.select_for_update().filter(
            project=project,
            kind=kind,
            period_start=period_start,
            period_end=period_end,
            status=PeriodReportStatus.GENERATED,
        ),
    )
    approved_daily, warnings = _check_daily_reports_coverage(project, period_start, period_end)
    label = 'هفتگی' if kind == PeriodReportKind.WEEKLY else 'ماهانه'
    report = ProjectPeriodReport.objects.create(
        project=project,
        kind=kind,
        period_start=period_start,
        period_end=period_end,
        status=PeriodReportStatus.GENERATED,
        warnings=warnings,
        generated_at=now,
        generated_by=user,
        title=f'گزارش {label} {period_start.isoformat()} تا {period_end.isoformat()}',
        created_by=user,
        updated_by=user,
    )
    for old in previous:
        old.status = PeriodReportStatus.SUPERSEDED
        old.superseded_by = report
        old.updated_by = user
        old.save(update_fields=['status', 'superseded_by', 'updated_by', 'updated_at'])

    figures = _compose_figures(project, kind, period_start, period_end, approved_daily)
    for fig in figures:
        db_figure = PeriodReportFigure.objects.create(
            report=report,
            section=fig.section,
            label_key=f'progressReports.sections.{fig.section}',
            value=fig.value,
            calculated_value=fig.value,
            is_overridden=False,
            unit_of_measure=fig.unit_of_measure,
            value_status=FigureValueStatus.RECORDED if fig.recorded else FigureValueStatus.NOT_RECORDED,
            source_type=fig.source_type,
            source_id=fig.source_id,
            source_path=fig.source_path,
            source_approved=fig.approved,
            last_updated_at=fig.last_updated_at,
        )
        if fig.source_items:
            source_items_to_create = [
                PeriodReportFigureSourceItem(
                    figure=db_figure,
                    source_type=item['source_type'],
                    daily_report=item.get('daily_report'),
                    daily_labor=item.get('daily_labor'),
                    daily_equipment=item.get('daily_equipment'),
                    daily_material=item.get('daily_material'),
                    daily_activity=item.get('daily_activity'),
                    daily_incident=item.get('daily_incident'),
                    source_id=item.get('source_id'),
                    source_date=item.get('source_date'),
                    source_code=item.get('source_code', ''),
                    contributed_quantity=item.get('contributed_quantity'),
                    created_by=item.get('created_by'),
                    approved_by=item.get('approved_by'),
                )
                for item in fig.source_items
            ]
            PeriodReportFigureSourceItem.objects.bulk_create(source_items_to_create)

    return report


def reject_direct_figure_mutation() -> None:
    """Figure values change only through ``apply_figure_override``."""
    raise ProgressValidationError(
        'مقدار شاخص گزارش مستقیماً قابل ویرایش نیست؛ از override همراه با دلیل استفاده کنید.',
        'figure_immutable',
    )


@transaction.atomic
def _contains_negative_number(value) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value < 0
    if isinstance(value, dict):
        return any(_contains_negative_number(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_negative_number(item) for item in value)
    return False


_NON_NEGATIVE_FIGURE_SECTIONS = {
    'labor_machinery', 'materials', 'completed_activities', 'hse_summary',
    'qc_summary', 'cost', 'commitments', 'ipc', 'next_week_plan', 'next_month_forecast',
}


def apply_figure_override(
    figure: PeriodReportFigure, new_value, reason: str, user, *, expected_version=None,
) -> PeriodReportFigureOverride:
    reason = (reason or '').strip()
    if len(reason) < 10:
        raise ProgressValidationError('دلیل بازنویسی باید حداقل ۱۰ کاراکتر باشد.', 'override_reason_required')

    figure = PeriodReportFigure.objects.select_for_update().get(pk=figure.pk)
    if figure.report.status == PeriodReportStatus.APPROVED:
        raise ProgressValidationError('گزارش نهایی شده و ارقام آن قفل هستند.', 'report_locked')
    if expected_version is not None and int(expected_version) != figure.version:
        raise ProgressValidationError(
            'این شاخص هم‌زمان توسط کاربر دیگری تغییر کرده است؛ ابتدا داده را تازه‌سازی کنید.',
            'conflict',
        )
    if figure.section in _NON_NEGATIVE_FIGURE_SECTIONS and _contains_negative_number(new_value):
        raise ProgressValidationError('مقدار این شاخص نمی‌تواند منفی باشد.', 'invalid_non_negative_value')

    calculated_val = figure.calculated_value if figure.calculated_value is not None else figure.value

    override = PeriodReportFigureOverride.objects.create(
        figure=figure,
        old_value=figure.value,
        new_value=new_value,
        reason=reason,
        created_by=user,
    )
    PeriodReportFigure.objects.filter(pk=figure.pk).update(
        value=new_value,
        calculated_value=calculated_val,
        is_overridden=True,
        version=figure.version + 1,
        value_status=FigureValueStatus.RECORDED,
        last_updated_at=timezone.now(),
    )
    return override


@transaction.atomic
def approve_period_report(report: ProjectPeriodReport, user) -> ProjectPeriodReport:
    report = ProjectPeriodReport.objects.select_for_update().get(pk=report.pk)
    if report.status == PeriodReportStatus.APPROVED:
        return report
    if report.status == PeriodReportStatus.SUPERSEDED:
        raise ProgressValidationError('گزارش باطل شده قابل تأیید نیست.', 'invalid_report_status')

    project = report.project
    project_code = (
        getattr(project, 'code', None)
        or getattr(project, 'project_code', None)
        or f'PRJ{str(project.id)[:4].upper()}'
    )
    try:
        jdate = jdatetime.date.fromgregorian(date=report.period_end)
        ym_str = jdate.strftime('%Y%m')
    except Exception:
        ym_str = report.period_end.strftime('%Y%m')

    kind_letter = 'W' if report.kind == PeriodReportKind.WEEKLY else 'M'
    prefix = f'REP-{project_code}-{ym_str}-{kind_letter}'
    count = ProjectPeriodReport.objects.filter(
        project=project,
        serial_number__startswith=prefix,
    ).count() + 1
    serial_number = f'{prefix}{count:02d}'

    now = timezone.now()
    report.status = PeriodReportStatus.APPROVED
    report.serial_number = serial_number
    report.approved_by = user
    report.approved_at = now
    report.save(update_fields=['status', 'serial_number', 'approved_by', 'approved_at', 'updated_at'])
    return report

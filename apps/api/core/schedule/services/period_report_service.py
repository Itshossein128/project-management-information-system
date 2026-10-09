"""Weekly / monthly project period report generation and figure overrides (FR-PRG)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from contracts.models import IPC, IPCStatus
from cost_control.models import ActualCost, Commitment, CommitmentStatus
from projects.models import Activity
from risk.models import BarrierStatus, EventType, RiskEvent
from schedule.models import (
    ActivityProgress,
    BaselineSchedule,
    FigureValueStatus,
    PeriodReportFigure,
    PeriodReportFigureOverride,
    PeriodReportKind,
    PeriodReportStatus,
    ProjectPeriodReport,
    ScheduleChangeRequest,
    ScheduleChangeRequestStatus,
)
from schedule.services.measurement_service import ProgressValidationError
from schedule.services.progress_service import get_progress_snapshot
from schedule.services.status_report_service import build_schedule_status

WEEKLY_SECTIONS = (
    'progress_summary',
    'critical_activities',
    'next_week_plan',
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
    ):
        self.section = section
        self.source_type = source_type
        self.source_path = source_path
        self.value = value if recorded else None
        self.recorded = recorded
        self.source_id = source_id
        self.approved = approved if recorded else False
        self.last_updated_at = last_updated_at if recorded else None


def _not_recorded(section: str, source_type: str, source_path: str) -> _Figure:
    return _Figure(section, source_type, source_path)


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _path(project_id, suffix: str) -> str:
    return f'/projects/{project_id}/{suffix}'


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
    return _Figure(
        'baseline_variance', 'baseline', path,
        value={
            'planned_progress_pct': snapshot['planned_progress_pct'],
            'actual_progress_pct': snapshot['actual_progress_pct'],
            'schedule_variance_pct': snapshot['schedule_variance_pct'],
            'spi': snapshot['spi'],
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


def _compose_figures(project, kind: str, start: date, end: date) -> list[_Figure]:
    pid = project.id
    status_report = build_schedule_status(pid, as_of=end)
    if kind == PeriodReportKind.WEEKLY:
        return [
            _progress_summary(pid, end),
            _critical_activities(pid, status_report),
            _window_plan(pid, end + timedelta(days=1), end + timedelta(days=7), 'next_week_plan'),
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
    label = 'هفتگی' if kind == PeriodReportKind.WEEKLY else 'ماهانه'
    report = ProjectPeriodReport.objects.create(
        project=project,
        kind=kind,
        period_start=period_start,
        period_end=period_end,
        status=PeriodReportStatus.GENERATED,
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

    PeriodReportFigure.objects.bulk_create([
        PeriodReportFigure(
            report=report,
            section=fig.section,
            label_key=f'progressReports.sections.{fig.section}',
            value=fig.value,
            value_status=FigureValueStatus.RECORDED if fig.recorded else FigureValueStatus.NOT_RECORDED,
            source_type=fig.source_type,
            source_id=fig.source_id,
            source_path=fig.source_path,
            source_approved=fig.approved,
            last_updated_at=fig.last_updated_at,
        )
        for fig in _compose_figures(project, kind, period_start, period_end)
    ])
    return report


def reject_direct_figure_mutation() -> None:
    """Figure values change only through ``apply_figure_override``."""
    raise ProgressValidationError(
        'مقدار شاخص گزارش مستقیماً قابل ویرایش نیست؛ از override همراه با دلیل استفاده کنید.',
        'figure_immutable',
    )


@transaction.atomic
def apply_figure_override(figure: PeriodReportFigure, new_value, reason: str, user) -> PeriodReportFigureOverride:
    reason = (reason or '').strip()
    if not reason:
        raise ProgressValidationError('دلیل override الزامی است.', 'override_reason_required')
    figure = PeriodReportFigure.objects.select_for_update().get(pk=figure.pk)
    override = PeriodReportFigureOverride.objects.create(
        figure=figure,
        old_value=figure.value,
        new_value=new_value,
        reason=reason,
        created_by=user,
    )
    # Queryset update: the only sanctioned write path for ``value``.
    PeriodReportFigure.objects.filter(pk=figure.pk).update(
        value=new_value,
        value_status=FigureValueStatus.RECORDED,
        last_updated_at=timezone.now(),
    )
    return override

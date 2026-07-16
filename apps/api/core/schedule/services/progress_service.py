"""Project progress aggregation and S-curve data."""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta

import redis
from django.conf import settings

from projects.models import Activity, ActivityStatus
from schedule.models import ActivityProgress

logger = logging.getLogger(__name__)

S_CURVE_TTL = 3600


def _redis_client():
    return redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


def s_curve_cache_key(project_id, date_from: date, date_to: date, interval: str) -> str:
    return f"s_curve:{project_id}:{date_from.isoformat()}:{date_to.isoformat()}:{interval}"


def invalidate_s_curve_cache(project_id) -> None:
    try:
        client = _redis_client()
        pattern = f"s_curve:{project_id}:*"
        for key in client.scan_iter(match=pattern):
            client.delete(key)
    except Exception:  # noqa: BLE001 - cache is best-effort
        logger.warning('Failed to invalidate s-curve cache for project %s', project_id, exc_info=True)


def get_project_progress_on_date(project_id, on_date: date) -> float:
    """Weighted average of latest actual progress per activity on or before `on_date`."""
    activities = Activity.objects.filter(
        project_id=project_id,
        is_deleted=False,
        weight__isnull=False,
    )
    # ⚡ Bolt: Evaluate activities once
    activities_list = list(activities)
    total_weight = sum(float(a.weight) for a in activities_list)
    if total_weight == 0:
        return 0.0

    # ⚡ Bolt: Fetch latest actual_progress for all activities in one query
    progresses = (
        ActivityProgress.objects.filter(
            activity__project_id=project_id,
            activity__is_deleted=False,
            activity__weight__isnull=False,
            report_date__lte=on_date,
            actual_progress__isnull=False,
        )
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    progress_map = {p.activity_id: float(p.actual_progress) for p in progresses}

    weighted_sum = 0.0
    for activity in activities_list:
        actual = progress_map.get(activity.id, 0.0)
        weighted_sum += float(activity.weight) * actual

    return weighted_sum / total_weight


def get_planned_progress_on_date(project_id, on_date: date) -> float:
    activities = Activity.objects.filter(
        project_id=project_id,
        is_deleted=False,
        weight__isnull=False,
    )
    # ⚡ Bolt: Evaluate activities once
    activities_list = list(activities)
    total_weight = sum(float(a.weight) for a in activities_list)
    if total_weight == 0:
        return 0.0

    # ⚡ Bolt: Fetch latest planned_progress for all activities in one query
    progresses = (
        ActivityProgress.objects.filter(
            activity__project_id=project_id,
            activity__is_deleted=False,
            activity__weight__isnull=False,
            report_date__lte=on_date,
            planned_progress__isnull=False,
        )
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    progress_map = {p.activity_id: float(p.planned_progress) for p in progresses}

    weighted_sum = 0.0
    for activity in activities_list:
        planned = progress_map.get(activity.id, 0.0)
        weighted_sum += float(activity.weight) * planned

    return weighted_sum / total_weight


def _aggregate_interval_points(project_id, date_from: date, date_to: date, interval: str):
    if interval == 'weekly':
        points: list[date] = []
        current = date_from
        while current <= date_to:
            week_end = current + timedelta(days=(6 - current.weekday()))
            if week_end > date_to:
                week_end = date_to
            points.append(week_end)
            current = week_end + timedelta(days=1)
        if not points or points[-1] < date_to:
            points.append(date_to)
        return points

    if interval == 'monthly':
        points = []
        current = date_from.replace(day=1)
        while current <= date_to:
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1, day=1)
            else:
                next_month = current.replace(month=current.month + 1, day=1)
            month_end = next_month - timedelta(days=1)
            if month_end > date_to:
                month_end = date_to
            if month_end >= date_from:
                points.append(month_end)
            current = next_month
        if not points or points[-1] < date_to:
            points.append(date_to)
        return points

    points = []
    current = date_from
    while current <= date_to:
        points.append(current)
        current += timedelta(days=1)
    return points


def get_s_curve_data(
    project_id,
    date_from: date,
    date_to: date,
    interval: str = 'daily',
    *,
    force_refresh: bool = False,
) -> tuple[list[dict], str | None]:
    """
    Returns daily (or aggregated) planned/actual progress for charting.
    Optional warning when daily interval spans more than 365 days.
    """
    warning = None
    if interval == 'daily' and (date_to - date_from).days > 365:
        warning = (
            'بازه تاریخ بیش از یک سال است. برای عملکرد بهتر از بازه هفتگی یا ماهانه استفاده کنید.'
        )
        logger.warning(
            'S-curve daily interval spans %s days for project %s; suggest weekly/monthly',
            (date_to - date_from).days,
            project_id,
        )

    cache_key = s_curve_cache_key(project_id, date_from, date_to, interval)
    if not force_refresh:
        try:
            client = _redis_client()
            cached = client.get(cache_key)
            if cached:
                return json.loads(cached), warning
        except Exception:  # noqa: BLE001
            logger.debug('S-curve cache read failed', exc_info=True)

    result = []
    for point_date in _aggregate_interval_points(project_id, date_from, date_to, interval):
        planned = get_planned_progress_on_date(project_id, point_date)
        actual = get_project_progress_on_date(project_id, point_date)
        result.append({
            'date': point_date.strftime('%Y-%m-%d'),
            'planned_progress': round(planned * 100, 2),
            'actual_progress': round(actual * 100, 2),
            'variance': round((actual - planned) * 100, 2),
        })

    try:
        client = _redis_client()
        client.setex(cache_key, S_CURVE_TTL, json.dumps(result))
    except Exception:  # noqa: BLE001
        logger.debug('S-curve cache write failed', exc_info=True)

    return result, warning


def get_progress_snapshot(project_id, as_of: date) -> dict:
    planned = get_planned_progress_on_date(project_id, as_of)
    actual = get_project_progress_on_date(project_id, as_of)
    spi = round(actual / planned, 3) if planned else None

    activities = Activity.objects.filter(project_id=project_id, is_deleted=False)
    # ⚡ Bolt: Evaluate activities once
    activities_list = list(activities)
    weighted = [a for a in activities_list if a.weight is not None]

    # ⚡ Bolt: Fetch latest progress for all activities in one query
    progresses = (
        ActivityProgress.objects.filter(
            activity__project_id=project_id,
            activity__is_deleted=False,
            report_date__lte=as_of,
        )
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    progress_map = {p.activity_id: p for p in progresses}

    behind = 0
    for activity in weighted:
        latest = progress_map.get(activity.id)
        if not latest:
            continue
        planned_a = float(latest.planned_progress or 0)
        actual_a = float(latest.actual_progress or 0)
        if actual_a < planned_a:
            behind += 1

    from field_reports.models import DailyReport, ReportStatus

    last_report = (
        DailyReport.objects.filter(
            project_id=project_id,
            status=ReportStatus.APPROVED,
            is_deleted=False,
        )
        .order_by('-report_date')
        .first()
    )

    # ⚡ Bolt: Calculate counts from the already evaluated list
    return {
        'as_of_date': as_of.strftime('%Y-%m-%d'),
        'planned_progress_pct': round(planned * 100, 2),
        'actual_progress_pct': round(actual * 100, 2),
        'schedule_variance_pct': round((actual - planned) * 100, 2),
        'spi': spi,
        'activities_total': len(activities_list),
        'activities_completed': sum(1 for a in activities_list if a.status == ActivityStatus.COMPLETED),
        'activities_in_progress': sum(1 for a in activities_list if a.status == ActivityStatus.IN_PROGRESS),
        'activities_not_started': sum(1 for a in activities_list if a.status == ActivityStatus.NOT_STARTED),
        'activities_behind_schedule': behind,
        'last_approved_report_date': (
            last_report.report_date.strftime('%Y-%m-%d') if last_report else None
        ),
    }


def get_activity_progress_breakdown(project_id, as_of: date, *, wbs_id=None, status=None, is_behind=None):
    qs = Activity.objects.filter(
        project_id=project_id,
        is_deleted=False,
        weight__isnull=False,
    ).select_related('wbs', 'unit')
    if wbs_id:
        qs = qs.filter(wbs_id=wbs_id)
    if status:
        qs = qs.filter(status=status)

    # ⚡ Bolt: Evaluate activities once
    activities_list = list(qs)

    # ⚡ Bolt: Fetch latest progress for only the relevant activities in one query
    progresses = (
        ActivityProgress.objects.filter(
            activity_id__in=[a.id for a in activities_list],
            report_date__lte=as_of,
        )
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    progress_map = {p.activity_id: p for p in progresses}

    rows = []
    for activity in activities_list:
        latest = progress_map.get(activity.id)

        planned = float(latest.planned_progress or 0) if latest else 0.0
        actual = float(latest.actual_progress or 0) if latest else 0.0
        variance = actual - planned
        behind = actual < planned
        if is_behind is not None and behind != is_behind:
            continue
        rows.append({
            'activity_id': str(activity.id),
            'activity_code': activity.activity_code,
            'activity_name': activity.activity_name,
            'wbs_name': activity.wbs.wbs_name if activity.wbs_id else '',
            'weight': float(activity.weight) if activity.weight is not None else None,
            'planned_progress_pct': round(planned * 100, 2),
            'actual_progress_pct': round(actual * 100, 2),
            'variance_pct': round(variance * 100, 2),
            'total_quantity': float(activity.total_quantity) if activity.total_quantity else None,
            'cumulative_quantity': (
                float(latest.cumulative_quantity) if latest and latest.cumulative_quantity is not None else None
            ),
            'unit': activity.unit.unit_symbol or activity.unit.unit_name if activity.unit_id else '',
            'status': activity.status,
            'is_behind': behind,
            'last_update_date': latest.report_date.strftime('%Y-%m-%d') if latest else None,
        })
    return rows


def get_progress_history(project_id):
    from field_reports.models import DailyReport, ReportStatus

    reports = (
        DailyReport.objects.filter(
            project_id=project_id,
            status=ReportStatus.APPROVED,
            is_deleted=False,
        )
        .select_related('approved_by')
        .order_by('report_date')
    )
    history = []
    for report in reports:
        planned = get_planned_progress_on_date(project_id, report.report_date)
        actual = get_project_progress_on_date(project_id, report.report_date)
        history.append({
            'date': report.report_date.strftime('%Y-%m-%d'),
            'planned_pct': round(planned * 100, 2),
            'actual_pct': round(actual * 100, 2),
            'variance_pct': round((actual - planned) * 100, 2),
            'approved_by_name': (
                report.approved_by.get_full_name() or report.approved_by.username
                if report.approved_by
                else ''
            ),
            'report_id': str(report.id),
        })
    return history

"""Equipment utilization calculations."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from django.db.models import Q

from field_reports.models import DailyReportEquipment, EquipmentLog, ReportStatus


DEFAULT_SHIFT_HOURS = 8.0


def _span_hours(log_date, work_start, work_end) -> float:
    if not work_start or not work_end:
        return 0.0
    start = datetime.combine(log_date, work_start)
    end = datetime.combine(log_date, work_end)
    if end < start:
        end += timedelta(days=1)
    return (end - start).total_seconds() / 3600


def _productive_hours(log_date, productive_hours, work_start, work_end, repair_hours) -> float:
    if productive_hours is not None:
        return float(productive_hours)
    span = _span_hours(log_date, work_start, work_end)
    if span <= 0:
        return 0.0
    return max(0.0, span - float(repair_hours or 0))


def _idle_hours(idle_hours, log_date, work_start, work_end, repair_hours, productive) -> float:
    if idle_hours is not None:
        return float(idle_hours)
    span = _span_hours(log_date, work_start, work_end)
    if span <= 0:
        return 0.0
    return max(0.0, span - float(repair_hours or 0) - productive)


def _utilization_rate(productive: float, idle: float) -> float | None:
    total = productive + idle
    if total <= 0:
        return None
    return round(productive / total * 100, 2)


def _cost_rollup(productive: float, hourly_rate, fuel_cost) -> float:
    rate = float(hourly_rate or 0)
    fuel = float(fuel_cost or 0)
    return round(productive * rate + fuel, 2)


def _row_from_log(
    *,
    log_date,
    equipment_name,
    equipment_code,
    status,
    productive,
    idle,
    hourly_rate,
    fuel_cost,
):
    return {
        'date': log_date.isoformat() if hasattr(log_date, 'isoformat') else str(log_date),
        'equipment_name': equipment_name,
        'equipment_code': equipment_code or '',
        'status': status,
        'productive_hours': round(productive, 2),
        'idle_hours': round(idle, 2),
        'utilization_rate': _utilization_rate(productive, idle),
        'total_cost': _cost_rollup(productive, hourly_rate, fuel_cost),
    }


def _collect_standalone_logs(project_id, date_from=None, date_to=None):
    qs = EquipmentLog.objects.filter(project_id=project_id, is_deleted=False).select_related('equipment')
    if date_from:
        qs = qs.filter(log_date__gte=date_from)
    if date_to:
        qs = qs.filter(log_date__lte=date_to)
    rows = []
    for log in qs:
        productive = _productive_hours(
            log.log_date, log.productive_hours, log.work_start, log.work_end, log.repair_hours
        )
        idle = _idle_hours(
            log.idle_hours, log.log_date, log.work_start, log.work_end, log.repair_hours, productive
        )
        code = log.equipment.equipment_code if log.equipment_id else log.equipment_ref
        rows.append(
            _row_from_log(
                log_date=log.log_date,
                equipment_name=log.equipment_name,
                equipment_code=code,
                status=log.status,
                productive=productive,
                idle=idle,
                hourly_rate=log.hourly_rate,
                fuel_cost=log.fuel_cost,
            )
        )
    return rows


def _collect_daily_report_equipment(project_id, date_from=None, date_to=None):
    qs = DailyReportEquipment.objects.filter(
        is_deleted=False,
        report__project_id=project_id,
        report__status=ReportStatus.APPROVED,
        report__is_deleted=False,
    ).select_related('report', 'equipment')
    if date_from:
        qs = qs.filter(report__report_date__gte=date_from)
    if date_to:
        qs = qs.filter(report__report_date__lte=date_to)

    rows = []
    for entry in qs:
        log_date = entry.report.report_date
        productive = _productive_hours(
            log_date, entry.productive_hours, entry.work_start, entry.work_end, entry.repair_hours
        )
        idle = _idle_hours(
            entry.idle_hours, log_date, entry.work_start, entry.work_end, entry.repair_hours, productive
        )
        code = entry.equipment.equipment_code if entry.equipment_id else entry.equipment_ref
        rows.append(
            _row_from_log(
                log_date=log_date,
                equipment_name=entry.equipment_name,
                equipment_code=code,
                status=entry.status,
                productive=productive,
                idle=idle,
                hourly_rate=entry.hourly_rate,
                fuel_cost=entry.fuel_cost,
            )
        )
    return rows


def equipment_utilization_list(project_id, *, date_from=None, date_to=None, equipment_name=None):
    rows = _collect_standalone_logs(project_id, date_from, date_to)
    rows.extend(_collect_daily_report_equipment(project_id, date_from, date_to))
    if equipment_name:
        rows = [r for r in rows if equipment_name.lower() in r['equipment_name'].lower()]

    grouped: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (row['equipment_name'], row['equipment_code'])
        if key not in grouped:
            grouped[key] = {
                'equipment_name': row['equipment_name'],
                'equipment_code': row['equipment_code'],
                'productive_hours': 0.0,
                'idle_hours': 0.0,
                'total_cost': 0.0,
                'log_count': 0,
                'active_count': 0,
                'standby_count': 0,
                'broken_count': 0,
            }
        g = grouped[key]
        g['productive_hours'] += row['productive_hours']
        g['idle_hours'] += row['idle_hours']
        g['total_cost'] += row['total_cost']
        g['log_count'] += 1
        if row['status'] == 'active':
            g['active_count'] += 1
        elif row['status'] == 'standby':
            g['standby_count'] += 1
        elif row['status'] == 'broken':
            g['broken_count'] += 1

    result = []
    for g in grouped.values():
        productive = g['productive_hours']
        idle = g['idle_hours']
        result.append(
            {
                **g,
                'productive_hours': round(productive, 2),
                'idle_hours': round(idle, 2),
                'total_cost': round(g['total_cost'], 2),
                'utilization_rate': _utilization_rate(productive, idle),
            }
        )
    result.sort(key=lambda x: x['equipment_name'])
    return result


def equipment_utilization_summary(project_id, *, date_from=None, date_to=None):
    rows = equipment_utilization_list(project_id, date_from=date_from, date_to=date_to)
    if not rows:
        return {
            'equipment_count': 0,
            'avg_utilization_rate': None,
            'total_productive_hours': 0,
            'total_idle_hours': 0,
            'total_cost': 0,
            'active_logs': 0,
            'standby_logs': 0,
            'broken_logs': 0,
        }

    rates = [r['utilization_rate'] for r in rows if r['utilization_rate'] is not None]
    return {
        'equipment_count': len(rows),
        'avg_utilization_rate': round(sum(rates) / len(rates), 2) if rates else None,
        'total_productive_hours': round(sum(r['productive_hours'] for r in rows), 2),
        'total_idle_hours': round(sum(r['idle_hours'] for r in rows), 2),
        'total_cost': round(sum(r['total_cost'] for r in rows), 2),
        'active_logs': sum(r['active_count'] for r in rows),
        'standby_logs': sum(r['standby_count'] for r in rows),
        'broken_logs': sum(r['broken_count'] for r in rows),
    }

"""Labor productivity = executed quantity / labor hours."""

from __future__ import annotations

from collections import defaultdict

from django.db.models import Q, Sum

from cost_control.models import Budget
from field_reports.models import DailyReportActivity, DailyReportLabor, ReportStatus

DEFAULT_SHIFT_HOURS = 8.0


def _effective_work_hours(labor_row) -> float:
    if labor_row.work_hours is not None:
        base = float(labor_row.work_hours)
    else:
        base = float(labor_row.total_count or 0) * DEFAULT_SHIFT_HOURS
    overtime = float(labor_row.overtime_hours or 0)
    return base + overtime


def _labor_queryset(project_id, date_from=None, date_to=None):
    qs = DailyReportLabor.objects.filter(is_deleted=False).filter(
        Q(
            report__project_id=project_id,
            report__status=ReportStatus.APPROVED,
            report__is_deleted=False,
        )
        | Q(project_id=project_id, report__isnull=True)
    )
    if date_from:
        qs = qs.filter(
            Q(report_date__gte=date_from) | Q(report__report_date__gte=date_from)
        )
    if date_to:
        qs = qs.filter(Q(report_date__lte=date_to) | Q(report__report_date__lte=date_to))
    return qs


def _activity_qty_queryset(project_id, date_from=None, date_to=None, activity_id=None):
    qs = DailyReportActivity.objects.filter(
        is_deleted=False,
        report__project_id=project_id,
        report__status=ReportStatus.APPROVED,
        report__is_deleted=False,
        quantity_measured=True,
        activity_ref__isnull=False,
    )
    if date_from:
        qs = qs.filter(report__report_date__gte=date_from)
    if date_to:
        qs = qs.filter(report__report_date__lte=date_to)
    if activity_id:
        qs = qs.filter(activity_ref_id=activity_id)
    return qs


def _planned_man_days(project_id, activity_id=None):
    """Budget labor amount as proxy; returns None if no budget rows."""
    qs = Budget.objects.filter(project_id=project_id, cost_category='labor', is_deleted=False)
    if activity_id:
        qs = qs.filter(activity_id=activity_id)
    total = qs.aggregate(total=Sum('budget_amount'))['total']
    if total is None:
        return None
    return float(total)


def labor_productivity_report(
    project_id,
    *,
    date_from=None,
    date_to=None,
    activity_id=None,
    group_by='activity',
):
    labor_qs = _labor_queryset(project_id, date_from, date_to)
    total_labor_hours = sum(_effective_work_hours(row) for row in labor_qs)

    activity_qty = (
        _activity_qty_queryset(project_id, date_from, date_to, activity_id)
        .values('activity_ref_id', 'activity_ref__activity_code', 'activity_ref__activity_name')
        .annotate(executed_qty=Sum('quantity'))
    )

    if group_by == 'job_title':
        by_title: dict[str, dict] = defaultdict(lambda: {'labor_hours': 0.0, 'headcount_days': 0})
        for row in labor_qs:
            key = row.job_title
            by_title[key]['labor_hours'] += _effective_work_hours(row)
            by_title[key]['headcount_days'] += row.total_count or 0
        rows = [
            {
                'job_title': title,
                'labor_hours': round(data['labor_hours'], 2),
                'headcount_days': data['headcount_days'],
                'productivity_index': None,
            }
            for title, data in sorted(by_title.items())
        ]
        return {
            'group_by': group_by,
            'total_labor_hours': round(total_labor_hours, 2),
            'rows': rows,
        }

    if group_by == 'discipline':
        by_cat: dict[str, dict] = defaultdict(lambda: {'labor_hours': 0.0, 'headcount_days': 0})
        for row in labor_qs:
            key = row.labor_category
            by_cat[key]['labor_hours'] += _effective_work_hours(row)
            by_cat[key]['headcount_days'] += row.total_count or 0
        rows = [
            {
                'discipline': cat,
                'labor_hours': round(data['labor_hours'], 2),
                'headcount_days': data['headcount_days'],
            }
            for cat, data in sorted(by_cat.items())
        ]
        return {
            'group_by': group_by,
            'total_labor_hours': round(total_labor_hours, 2),
            'rows': rows,
        }

    rows = []
    for item in activity_qty:
        act_id = item['activity_ref_id']
        executed = float(item['executed_qty'] or 0)
        hours = total_labor_hours
        if activity_id and str(act_id) != str(activity_id):
            continue
        productivity = round(executed / hours, 4) if hours > 0 and executed > 0 else None
        planned = _planned_man_days(project_id, act_id)
        actual_man_days = sum(
            (row.total_count or 0)
            for row in labor_qs
            if row.report_id is None or True
        )
        rows.append(
            {
                'activity_id': str(act_id),
                'activity_code': item['activity_ref__activity_code'],
                'activity_name': item['activity_ref__activity_name'],
                'executed_qty': executed,
                'labor_hours': round(hours, 2),
                'productivity_index': productivity,
                'planned_budget_labor': planned,
                'actual_man_days': actual_man_days,
            }
        )

    project_executed = float(
        _activity_qty_queryset(project_id, date_from, date_to, activity_id).aggregate(
            total=Sum('quantity')
        )['total']
        or 0
    )
    return {
        'group_by': 'activity',
        'total_labor_hours': round(total_labor_hours, 2),
        'total_executed_qty': project_executed,
        'project_productivity_index': round(project_executed / total_labor_hours, 4)
        if total_labor_hours > 0 and project_executed > 0
        else None,
        'rows': rows,
    }

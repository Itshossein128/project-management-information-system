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


def _allocate_labor_to_activities(project_id, date_from=None, date_to=None, activity_id=None):
    """
    Allocate labor hours / headcount to activities.

    Labor rows are not activity-linked (Shiraz grid). Hours on a daily report are
    split across measured activities on that report by executed-qty share.
    Standalone labor (no report) is split across all activities by total qty share.
    """
    labor_qs = list(_labor_queryset(project_id, date_from, date_to))

    hours_by_report: dict = defaultdict(float)
    headcount_by_report: dict = defaultdict(float)
    orphan_hours = 0.0
    orphan_headcount = 0.0
    for row in labor_qs:
        hours = _effective_work_hours(row)
        headcount = float(row.total_count or 0)
        if row.report_id:
            hours_by_report[row.report_id] += hours
            headcount_by_report[row.report_id] += headcount
        else:
            orphan_hours += hours
            orphan_headcount += headcount

    qty_rows = list(
        _activity_qty_queryset(project_id, date_from, date_to, activity_id).values(
            'report_id',
            'activity_ref_id',
            'activity_ref__activity_code',
            'activity_ref__activity_name',
            'quantity',
        )
    )

    qty_by_report_activity: dict[tuple, float] = defaultdict(float)
    meta_by_activity: dict = {}
    qty_by_report: dict = defaultdict(float)
    total_qty = 0.0

    for row in qty_rows:
        act_id = row['activity_ref_id']
        qty = float(row['quantity'] or 0)
        qty_by_report_activity[(row['report_id'], act_id)] += qty
        qty_by_report[row['report_id']] += qty
        total_qty += qty
        meta_by_activity[act_id] = {
            'activity_code': row['activity_ref__activity_code'],
            'activity_name': row['activity_ref__activity_name'],
        }

    allocated_hours: dict = defaultdict(float)
    allocated_headcount: dict = defaultdict(float)
    executed_by_activity: dict = defaultdict(float)

    for (report_id, act_id), qty in qty_by_report_activity.items():
        executed_by_activity[act_id] += qty
        report_qty = qty_by_report.get(report_id) or 0
        if report_qty <= 0:
            continue
        share = qty / report_qty
        allocated_hours[act_id] += hours_by_report.get(report_id, 0.0) * share
        allocated_headcount[act_id] += headcount_by_report.get(report_id, 0.0) * share

    if orphan_hours or orphan_headcount:
        if total_qty > 0:
            for act_id, qty in executed_by_activity.items():
                share = qty / total_qty
                allocated_hours[act_id] += orphan_hours * share
                allocated_headcount[act_id] += orphan_headcount * share
        elif len(meta_by_activity) == 1:
            only_id = next(iter(meta_by_activity))
            allocated_hours[only_id] += orphan_hours
            allocated_headcount[only_id] += orphan_headcount

    return allocated_hours, allocated_headcount, executed_by_activity, meta_by_activity, labor_qs


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
                'hours_per_headcount': round(data['labor_hours'] / data['headcount_days'], 4)
                if data['headcount_days'] > 0
                else None,
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
                'hours_per_headcount': round(data['labor_hours'] / data['headcount_days'], 4)
                if data['headcount_days'] > 0
                else None,
                'productivity_index': None,
            }
            for cat, data in sorted(by_cat.items())
        ]
        return {
            'group_by': group_by,
            'total_labor_hours': round(total_labor_hours, 2),
            'rows': rows,
        }

    (
        allocated_hours,
        allocated_headcount,
        executed_by_activity,
        meta_by_activity,
        _,
    ) = _allocate_labor_to_activities(project_id, date_from, date_to, activity_id)

    rows = []
    for act_id, executed in executed_by_activity.items():
        if activity_id and str(act_id) != str(activity_id):
            continue
        hours = allocated_hours.get(act_id, 0.0)
        productivity = round(executed / hours, 4) if hours > 0 and executed > 0 else None
        meta = meta_by_activity.get(act_id, {})
        rows.append(
            {
                'activity_id': str(act_id),
                'activity_code': meta.get('activity_code'),
                'activity_name': meta.get('activity_name'),
                'executed_qty': executed,
                'labor_hours': round(hours, 2),
                'productivity_index': productivity,
                'planned_budget_labor': _planned_man_days(project_id, act_id),
                'actual_man_days': round(allocated_headcount.get(act_id, 0.0), 2),
            }
        )
    rows.sort(key=lambda r: (r['activity_code'] or '', r['activity_name'] or ''))

    project_executed = float(sum(executed_by_activity.values()))
    return {
        'group_by': 'activity',
        'total_labor_hours': round(total_labor_hours, 2),
        'total_executed_qty': project_executed,
        'project_productivity_index': round(project_executed / total_labor_hours, 4)
        if total_labor_hours > 0 and project_executed > 0
        else None,
        'rows': rows,
    }

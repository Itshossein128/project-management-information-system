"""Personnel summary pivot data."""

from __future__ import annotations

from datetime import timedelta

import jdatetime
from django.db import models

from common.jalali import gregorian_to_jalali
from field_reports.models import DailyReportLabor, LaborJobTitle, ReportStatus


def _date_range(date_from, date_to, group_by):
    current = date_from
    dates = []
    seen = set()
    while current <= date_to:
        if group_by == 'monthly':
            j = jdatetime.date.fromgregorian(date=current)
            key = f'{j.year}/{j.month:02d}'
        else:
            key = gregorian_to_jalali(current)
        if key not in seen:
            dates.append(key)
            seen.add(key)
        current += timedelta(days=1)
    return dates


def _bucket_key(d, group_by):
    if group_by == 'monthly':
        j = jdatetime.date.fromgregorian(date=d)
        return f'{j.year}/{j.month:02d}'
    return gregorian_to_jalali(d)


def personnel_summary(project_id, date_from, date_to, category='all', group_by='daily'):
    titles_qs = LaborJobTitle.objects.all().order_by('display_order', 'title')
    if category == 'indirect':
        titles_qs = titles_qs.filter(category='indirect')
    elif category == 'direct':
        titles_qs = titles_qs.filter(category='direct')
    job_titles = [t.title for t in titles_qs]

    dates = _date_range(date_from, date_to, group_by)
    data: dict[str, dict[str, float]] = {t: {d: 0 for d in dates} for t in job_titles}

    rows = DailyReportLabor.objects.filter(is_deleted=False).filter(
        models.Q(
            report__project_id=project_id,
            report__status=ReportStatus.APPROVED,
            report__is_deleted=False,
        )
        | models.Q(project_id=project_id, report__isnull=True)
    )
    if category in ('indirect', 'direct'):
        rows = rows.filter(labor_category=category)

    rows = rows.filter(report_date__gte=date_from, report_date__lte=date_to)

    for row in rows:
        title = row.job_title
        if title not in data:
            data[title] = {d: 0 for d in dates}
        key = _bucket_key(row.report_date, group_by)
        if key in data[title]:
            data[title][key] += float(row.total_count or 0)

    totals_by_title = {
        t: round(sum(vals.values()) / max(len([v for v in vals.values() if v > 0]), 1), 2)
        for t, vals in data.items()
    }
    totals_by_date = {d: sum(data[t].get(d, 0) for t in data) for d in dates}

    return {
        'job_titles': job_titles,
        'dates': dates,
        'data': data,
        'totals_by_title': totals_by_title,
        'totals_by_date': totals_by_date,
    }

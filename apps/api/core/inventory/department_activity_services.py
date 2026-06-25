"""
Query helpers for department activity records (grid, export, reports).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import Department, DepartmentActivityRecord

_ALLOWED_ORDERING_FIELDS = {
    'date',
    '-date',
    'created_at',
    '-created_at',
    'updated_at',
    '-updated_at',
    'location',
    '-location',
    'activity_description',
    '-activity_description',
    'contractor',
    '-contractor',
    'unit',
    '-unit',
}


def get_department_activity_queryset(
    project_pk: int,
    query_params: Any,
) -> QuerySet[DepartmentActivityRecord]:
    """Apply list/export filters from query parameters."""
    qs = DepartmentActivityRecord.objects.filter(project_id=project_pk)

    department = query_params.get('department')
    if department:
        valid_departments = {choice[0] for choice in Department.choices}
        if department in valid_departments:
            qs = qs.filter(department=department)
        else:
            return qs.none()

    date_from = query_params.get('date_from')
    date_to = query_params.get('date_to')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    location = query_params.get('location')
    activity_description = query_params.get('activity_description')
    contractor = query_params.get('contractor')
    unit = query_params.get('unit')

    if location:
        qs = qs.filter(location__icontains=location)
    if activity_description:
        qs = qs.filter(activity_description__icontains=activity_description)
    if contractor:
        qs = qs.filter(contractor__icontains=contractor)
    if unit:
        qs = qs.filter(unit__icontains=unit)

    search = query_params.get('search')
    if search:
        qs = qs.filter(
            Q(location__icontains=search)
            | Q(activity_description__icontains=search)
            | Q(contractor__icontains=search)
            | Q(unit__icontains=search)
        )

    ordering = query_params.get('ordering')
    if ordering and ordering in _ALLOWED_ORDERING_FIELDS:
        qs = qs.order_by(ordering, '-created_at')
    else:
        qs = qs.order_by('-date', '-created_at')

    return qs.select_related('business')


def require_valid_department(department: str | None) -> str | None:
    if not department:
        return None
    valid = {choice[0] for choice in Department.choices}
    return department if department in valid else None


def get_report_date_range(period: str) -> tuple[date, date]:
    """
    Daily: previous calendar day. Weekly: rolling last 7 days including today.
    """
    today = timezone.localdate()
    if period == 'daily':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    start = today - timedelta(days=6)
    return start, today

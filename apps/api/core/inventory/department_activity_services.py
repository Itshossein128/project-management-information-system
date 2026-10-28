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
    'executed_quantity',
    '-executed_quantity',
    'unit',
    '-unit',
    'material_type',
    '-material_type',
    'quantity_in',
    '-quantity_in',
    'quantity_out',
    '-quantity_out',
    'consumption_location',
    '-consumption_location',
    'supplier',
    '-supplier',
}


def normalize_department(department: str | None) -> str | None:
    if not department:
        return None
    dept_clean = str(department).strip().lower()
    if dept_clean in ('civil', 'buildings'):
        return 'buildings'
    return dept_clean


def get_department_activity_queryset(
    project_pk: int,
    query_params: Any,
) -> QuerySet[DepartmentActivityRecord]:
    """Apply list/export filters from query parameters."""
    qs = DepartmentActivityRecord.objects.filter(project_id=project_pk)

    department = query_params.get('department')
    if department:
        dept_clean = str(department).strip().lower()
        if dept_clean in ('civil', 'buildings'):
            qs = qs.filter(department__in=['buildings', 'civil'])
        else:
            valid_departments = {choice[0] for choice in Department.choices}
            if dept_clean in valid_departments:
                qs = qs.filter(department=dept_clean)
            else:
                return qs.none()

    from common.jalali import parse_date_optional

    date_from = parse_date_optional(query_params.get('date_from'))
    date_to = parse_date_optional(query_params.get('date_to'))
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    location = query_params.get('location')
    activity_description = query_params.get('activity_description')
    contractor = query_params.get('contractor')
    contractor_ref = query_params.get('contractor_ref')
    unit = query_params.get('unit')
    material_type = query_params.get('material_type')
    consumption_location = query_params.get('consumption_location')
    supplier = query_params.get('supplier')

    if location:
        qs = qs.filter(location__icontains=location)
    if activity_description:
        qs = qs.filter(activity_description__icontains=activity_description)
    if contractor_ref:
        qs = qs.filter(contractor_ref_id=contractor_ref)
    elif contractor:
        qs = qs.filter(contractor__icontains=contractor)
    if unit:
        qs = qs.filter(unit__icontains=unit)
    if material_type:
        qs = qs.filter(material_type__icontains=material_type)
    if consumption_location:
        qs = qs.filter(consumption_location__icontains=consumption_location)
    if supplier:
        qs = qs.filter(supplier__icontains=supplier)

    search = query_params.get('search')
    if search:
        qs = qs.filter(
            Q(location__icontains=search)
            | Q(activity_description__icontains=search)
            | Q(contractor__icontains=search)
            | Q(unit__icontains=search)
            | Q(material_type__icontains=search)
            | Q(consumption_location__icontains=search)
            | Q(supplier__icontains=search)
            | Q(description__icontains=search)
        )

    ordering = query_params.get('ordering')
    if ordering and ordering in _ALLOWED_ORDERING_FIELDS:
        qs = qs.order_by(ordering, '-created_at')
    else:
        qs = qs.order_by('-date', '-created_at')

    return qs.select_related('project')


def require_valid_department(department: str | None) -> str | None:
    if not department:
        return None
    dept_clean = str(department).strip().lower()
    if dept_clean in ('civil', 'buildings'):
        return 'buildings'
    valid = {choice[0] for choice in Department.choices}
    return dept_clean if dept_clean in valid else None


def get_report_date_range(period: str, anchor_date: date | None = None) -> tuple[date, date]:
    """
    Daily: given date or previous calendar day.
    Weekly: given week_start through week_start + 6 days, or rolling last 7 days including today.
    """
    today = timezone.localdate()
    if period == 'daily':
        if anchor_date:
            return anchor_date, anchor_date
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday

    if anchor_date:
        return anchor_date, anchor_date + timedelta(days=6)
    start = today - timedelta(days=6)
    return start, today

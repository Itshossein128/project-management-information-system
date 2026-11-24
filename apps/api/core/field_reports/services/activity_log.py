"""Activity log selection shared by the list, filter options, and FILE1."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.utils.translation import get_language
from rest_framework.exceptions import ValidationError

from common.jalali import gregorian_to_jalali, parse_jalali_or_gregorian
from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
from projects.models import Activity, Stakeholder

RECORDED_UNIT = Q(unit__regex=r'\S')
MEASURED_QUANTITY = Q(quantity_measured=True, quantity__isnull=False) & RECORDED_UNIT


def scoped_filter_id(model, project_id, value):
    """Resolve identities from the authorized project only."""
    try:
        identity = UUID(str(value))
    except ValueError:
        return None
    return model.objects.filter(project_id=project_id, pk=identity, is_deleted=False).values_list('pk', flat=True).first()


def invalid_filter(field):
    if (get_language() or '').startswith('fa'):
        return ValidationError({field: 'مقدار فیلتر برای این پروژه معتبر نیست.'})
    return ValidationError({field: 'This filter value is invalid for this project.'})


def activity_log_selection(project_id, params):
    """Return a queryset and the normalized selection used for its cache identity."""
    filters = {}
    for parameter, lookup in (
        ('zone', 'zone'), ('block', 'block'), ('floor', 'floor'), ('shift', 'shift'),
        ('status', 'report__status'), ('unit', 'unit'),
        ('location', 'location_detail__icontains'), ('subcontractor', 'subcontractor_name__icontains'),
    ):
        value = params.get(parameter)
        if value:
            filters[lookup] = value.lower() if lookup.endswith('__icontains') else value

    for parameter, lookup, model in (
        ('contractor_id', 'contractor_ref_id', Stakeholder),
        ('activity_id', 'activity_ref_id', Activity),
        ('report_id', 'report_id', DailyReport),
    ):
        if params.get(parameter):
            identity = scoped_filter_id(model, project_id, params[parameter])
            if identity is None:
                raise invalid_filter(parameter)
            filters[lookup] = identity

    if params.get('headcount'):
        try:
            headcount = int(params['headcount'])
            if not 0 <= headcount <= 2147483647:
                raise ValueError
        except ValueError as error:
            raise invalid_filter('headcount') from error
        filters['headcount'] = headcount

    for parameter, bound in (('date_from', 'gte'), ('date_to', 'lte')):
        if params.get(parameter):
            try:
                filters[f'report__report_date__{bound}'] = parse_jalali_or_gregorian(params[parameter])
            except (ValueError, OverflowError) as error:
                raise invalid_filter(parameter) from error

    approved_only = params.get('approved_only', 'true').lower() != 'false'
    qs = DailyReportActivity.objects.filter(
        report__project_id=project_id, report__is_current=True, report__is_deleted=False, is_deleted=False,
        **filters,
    ).select_related('report', 'activity_ref', 'contractor_ref')
    if approved_only:
        qs = qs.filter(report__status=ReportStatus.APPROVED)
    fingerprint = {**filters, 'approved_only': approved_only}

    for field, raw in (
        ('source_discipline', params.get('source_discipline') or params.get('discipline')),
        ('parcel', params.get('parcel')),
    ):
        values = sorted({value.strip().lower() for value in (raw or '').split(',') if value.strip()})
        if values:
            alternatives = Q()
            for value in values:
                alternatives |= Q(**{f'{field}__iexact': value})
            qs = qs.filter(alternatives)
            fingerprint[field] = values

    search = (params.get('q') or '').strip().lower()
    if search:
        qs = qs.filter(
            Q(activity_description__icontains=search)
            | Q(activity_ref__project_id=project_id, activity_ref__activity_code__icontains=search)
        )
        fingerprint['q'] = search

    if params.get('quantity'):
        try:
            quantity = Decimal(params['quantity'])
            if not quantity.is_finite() or quantity.adjusted() > 13 or quantity != quantity.quantize(Decimal('0.0001')):
                raise ValueError
        except (InvalidOperation, ValueError) as error:
            raise invalid_filter('quantity') from error
        qs = qs.filter(MEASURED_QUANTITY, quantity=quantity)
        fingerprint['quantity'] = str(quantity.normalize())

    return qs.order_by('-report__report_date', 'id'), fingerprint


def activity_log_queryset(project_id, params):
    queryset, _ = activity_log_selection(project_id, params)
    return queryset


def activity_log_aggregates(queryset):
    groups = queryset.order_by().values('unit').annotate(
        row_count=Count('pk'),
        headcount=Sum('headcount'),
        measured_count=Count('pk', filter=MEASURED_QUANTITY),
        total=Sum('quantity', filter=MEASURED_QUANTITY),
    ).order_by('unit')
    headcount_sum = 0
    missing_unit = 0
    quantities = []
    for group in groups:
        headcount_sum += group['headcount'] or 0
        unit = group['unit']
        count = group['row_count']
        if not unit or not unit.strip():
            missing_unit += count
            continue
        measured = group['measured_count']
        total = group['total']
        quantities.append({
            'unit': unit,
            'total': format(total, 'f') if total is not None else None,
            'measured_count': measured,
            'unknown_count': count - measured,
        })
    return {
        'headcount_sum': headcount_sum,
        'quantity_by_unit': quantities,
        'unknown_quantity_without_unit_count': missing_unit,
    }


def measured_activity_quantity(row):
    if row.quantity_measured and row.quantity is not None and row.unit and row.unit.strip():
        return row.quantity
    return None


def activity_contractor(row):
    contractor = row.contractor_ref if row.contractor_ref_id else None
    return contractor if contractor and contractor.project_id == row.report.project_id else None


def serialize_activity_log_row(row: DailyReportActivity) -> dict:
    report = row.report
    contractor = activity_contractor(row)
    quantity = measured_activity_quantity(row)
    activity = row.activity_ref if row.activity_ref_id else None
    if activity and activity.project_id != report.project_id:
        activity = None
    return {
        'id': str(row.id),
        'report_id': str(report.id),
        'report_date': gregorian_to_jalali(report.report_date),
        'day_name': report.report_date.strftime('%A'),
        'source_discipline': row.source_discipline or '',
        'parcel': row.parcel or '',
        'activity_description': row.activity_description,
        'shift': row.shift,
        'subcontractor': contractor.name if contractor else row.subcontractor_name,
        'contractor_id': str(contractor.pk) if contractor else None,
        'headcount': row.headcount,
        'zone': row.zone,
        'block': row.block,
        'floor': row.floor,
        'location': row.location_detail,
        'quantity': float(quantity) if quantity is not None else None,
        'quantity_measured': quantity is not None,
        'unit': row.unit,
        'activity_code': activity.activity_code if activity else None,
        'activity_name': activity.activity_name if activity else None,
        'report_status': report.status,
    }


def invalidate_activity_log_cache(project_id):
    # Unique generations also keep an in-flight request from repopulating the new cache.
    cache.set(f'activity_log_version:{project_id}', uuid4().hex, 86400 * 30)

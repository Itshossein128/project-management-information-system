"""Activity log query service."""

from __future__ import annotations

from common.jalali import parse_jalali_or_gregorian
from field_reports.models import DailyReportActivity, ReportStatus


def activity_log_queryset(project_id, params):
    qs = DailyReportActivity.objects.filter(
        report__project_id=project_id,
        is_deleted=False,
    ).select_related('report', 'activity_ref')

    if params.get('approved_only', 'true').lower() != 'false':
        qs = qs.filter(report__status=ReportStatus.APPROVED, report__is_deleted=False)

    if params.get('date_from'):
        qs = qs.filter(report__report_date__gte=parse_jalali_or_gregorian(params['date_from']))
    if params.get('date_to'):
        qs = qs.filter(report__report_date__lte=parse_jalali_or_gregorian(params['date_to']))
    if params.get('subcontractor'):
        qs = qs.filter(subcontractor_name__icontains=params['subcontractor'])
    if params.get('zone'):
        qs = qs.filter(zone=params['zone'])
    if params.get('block'):
        qs = qs.filter(block=params['block'])
    if params.get('floor'):
        qs = qs.filter(floor=params['floor'])
    if params.get('shift'):
        qs = qs.filter(shift=params['shift'])
    if params.get('activity_id'):
        qs = qs.filter(activity_ref_id=params['activity_id'])

    disc_param = params.get('source_discipline') or params.get('discipline')
    if disc_param:
        discs = [d.strip() for d in disc_param.split(',') if d.strip()]
        if len(discs) == 1:
            qs = qs.filter(source_discipline__iexact=discs[0])
        elif len(discs) > 1:
            from django.db.models import Q
            q_obj = Q()
            for d in discs:
                q_obj |= Q(source_discipline__iexact=d)
            qs = qs.filter(q_obj)

    parcel_param = params.get('parcel')
    if parcel_param:
        parcels = [p.strip() for p in parcel_param.split(',') if p.strip()]
        if len(parcels) == 1:
            qs = qs.filter(parcel__iexact=parcels[0])
        elif len(parcels) > 1:
            from django.db.models import Q
            q_obj = Q()
            for p in parcels:
                q_obj |= Q(parcel__iexact=p)
            qs = qs.filter(q_obj)

    return qs.order_by('-report__report_date', 'id')


def serialize_activity_log_row(row: DailyReportActivity) -> dict:
    from common.jalali import gregorian_to_jalali

    report = row.report
    return {
        'id': str(row.id),
        'report_id': str(report.id),
        'report_date': gregorian_to_jalali(report.report_date),
        'day_name': report.report_date.strftime('%A'),
        'source_discipline': row.source_discipline or '',
        'parcel': row.parcel or '',
        'activity_description': row.activity_description,
        'shift': row.shift,
        'subcontractor': row.subcontractor_name,
        'headcount': row.headcount,
        'zone': row.zone,
        'block': row.block,
        'floor': row.floor,
        'location': row.location_detail,
        'quantity': float(row.quantity) if row.quantity is not None else None,
        'unit': row.unit,
        'activity_code': row.activity_ref.activity_code if row.activity_ref_id else None,
        'activity_name': row.activity_ref.activity_name if row.activity_ref_id else None,
        'report_status': report.status,
    }


def invalidate_activity_log_cache(project_id):
    from django.conf import settings
    from django.core.cache import cache
    from django.utils import timezone

    version_key = f'activity_log_version:{project_id}'
    try:
        if cache.get(version_key) is None:
            cache.set(version_key, 1, 86400 * 30)
        else:
            cache.incr(version_key)
    except Exception:
        cache.set(version_key, int(timezone.now().timestamp()), 86400 * 30)

    try:
        import redis
        redis_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
        client = redis.from_url(redis_url, decode_responses=True)
        pattern = f'*activity_log:{project_id}:*'
        keys = list(client.scan_iter(match=pattern, count=100))
        if keys:
            client.delete(*keys)
    except Exception:
        pass

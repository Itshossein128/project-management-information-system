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

    return qs.order_by('-report__report_date', '-created_at')


def serialize_activity_log_row(row: DailyReportActivity) -> dict:
    from common.jalali import gregorian_to_jalali

    report = row.report
    return {
        'id': str(row.id),
        'report_id': str(report.id),
        'report_date': gregorian_to_jalali(report.report_date),
        'day_name': report.report_date.strftime('%A'),
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

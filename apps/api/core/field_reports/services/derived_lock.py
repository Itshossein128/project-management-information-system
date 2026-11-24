"""Ownership-based guards for derived daily-report rows."""
from rest_framework.exceptions import ValidationError

from field_reports.models import DailyReportDerivedSource, ReportStatus
from field_reports.services.lifecycle_errors import lifecycle_error_detail


def is_derived_row(row, report=None) -> bool:
    if row is None:
        return False
    if bool(getattr(row, 'is_derived', False)):
        return True
    if getattr(row, 'source_sub_report_id', None) or getattr(row, 'source_report_id', None):
        return True
    row_report = report or getattr(row, 'report', None)
    return bool(row_report and DailyReportDerivedSource.objects.filter(
        daily_report=row_report, derived_row_id=str(row.pk),
    ).exists())


def report_has_derived_rows(report) -> bool:
    if not report:
        return False
    if report.is_auto_summary or DailyReportDerivedSource.objects.filter(daily_report=report).exists():
        return True
    related_names = ('activities', 'labor_entries', 'equipment_entries', 'material_entries',
                     'concrete_logs', 'machinery_rows', 'general_activities', 'visits', 'incidents')
    for name in related_names:
        manager = getattr(report, name, None)
        if manager is None:
            continue
        qs = manager.filter(is_deleted=False)
        field_names = {field.name for field in manager.model._meta.get_fields()}
        if 'is_derived' in field_names and qs.filter(is_derived=True).exists():
            return True
        if 'source_sub_report' in field_names and qs.filter(source_sub_report__isnull=False).exists():
            return True
        if name == 'incidents' and qs.filter(source_report__isnull=False).exists():
            return True
    return False


def _reject(code, request=None):
    raise ValidationError({'detail': lifecycle_error_detail(code, request=request), 'code': code})


def assert_report_editable(report, request=None):
    if report.is_deleted:
        _reject('report_not_current', request)
    if not report.is_current:
        _reject('report_not_current', request)
    if report.status == ReportStatus.APPROVED:
        _reject('report_locked', request)
    if report.status not in (ReportStatus.DRAFT, ReportStatus.REJECTED):
        _reject('report_not_editable', request)


def assert_child_row_mutable(report, row=None, request=None):
    assert_report_editable(report, request)
    if is_derived_row(row, report=report) or report_has_derived_rows(report):
        _reject('derived_collection_read_only', request)

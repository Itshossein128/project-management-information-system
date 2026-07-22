"""Business logic for the daily-report workflow and offline sync-batch."""
import logging

from django.db import transaction
from django.utils import timezone

from common.jalali import parse_jalali_or_gregorian
from field_reports.models import DailyReport, ReportStatus

logger = logging.getLogger(__name__)

CHILD_SERIALIZER_MAP = {
    'activities': 'DailyReportActivitySerializer',
    'labor': 'DailyReportLaborSerializer',
    'equipment': 'DailyReportEquipmentSerializer',
    'materials': 'DailyReportMaterialSerializer',
    'concrete_logs': 'DailyReportConcreteLogSerializer',
    'labor_camp': 'DailyReportLaborCampSerializer',
    'incidents': 'DailyReportIncidentSerializer',
}


# ---------------------------------------------------------------------------
# Workflow transitions
# ---------------------------------------------------------------------------


def submit_report(report: DailyReport, user) -> DailyReport:
    report.status = ReportStatus.SUBMITTED
    report.submitted_by = user
    report.submitted_at = timezone.now()
    report.rejection_reason = ''
    report.updated_by = user
    report.save(
        update_fields=[
            'status',
            'submitted_by',
            'submitted_at',
            'rejection_reason',
            'updated_by',
            'updated_at',
        ],
    )
    _notify_submitted(report, actor=user)
    return report


def review_report(report: DailyReport, user, notes: str = '') -> DailyReport:
    report.status = ReportStatus.UNDER_REVIEW
    report.reviewed_by = user
    report.reviewed_at = timezone.now()
    report.updated_by = user
    update_fields = ['status', 'reviewed_by', 'reviewed_at', 'updated_by', 'updated_at']
    if notes:
        # Persist reviewer notes on the report header until a dedicated field exists.
        suffix = f'\n[بررسی] {notes.strip()}'
        report.general_notes = (report.general_notes or '') + suffix
        update_fields.append('general_notes')
    report.save(update_fields=update_fields)
    return report


def approve_report(report: DailyReport, user) -> DailyReport:
    report.status = ReportStatus.APPROVED
    report.approved_by = user
    report.approved_at = timezone.now()
    report.updated_by = user
    report.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])

    _publish_approved(report)
    _enqueue_progress_recalc(report)
    _notify_approved(report)
    return report


def reject_report(report: DailyReport, user, reason: str) -> DailyReport:
    report.status = ReportStatus.REJECTED
    report.rejection_reason = reason
    report.reviewed_by = user
    report.reviewed_at = timezone.now()
    report.updated_by = user
    report.save(
        update_fields=[
            'status', 'rejection_reason', 'reviewed_by', 'reviewed_at', 'updated_by', 'updated_at',
        ],
    )
    _notify_rejected(report)
    return report


# ---------------------------------------------------------------------------
# Offline sync-batch
# ---------------------------------------------------------------------------


def _child_serializers():
    from field_reports import serializers as s

    return {key: getattr(s, name) for key, name in CHILD_SERIALIZER_MAP.items()}


MERGEABLE_STATUSES = {ReportStatus.DRAFT, ReportStatus.REJECTED}

HEADER_COMPARE_FIELDS = (
    'report_date',
    'shift',
    'weather_condition',
    'temp_min',
    'temp_max',
    'site_status',
    'general_notes',
)

CHILD_RELATED_NAMES = {
    'activities': 'activities',
    'labor': 'labor_entries',
    'equipment': 'equipment_entries',
    'materials': 'material_entries',
    'concrete_logs': 'concrete_logs',
    'labor_camp': 'labor_camp_entries',
    'incidents': 'incidents',
}


def _report_conflict_snapshot(report: DailyReport) -> dict:
    from field_reports.serializers import DailyReportDetailSerializer

    return DailyReportDetailSerializer(report).data


def _diff_conflict_fields(snapshot: dict, payload: dict) -> list[str]:
    fields: list[str] = []
    for key in HEADER_COMPARE_FIELDS:
        if key not in payload:
            continue
        client_val = payload.get(key)
        server_val = snapshot.get(key)
        if client_val is None and server_val in (None, ''):
            continue
        if key == 'report_date':
            try:
                client_date = parse_jalali_or_gregorian(client_val) if client_val else None
                server_date = parse_jalali_or_gregorian(server_val) if server_val else None
            except (ValueError, TypeError):
                client_date = client_val
                server_date = server_val
            if client_date != server_date:
                fields.append(key)
            continue
        if str(client_val) != str(server_val):
            fields.append(key)
    return fields


def _conflict_result(local_id, report: DailyReport, payload: dict, reason: str) -> dict:
    from field_reports.services.sync_conflict_service import log_sync_conflict

    log_sync_conflict(report.project_id, local_id, report.id, reason)
    snapshot = _report_conflict_snapshot(report)
    return {
        'local_id': local_id,
        'status': 'conflict',
        'server_id': str(report.id),
        'conflict_reason': reason,
        'server_payload': snapshot,
        'conflict_fields': _diff_conflict_fields(snapshot, payload),
        'child_errors': [],
    }


def _apply_header_merge(report: DailyReport, payload: dict, user, local_id) -> list[dict] | None:
    """Apply offline header fields onto a mergeable report. Returns error child_errors or None."""
    from field_reports.serializers import DailyReportHeaderSerializer

    header = DailyReportHeaderSerializer(report, data=payload, partial=True)
    if not header.is_valid():
        return [{'section': 'header', 'errors': header.errors}]

    update_kwargs = {'synced_from_offline': True, 'updated_by': user}
    if local_id and not report.local_id:
        update_kwargs['local_id'] = local_id
    header.save(**update_kwargs)
    return None


def _child_sections_in_payload(payload) -> list[str]:
    return [key for key in CHILD_SERIALIZER_MAP if key in payload]


def _clear_child_sections(report, section_keys: list[str]) -> None:
    for key in section_keys:
        related = getattr(report, CHILD_RELATED_NAMES[key])
        related.all().delete()


def _create_children(report, payload, sections: list[str] | None = None) -> list[dict]:
    serializers_map = _child_serializers()
    child_errors = []
    keys = sections if sections is not None else list(CHILD_SERIALIZER_MAP.keys())
    for key in keys:
        serializer_cls = serializers_map[key]
        rows = payload.get(key) or []
        for idx, row in enumerate(rows):
            serializer = serializer_cls(data=row)
            if serializer.is_valid():
                serializer.save(report=report)
            else:
                child_errors.append({'section': key, 'index': idx, 'errors': serializer.errors})
                logger.warning('sync-batch skipped invalid %s row: %s', key, serializer.errors)
    return child_errors


def _replace_children(report, payload) -> list[dict]:
    sections = _child_sections_in_payload(payload)
    if sections:
        _clear_child_sections(report, sections)
    return _create_children(report, payload, sections=sections or None)


def sync_batch(project_id, user, reports: list) -> dict:
    from field_reports.serializers import DailyReportHeaderSerializer
    from field_reports.services.sync_conflict_service import resolve_sync_conflict

    results = []
    counts = {'created': 0, 'merged': 0, 'skipped': 0, 'conflicts': 0, 'errors': 0}
    seen_local_ids: set[str] = set()

    for item in reports:
        local_id = item.get('local_id')
        if local_id:
            if local_id in seen_local_ids:
                results.append({
                    'local_id': local_id,
                    'status': 'skipped',
                    'server_id': None,
                    'conflict_reason': 'تکراری در همان دسته',
                    'server_payload': None,
                    'conflict_fields': [],
                    'child_errors': [],
                })
                counts['skipped'] += 1
                continue
            seen_local_ids.add(local_id)

        raw_date = item.get('report_date')
        try:
            report_date = parse_jalali_or_gregorian(raw_date) if raw_date else None
        except (ValueError, TypeError):
            report_date = None

        if report_date is None:
            results.append({
                'local_id': local_id,
                'status': 'error',
                'server_id': None,
                'conflict_reason': 'تاریخ نامعتبر',
                'server_payload': None,
                'conflict_fields': [],
                'child_errors': [{'section': 'header', 'errors': {'report_date': ['تاریخ نامعتبر']}}],
            })
            counts['errors'] += 1
            continue

        shift = item.get('shift') or 'full'

        existing = None
        if local_id:
            existing = DailyReport.objects.filter(
                project_id=project_id, local_id=local_id, is_deleted=False,
            ).first()
        if existing is None:
            existing = DailyReport.objects.filter(
                project_id=project_id,
                report_date=report_date,
                shift=shift,
                is_deleted=False,
            ).first()

        if existing and existing.status == ReportStatus.APPROVED:
            results.append(_conflict_result(
                local_id, existing, item,
                'گزارش تأیید شده برای این تاریخ وجود دارد',
            ))
            counts['conflicts'] += 1
            continue

        if existing and existing.status not in MERGEABLE_STATUSES:
            results.append(_conflict_result(
                local_id, existing, item,
                'گزارش در وضعیت غیرقابل ادغام است',
            ))
            counts['conflicts'] += 1
            continue

        with transaction.atomic():
            if existing:
                header_errors = _apply_header_merge(existing, item, user, local_id)
                if header_errors is not None:
                    results.append({
                        'local_id': local_id,
                        'status': 'error',
                        'server_id': str(existing.id),
                        'conflict_reason': 'اطلاعات سربرگ نامعتبر',
                        'server_payload': None,
                        'conflict_fields': [],
                        'child_errors': header_errors,
                    })
                    counts['errors'] += 1
                    continue
                existing.refresh_from_db()
                child_errors = _replace_children(existing, item)
                results.append({
                    'local_id': local_id,
                    'status': 'merged',
                    'server_id': str(existing.id),
                    'conflict_reason': None,
                    'server_payload': None,
                    'conflict_fields': [],
                    'child_errors': child_errors,
                })
                counts['merged'] += 1
                resolve_sync_conflict(project_id, local_id=local_id, daily_report_id=existing.id)
            else:
                header = DailyReportHeaderSerializer(data=item)
                if not header.is_valid():
                    results.append({
                        'local_id': local_id,
                        'status': 'error',
                        'server_id': None,
                        'conflict_reason': 'اطلاعات سربرگ نامعتبر',
                        'server_payload': None,
                        'conflict_fields': [],
                        'child_errors': [{'section': 'header', 'errors': header.errors}],
                    })
                    counts['errors'] += 1
                    continue
                report = header.save(
                    project_id=project_id,
                    prepared_by=user,
                    created_by=user,
                    updated_by=user,
                    synced_from_offline=True,
                    local_id=local_id,
                )
                child_errors = _create_children(report, item)
                results.append({
                    'local_id': local_id,
                    'status': 'created',
                    'server_id': str(report.id),
                    'conflict_reason': None,
                    'server_payload': None,
                    'conflict_fields': [],
                    'child_errors': child_errors,
                })
                counts['created'] += 1
                resolve_sync_conflict(project_id, local_id=local_id, daily_report_id=report.id)

    return {'results': results, 'summary': counts}


# ---------------------------------------------------------------------------
# Events / notifications (best-effort; safe before infra is up)
# ---------------------------------------------------------------------------


def _publish_approved(report):
    try:
        from events.publisher import EventPublisher

        EventPublisher().publish(
            'daily-report.approved',
            {'report_id': str(report.id), 'report_date': str(report.report_date)},
            project_id=str(report.project_id),
        )
    except Exception:  # noqa: BLE001 - event bus is optional in dev
        logger.warning('Could not publish daily-report.approved for %s', report.id, exc_info=True)


def _enqueue_progress_recalc(report):
    try:
        from field_reports.tasks import recalculate_activity_progress

        recalculate_activity_progress.delay(str(report.id))
    except Exception:  # noqa: BLE001 - broker optional in dev/tests
        logger.warning('Could not enqueue progress recalc for %s', report.id, exc_info=True)


def _report_link(report):
    return f'/projects/{report.project_id}/daily-reports/{report.id}/view'


def _notify_submitted(report, actor):
    from field_reports.tasks import notify_report_event

    notify_report_event(
        event='submitted',
        report_id=str(report.id),
        project_id=str(report.project_id),
    )


def _notify_approved(report):
    from field_reports.tasks import notify_report_event

    notify_report_event(
        event='approved',
        report_id=str(report.id),
        project_id=str(report.project_id),
    )


def _notify_rejected(report):
    from field_reports.tasks import notify_report_event

    notify_report_event(
        event='rejected',
        report_id=str(report.id),
        project_id=str(report.project_id),
    )

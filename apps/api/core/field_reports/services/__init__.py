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
    report.updated_by = user
    report.save(update_fields=['status', 'submitted_by', 'submitted_at', 'updated_by', 'updated_at'])
    _notify_submitted(report, actor=user)
    return report


def review_report(report: DailyReport, user, notes: str = '') -> DailyReport:
    report.status = ReportStatus.UNDER_REVIEW
    report.reviewed_by = user
    report.reviewed_at = timezone.now()
    report.updated_by = user
    report.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_by', 'updated_at'])
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


def _create_children(report, payload) -> list[dict]:
    serializers_map = _child_serializers()
    child_errors = []
    for key, serializer_cls in serializers_map.items():
        rows = payload.get(key) or []
        for idx, row in enumerate(rows):
            serializer = serializer_cls(data=row)
            if serializer.is_valid():
                serializer.save(report=report)
            else:
                child_errors.append({'section': key, 'index': idx, 'errors': serializer.errors})
                logger.warning('sync-batch skipped invalid %s row: %s', key, serializer.errors)
    return child_errors


def sync_batch(project_id, user, reports: list) -> dict:
    from field_reports.serializers import DailyReportHeaderSerializer

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
                'status': 'conflict',
                'server_id': None,
                'conflict_reason': 'تاریخ نامعتبر',
                'child_errors': [],
            })
            counts['conflicts'] += 1
            continue

        existing = None
        if local_id:
            existing = DailyReport.objects.filter(
                project_id=project_id, local_id=local_id, is_deleted=False,
            ).first()
        if existing is None:
            existing = DailyReport.objects.filter(
                project_id=project_id, report_date=report_date, is_deleted=False,
            ).first()

        if existing and existing.status == ReportStatus.APPROVED:
            results.append({
                'local_id': local_id,
                'status': 'conflict',
                'server_id': str(existing.id),
                'conflict_reason': 'گزارش تأیید شده برای این تاریخ وجود دارد',
                'child_errors': [],
            })
            counts['conflicts'] += 1
            continue

        if existing and existing.status not in MERGEABLE_STATUSES:
            results.append({
                'local_id': local_id,
                'status': 'conflict',
                'server_id': str(existing.id),
                'conflict_reason': 'گزارش در وضعیت غیرقابل ادغام است',
                'child_errors': [],
            })
            counts['conflicts'] += 1
            continue

        with transaction.atomic():
            if existing:
                child_errors = _create_children(existing, item)
                existing.synced_from_offline = True
                existing.updated_by = user
                if local_id and not existing.local_id:
                    existing.local_id = local_id
                    existing.save(update_fields=['synced_from_offline', 'updated_by', 'updated_at', 'local_id'])
                else:
                    existing.save(update_fields=['synced_from_offline', 'updated_by', 'updated_at'])
                results.append({
                    'local_id': local_id,
                    'status': 'merged',
                    'server_id': str(existing.id),
                    'conflict_reason': None,
                    'child_errors': child_errors,
                })
                counts['merged'] += 1
            else:
                header = DailyReportHeaderSerializer(data=item)
                if not header.is_valid():
                    results.append({
                        'local_id': local_id,
                        'status': 'error',
                        'server_id': None,
                        'conflict_reason': 'اطلاعات سربرگ نامعتبر',
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
                    'child_errors': child_errors,
                })
                counts['created'] += 1

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

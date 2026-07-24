"""Track unresolved offline sync conflicts for alerts."""

from django.utils import timezone

from field_reports.models import SyncConflictLog


def log_sync_conflict(project_id, local_id, daily_report_id, reason: str):
    SyncConflictLog.objects.get_or_create(
        project_id=project_id,
        local_id=local_id or '',
        daily_report_id=daily_report_id,
        resolved_at__isnull=True,
        defaults={'conflict_reason': reason},
    )


def resolve_sync_conflict(project_id, local_id=None, daily_report_id=None):
    qs = SyncConflictLog.objects.filter(project_id=project_id, resolved_at__isnull=True)
    if local_id:
        qs = qs.filter(local_id=local_id)
    elif daily_report_id:
        qs = qs.filter(daily_report_id=daily_report_id)
    else:
        return 0
    return qs.update(resolved_at=timezone.now())

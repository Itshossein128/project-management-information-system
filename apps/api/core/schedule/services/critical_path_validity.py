"""Critical-path validity gate (no full CPM rewrite)."""

from __future__ import annotations

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule

NEAR_CRITICAL_FLOAT_DAYS = 5
MESSAGE_KEY = 'schedule.critical_path_not_valid'


def _has_known_duration(activity: Activity) -> bool:
    if activity.is_milestone and activity.duration_days == 0:
        return True
    return activity.duration_days is not None


def _import_omitted_links(project_id) -> bool:
    from schedule.services.import_fidelity import OMITTED_LINK_CODES
    from schedule.models import MspImportJob, P6ImportJob

    for model in (MspImportJob, P6ImportJob):
        job = (
            model.objects.filter(project_id=project_id, status='done')
            .order_by('-created_at')
            .first()
        )
        if job is None:
            continue
        for warning in (job.result or {}).get('warnings') or []:
            code = str(warning).split(':', 1)[0]
            if code in OMITTED_LINK_CODES:
                return True
    return False


def evaluate_critical_path_validity(project_id) -> dict:
    activities = list(
        Activity.objects.filter(project_id=project_id, is_deleted=False),
    )
    reason_codes: list[str] = []

    incomplete = [a for a in activities if not _has_known_duration(a)]
    if incomplete:
        reason_codes.append('incomplete_durations')
    if _import_omitted_links(project_id):
        reason_codes.append('omitted_relationships')

    valid = len(reason_codes) == 0

    critical_ids: list[str] = []
    near_critical_ids: list[str] = []

    if valid and activities:
        baseline = BaselineSchedule.objects.filter(
            project_id=project_id,
            is_current=True,
        ).first()
        if baseline:
            for ba in BaselineActivity.objects.filter(baseline=baseline).select_related('activity'):
                if ba.activity_id is None:
                    continue
                aid = str(ba.activity_id)
                if ba.is_critical:
                    critical_ids.append(aid)
                elif ba.total_float is not None and ba.total_float <= NEAR_CRITICAL_FLOAT_DAYS:
                    near_critical_ids.append(aid)

    return {
        'valid': valid,
        'reason_codes': reason_codes,
        'message_key': MESSAGE_KEY if not valid else None,
        'critical_activity_ids': critical_ids if valid else [],
        'near_critical_activity_ids': near_critical_ids if valid else [],
    }

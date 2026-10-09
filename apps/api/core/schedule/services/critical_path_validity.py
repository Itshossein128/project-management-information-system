"""Critical-path validity gate (no full CPM rewrite)."""

from __future__ import annotations

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule

NEAR_CRITICAL_FLOAT_DAYS = 5
MESSAGE_KEY = 'schedule.critical_path_not_valid'


def _has_known_duration(activity: Activity) -> bool:
    if activity.duration_days is not None:
        return True
    if activity.is_milestone:
        return True
    if activity.planned_start and activity.planned_finish:
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

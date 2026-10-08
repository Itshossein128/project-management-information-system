"""Baseline snapshot create, approve-lock, and locked mutation guards."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from config.exceptions import ConflictError
from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule


def list_baselines(project_id):
    return BaselineSchedule.objects.filter(project_id=project_id).order_by('-approved_at', '-id')


def _snapshot_activities(baseline: BaselineSchedule, project_id) -> None:
    """Create BaselineActivity rows from live activities. Caller must ensure unlocked."""
    rows = []
    for act in Activity.objects.filter(project_id=project_id, is_deleted=False):
        duration = act.duration_days
        if duration is None and act.planned_start and act.planned_finish:
            duration = (act.planned_finish - act.planned_start).days + 1
        rows.append(
            BaselineActivity(
                baseline=baseline,
                activity=act,
                planned_start=act.planned_start,
                planned_finish=act.planned_finish,
                planned_duration=duration,
                planned_quantity=act.total_quantity,
            )
        )
    if rows:
        BaselineActivity.objects.bulk_create(rows)


@transaction.atomic
def create_baseline_snapshot(
    *,
    project_id,
    version_name: str,
    user=None,
    make_current: bool = False,
    source_change_request=None,
    is_locked: bool = False,
) -> BaselineSchedule:
    if user is None:
        raise ValueError('user is required to create a baseline snapshot (audit created_by).')
    baseline = BaselineSchedule(
        project_id=project_id,
        version_name=version_name or '',
        is_current=bool(make_current),
        is_locked=False,
        source_change_request=source_change_request,
        created_by=user,
        updated_by=user,
    )
    baseline.save()
    _snapshot_activities(baseline, project_id)

    if is_locked:
        return approve_lock_baseline(baseline, user)

    return baseline


@transaction.atomic
def soft_delete_baseline(baseline: BaselineSchedule, user=None) -> None:
    """Soft-delete baseline (locked or unlocked). Hard delete is never used."""
    if baseline.is_current:
        baseline.is_current = False
        baseline.save(update_fields=['is_current', 'updated_at'])
    baseline.soft_delete(user=user)


@transaction.atomic
def approve_lock_baseline(baseline: BaselineSchedule, user) -> BaselineSchedule:
    if baseline.is_locked:
        raise ConflictError('Baseline is already locked.', code='baseline_already_locked')

    now = timezone.now()
    BaselineSchedule.objects.filter(
        project_id=baseline.project_id,
        is_current=True,
    ).exclude(pk=baseline.pk).update(is_current=False)

    baseline.is_locked = True
    baseline.locked_at = now
    baseline.locked_by = user
    baseline.approved_at = now.date()
    baseline.approved_by = user
    baseline.is_current = True
    baseline.save()
    return baseline


def assert_baseline_mutable(baseline: BaselineSchedule) -> None:
    if baseline.is_locked:
        raise ConflictError('Baseline is locked and cannot be modified.', code='baseline_locked')


@transaction.atomic
def update_baseline_activity(ba: BaselineActivity, **fields) -> BaselineActivity:
    assert_baseline_mutable(ba.baseline)
    for key, value in fields.items():
        if hasattr(ba, key):
            setattr(ba, key, value)
    ba.save()
    return ba


@transaction.atomic
def delete_baseline_activity(ba: BaselineActivity) -> None:
    assert_baseline_mutable(ba.baseline)
    ba.delete()

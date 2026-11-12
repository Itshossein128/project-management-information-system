"""Shared safety gate for MSP and P6 schedule import."""

from __future__ import annotations

import hashlib

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from cost_control.models import ActualCost, Budget
from documents.models import ProjectDocument
from permissions.project import active_member_has_codename, has_organizational_observation
from projects.models import Activity, ActivityRelation, Project, ProjectStatus, WBS
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule, MspImportStatus

IMPORT_ACTOR_MISSING = 'import_actor_missing'
IMPORT_NOT_PERMITTED = 'import_not_permitted'
PROJECT_ARCHIVED = 'project_archived'
WBS_HAS_PROGRESS = 'wbs_has_progress'
WBS_HAS_COST = 'wbs_has_cost'
WBS_HAS_DOCUMENTS = 'wbs_has_documents'
WBS_HAS_ACTIVITIES = 'wbs_has_activities'
BASELINE_HISTORY_PROTECTED = 'baseline_history_protected'

_BLOCK_ORDER = (
    WBS_HAS_PROGRESS,
    WBS_HAS_COST,
    WBS_HAS_DOCUMENTS,
    WBS_HAS_ACTIVITIES,
    BASELINE_HISTORY_PROTECTED,
)


class ImportSafetyError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def message_for(code: str) -> str:
    messages = {
        WBS_HAS_PROGRESS: _('Cannot replace a schedule that has progress recorded.'),
        WBS_HAS_COST: _('Cannot replace a schedule that has cost records.'),
        WBS_HAS_DOCUMENTS: _('Cannot replace a schedule that has linked documents.'),
        WBS_HAS_ACTIVITIES: _('Cannot replace a schedule that has activities.'),
        BASELINE_HISTORY_PROTECTED: _(
            'Cannot replace a schedule that has a locked or approved baseline.'
        ),
        PROJECT_ARCHIVED: _('Archived projects are read-only.'),
        IMPORT_NOT_PERMITTED: _('You no longer have permission to import into this project.'),
        IMPORT_ACTOR_MISSING: _('The import has no confirming user.'),
    }
    return str(messages.get(code, code))


def _actor_exists(user) -> bool:
    if user is None or not getattr(user, 'pk', None):
        return False
    model = user.__class__
    return model.objects.filter(pk=user.pk).exists()


def assert_can_import(project: Project, user) -> None:
    if not _actor_exists(user):
        raise ImportSafetyError(IMPORT_ACTOR_MISSING, message_for(IMPORT_ACTOR_MISSING))
    allowed = active_member_has_codename(user, project.id, 'edit_wbs')
    if project.status == ProjectStatus.ARCHIVED:
        if not (has_organizational_observation(user) and allowed):
            raise ImportSafetyError(PROJECT_ARCHIVED, message_for(PROJECT_ARCHIVED))
        return
    if not allowed:
        raise ImportSafetyError(IMPORT_NOT_PERMITTED, message_for(IMPORT_NOT_PERMITTED))


def replacement_projection(project: Project) -> dict:
    """Read-only counts for a replacement. This does not write."""
    code = replacement_block_code(project)
    if code:
        return {
            'blocked': code,
            'wbs_nodes_removed': 0,
            'activities_removed': 0,
            'relations_removed': 0,
        }
    return {
        'blocked': None,
        'wbs_nodes_removed': WBS.objects.filter(project=project, is_deleted=False).count(),
        'activities_removed': Activity.objects.filter(project=project, is_deleted=False).count(),
        'relations_removed': ActivityRelation.objects.filter(
            predecessor__project=project, is_deleted=False,
        ).count(),
    }


def replacement_block_code(project: Project) -> str | None:
    """Return the first protection code, or None when replacement may proceed."""
    live_activities = Activity.objects.filter(project=project, is_deleted=False)
    if ActivityProgress.objects.filter(activity__in=live_activities).exists():
        return WBS_HAS_PROGRESS
    if (
        Budget.objects.filter(project=project, is_deleted=False).exists()
        or ActualCost.objects.filter(project=project, is_deleted=False).exists()
    ):
        return WBS_HAS_COST
    wbs_ids = WBS.objects.filter(project=project, is_deleted=False).values_list('id', flat=True)
    if ProjectDocument.objects.filter(related_wbs_id__in=wbs_ids, is_deleted=False).exists():
        return WBS_HAS_DOCUMENTS
    if live_activities.exists():
        return WBS_HAS_ACTIVITIES
    if BaselineSchedule.objects.filter(project=project, is_deleted=False).filter(
        Q(is_locked=True) | Q(approved_at__isnull=False)
    ).exists():
        return BASELINE_HISTORY_PROTECTED
    return None


def guard_and_maybe_replace(project: Project, user, replace: bool) -> dict:
    assert_can_import(project, user)
    removed = {
        'wbs_nodes_removed': 0,
        'activities_removed': 0,
        'relations_removed': 0,
    }
    if not replace:
        return removed
    code = replacement_block_code(project)
    if code:
        raise ImportSafetyError(code, message_for(code))
    return _soft_clear(project, user)


def _soft_clear(project: Project, user) -> dict:
    relations = list(
        ActivityRelation.objects.filter(predecessor__project=project, is_deleted=False)
    )
    for relation in relations:
        relation.soft_delete(user=user)
    activities = list(Activity.objects.filter(project=project, is_deleted=False))
    for activity in activities:
        activity.soft_delete(user=user)
    nodes = list(WBS.objects.filter(project=project, is_deleted=False).order_by('-depth'))
    for node in nodes:
        node.soft_delete(user=user)
        # Keep the row, but move it out of the live materialised path so a new
        # root can be stored without colliding with this tombstone.
        WBS.objects.filter(pk=node.pk).update(path=node.pk.hex, depth=0, numchild=0)
    return {
        'wbs_nodes_removed': len(nodes),
        'activities_removed': len(activities),
        'relations_removed': len(relations),
    }


def file_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def find_inflight_job(job_model, project, user, replace: bool, file_bytes: bytes):
    """Return a pending or running job with the same bytes. The hash is not stored."""
    digest = file_sha256(file_bytes)
    candidates = job_model.objects.filter(
        project=project,
        created_by=user,
        replace_existing=replace,
        status__in=(MspImportStatus.PENDING, MspImportStatus.RUNNING),
    )
    for job in candidates:
        if file_sha256(bytes(job.file_data or b'')) == digest:
            return job
    return None


def open_working_copy(project: Project, user, filename: str, label: str, created_any: bool):
    """Create an unlocked working copy only when this attempt added schedule content."""
    if not created_any:
        return None
    approved_current = BaselineSchedule.objects.filter(
        project=project,
        is_current=True,
        is_deleted=False,
    ).filter(Q(is_locked=True) | Q(approved_at__isnull=False)).exists()
    version_name = f'{label} — {filename} — {timezone.now().strftime("%Y-%m-%d %H:%M")}'
    return BaselineSchedule.objects.create(
        project=project,
        version_name=version_name[:60],
        is_current=not approved_current,
        is_locked=False,
        approved_at=None,
        created_by=user,
        updated_by=user,
    )


def result_flags(removed: dict, created: dict, baseline, duplicates: list[str]) -> dict:
    created_any = any(created.get(key, 0) for key in ('wbs_nodes_created', 'activities_created', 'relations_created'))
    removed_any = any(removed.get(key, 0) for key in ('wbs_nodes_removed', 'activities_removed', 'relations_removed'))
    return {
        **removed,
        'duplicates': duplicates,
        'schedule_version_changed': bool(baseline and baseline.is_current),
        'baseline_id': str(baseline.id) if baseline else None,
        'nothing_changed': not created_any and not removed_any,
    }


def duplicate_messages(warnings: list[str]) -> list[str]:
    return [warning for warning in warnings if 'Duplicate' in warning or 'skipped' in warning.lower()]


def baseline_rows_for(baseline, tasks, uid_to_activity) -> list[BaselineActivity]:
    rows = []
    for task in tasks:
        if getattr(task, 'is_summary', False) or task.uid not in uid_to_activity:
            continue
        activity = uid_to_activity[task.uid]
        rows.append(BaselineActivity(
            baseline=baseline,
            activity=activity,
            planned_start=task.start,
            planned_finish=task.finish,
            planned_duration=getattr(task, 'duration_days', None),
            planned_progress=None if getattr(task, 'percent_invalid', False) else getattr(task, 'percent_complete', None),
            total_float=getattr(task, 'total_slack_days', getattr(task, 'total_slack', None)),
            free_float=getattr(task, 'free_slack_days', getattr(task, 'free_slack', None)),
            is_critical=bool(task.is_critical) if getattr(task, 'critical_known', False) else bool(getattr(task, 'is_critical', False)),
        ))
    return rows

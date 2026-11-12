"""Shared parent, unit, and warning resolution for MSP and P6 import."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

from django.utils.translation import gettext as _

from projects.models import RelationType

HOURS_PER_DAY = 8
TENTHS_PER_DAY = 8 * 60 * 10

FINISH_BEFORE_START = 'finish_before_start'
STRUCTURE_CYCLE = 'structure_cycle'
DUPLICATE_IN_FILE = 'duplicate_in_file'
ACTIVITY_WITHOUT_PARENT = 'activity_without_parent'
PREDECESSOR_MISSING = 'predecessor_missing'
PREDECESSOR_IS_SUMMARY = 'predecessor_is_summary'
RELATION_TYPE_INVALID = 'relation_type_invalid'
LAG_NOT_WHOLE_DAYS = 'lag_not_whole_days'
DEPTH_EXCEEDED = 'depth_exceeded'
DURATION_NOT_WHOLE_DAYS = 'duration_not_whole_days'
SLACK_NOT_WHOLE_DAYS = 'slack_not_whole_days'
INVALID_PERCENT = 'invalid_percent'
MILESTONE_DURATION_CONFLICT = 'milestone_duration_conflict'
CALENDAR_NOT_APPLIED = 'calendar_not_applied'
EMPTY_IMPORT = 'empty_import'
DUPLICATE_EXISTING = 'duplicate_existing'
INVALID_WEIGHT = 'invalid_weight'
OMITTED_LINK_CODES = {
    PREDECESSOR_MISSING,
    PREDECESSOR_IS_SUMMARY,
    RELATION_TYPE_INVALID,
    LAG_NOT_WHOLE_DAYS,
}

MSP_RELATION_TYPES = {
    '1': RelationType.FS,
    '2': RelationType.SS,
    '3': RelationType.FF,
    '4': RelationType.SF,
}

P6_RELATION_TYPES = {
    'PR_FS': RelationType.FS,
    'PR_SS': RelationType.SS,
    'PR_FF': RelationType.FF,
    'PR_SF': RelationType.SF,
    '0': RelationType.FS,
    '1': RelationType.SS,
    '2': RelationType.FF,
    '3': RelationType.SF,
}


class ImportFidelityError(Exception):
    def __init__(self, notes):
        if isinstance(notes, PlanNote):
            notes = [notes]
        self.notes = list(notes)
        self.code = self.notes[0].code if self.notes else ''
        self.message = message_for(self.code) if self.code else ''
        super().__init__(self.message)

    def as_dicts(self) -> list[dict]:
        return [{'code': note.code, 'row': note.row} for note in self.notes]


def message_for(code: str) -> str:
    messages = {
        FINISH_BEFORE_START: _('A finish date is before its start.'),
        STRUCTURE_CYCLE: _('The file contains a cycle.'),
        DUPLICATE_IN_FILE: _('The file contains a duplicate identifier or code.'),
        ACTIVITY_WITHOUT_PARENT: _('A row has no resolvable parent.'),
        PREDECESSOR_MISSING: _('A predecessor is not in the file.'),
        PREDECESSOR_IS_SUMMARY: _('A predecessor is a summary work package.'),
        RELATION_TYPE_INVALID: _('A relationship type is not supported.'),
        LAG_NOT_WHOLE_DAYS: _('A delay is not an exact number of eight-hour days.'),
        DEPTH_EXCEEDED: _('A row is deeper than the project allows.'),
        DURATION_NOT_WHOLE_DAYS: _('A duration is not an exact number of eight-hour days.'),
        SLACK_NOT_WHOLE_DAYS: _('Slack is not an exact number of eight-hour days.'),
        INVALID_PERCENT: _('A percent is outside 0 through 100.'),
        MILESTONE_DURATION_CONFLICT: _('A milestone mark does not have zero duration.'),
        CALENDAR_NOT_APPLIED: _('The file calendar was not applied.'),
        EMPTY_IMPORT: _('The file did not contain a schedule to store.'),
        DUPLICATE_EXISTING: _('A code already exists in the project and was left unchanged.'),
        INVALID_WEIGHT: _('A parent-share weight is outside 0 through 1.'),
    }
    return str(messages.get(code, code))


def days_from_msp_duration(value: str) -> tuple[int | None, bool]:
    """Return (days, inexact). Empty input is (None, False). Zero is 0 days."""
    import re

    if not value:
        return None, False
    match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', value)
    if not match or match.group(0) == 'P':
        return None, True
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)
    if minutes or seconds or hours % HOURS_PER_DAY:
        return None, True
    return days + hours // HOURS_PER_DAY, False


def days_from_hours(value: str) -> tuple[int | None, bool]:
    if value is None or value == '':
        return None, False
    try:
        hours = Decimal(str(value))
    except Exception:
        return None, True
    if hours % HOURS_PER_DAY:
        return None, True
    return int(hours // HOURS_PER_DAY), False


def days_from_tenths(raw: int) -> tuple[int | None, bool]:
    if raw % TENTHS_PER_DAY:
        return None, True
    return raw // TENTHS_PER_DAY, False


def relation_type_for(raw: str, *, prima: bool) -> str | None:
    table = P6_RELATION_TYPES if prima else MSP_RELATION_TYPES
    return table.get(str(raw).strip())


@dataclass
class PlanNote:
    code: str
    row: str

    def as_text(self) -> str:
        if self.row:
            return f'{self.code}: {self.row}'
        return self.code


@dataclass
class ResolvedPlan:
    packages: list = field(default_factory=list)
    activities: list = field(default_factory=list)
    links: list = field(default_factory=list)
    blocking: list[PlanNote] = field(default_factory=list)
    warnings: list[PlanNote] = field(default_factory=list)
    existing_wbs_codes: set[str] = field(default_factory=set)
    existing_activity_codes: set[str] = field(default_factory=set)

    def warning_texts(self) -> list[str]:
        return [note.as_text() for note in [*self.blocking, *self.warnings]]

    def _new(self, rows, existing: set[str]) -> list:
        return [row for row in rows if _task_code(row) not in existing]

    def counts(self) -> dict:
        omitted = [note for note in self.warnings if note.code != DUPLICATE_EXISTING]
        return {
            'created_packages': len(self._new(self.packages, self.existing_wbs_codes)),
            'created_activities': len(self._new(self.activities, self.existing_activity_codes)),
            'created_links': len(self.links),
            'omitted_count': len(omitted),
            'warned_count': len(self.warnings),
        }


def _task_code(task) -> str:
    return task.wbs_code or task.uid


def _row_id(task) -> str:
    return task.uid or task.name or ''


def _by_key(tasks) -> dict:
    found = {}
    for task in tasks:
        if task.node_key:
            found.setdefault(task.node_key, task)
    return found


def _parent_cycle(tasks) -> bool:
    found = _by_key(tasks)
    for task in tasks:
        seen: set[str] = set()
        key = task.parent_key
        while key:
            if key == task.node_key or key in seen:
                return True
            seen.add(key)
            parent = found.get(key)
            if parent is None:
                break
            key = parent.parent_key
    return False


def _depth(task, found) -> int:
    depth = 1
    seen: set[str] = set()
    key = task.parent_key
    while key and key not in seen:
        seen.add(key)
        depth += 1
        parent = found.get(key)
        if parent is None:
            break
        key = parent.parent_key
    return depth


def _link_cycle(leaves) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    leaf_ids = {task.uid for task in leaves}
    for task in leaves:
        for pred in task.predecessors:
            if pred.get('uid') == task.uid:
                return True
            if pred.get('uid') not in leaf_ids:
                continue
            if not pred.get('relation_type') or not pred.get('lag_exact'):
                continue
            graph[pred['uid']].append(task.uid)
    color: dict[str, int] = {}

    def visit(node: str) -> bool:
        color[node] = 1
        for nxt in graph.get(node, []):
            state = color.get(nxt, 0)
            if state == 1 or (state == 0 and visit(nxt)):
                return True
        color[node] = 2
        return False

    for node in list(graph):
        if color.get(node, 0) == 0 and visit(node):
            return True
    return False


def _duplicate_rows(tasks) -> list[PlanNote]:
    notes = []
    seen_uid: dict[str, object] = {}
    seen_key: dict[str, object] = {}
    seen_code: dict[str, object] = {}
    for task in tasks:
        row = _row_id(task)
        if task.uid in seen_uid:
            notes.append(PlanNote(DUPLICATE_IN_FILE, row))
        else:
            seen_uid[task.uid] = task
        if task.node_key:
            if task.node_key in seen_key:
                notes.append(PlanNote(DUPLICATE_IN_FILE, row))
            else:
                seen_key[task.node_key] = task
        code = _task_code(task)
        if code in seen_code:
            notes.append(PlanNote(DUPLICATE_IN_FILE, row))
        else:
            seen_code[code] = task
    return notes


def resolve(parsed, max_depth: int | None = None) -> ResolvedPlan:
    tasks = list(parsed.tasks)
    plan = ResolvedPlan()
    if getattr(parsed, 'has_calendar', False):
        plan.warnings.append(PlanNote(CALENDAR_NOT_APPLIED, ''))

    for task in tasks:
        row = _row_id(task)
        if task.duration_inexact:
            task.duration_days = None
            plan.warnings.append(PlanNote(DURATION_NOT_WHOLE_DAYS, row))
        if task.slack_inexact or task.free_slack_inexact:
            if task.slack_inexact:
                task.total_slack_days = None
            if task.free_slack_inexact:
                task.free_slack_days = None
            plan.warnings.append(PlanNote(SLACK_NOT_WHOLE_DAYS, row))
        if task.percent_invalid:
            task.percent_complete = None
            plan.warnings.append(PlanNote(INVALID_PERCENT, row))
        if getattr(task, 'weight_invalid', False):
            plan.warnings.append(PlanNote(INVALID_WEIGHT, row))
        if task.milestone_flag and task.duration_days == 0:
            task.is_milestone = True
        elif task.milestone_flag:
            task.is_milestone = False
            plan.warnings.append(PlanNote(MILESTONE_DURATION_CONFLICT, row))
        else:
            task.is_milestone = False
        if task.start and task.finish and task.finish < task.start:
            plan.blocking.append(PlanNote(FINISH_BEFORE_START, row))

    plan.blocking.extend(_duplicate_rows(tasks))
    if _parent_cycle(tasks):
        plan.blocking.append(PlanNote(STRUCTURE_CYCLE, ''))
    leaves = [task for task in tasks if not task.is_summary]
    if any(pred.get('uid') == task.uid for task in leaves for pred in task.predecessors):
        plan.blocking.append(PlanNote(STRUCTURE_CYCLE, ''))
    elif _link_cycle(leaves):
        plan.blocking.append(PlanNote(STRUCTURE_CYCLE, ''))

    if plan.blocking:
        return plan

    found = _by_key(tasks)
    omitted: set[str] = set()
    if max_depth is not None:
        for task in tasks:
            if task.node_key and _depth(task, found) > max_depth:
                omitted.add(task.node_key)
        changed = True
        while changed:
            changed = False
            for task in tasks:
                if task.node_key and task.node_key not in omitted and task.parent_key in omitted:
                    omitted.add(task.node_key)
                    changed = True
        for task in tasks:
            if task.node_key in omitted:
                plan.warnings.append(PlanNote(DEPTH_EXCEEDED, _row_id(task)))

    packages = []
    package_keys = set()
    for task in tasks:
        if not task.is_summary or task.node_key in omitted:
            continue
        if task.parent_key and task.parent_key not in found:
            plan.warnings.append(PlanNote(ACTIVITY_WITHOUT_PARENT, _row_id(task)))
            continue
        if task.parent_key and not found[task.parent_key].is_summary:
            plan.warnings.append(PlanNote(ACTIVITY_WITHOUT_PARENT, _row_id(task)))
            continue
        packages.append(task)
        package_keys.add(task.node_key)

    kept_packages = []
    for task in packages:
        if task.parent_key and task.parent_key not in package_keys:
            plan.warnings.append(PlanNote(DEPTH_EXCEEDED, _row_id(task)))
            continue
        kept_packages.append(task)
        plan.packages.append(task)
    package_keys = {task.node_key for task in plan.packages}

    stored_leaves = []
    for task in leaves:
        if task.node_key in omitted:
            continue
        if not task.parent_key or task.parent_key not in package_keys:
            plan.warnings.append(PlanNote(ACTIVITY_WITHOUT_PARENT, _row_id(task)))
            continue
        stored_leaves.append(task)
        plan.activities.append(task)

    stored_ids = {task.uid for task in stored_leaves}
    summary_ids = {task.uid for task in tasks if task.is_summary}
    known_ids = {task.uid for task in tasks}
    for task in leaves:
        if task.node_key in omitted:
            continue
        for pred in task.predecessors:
            uid = pred.get('uid') or ''
            row = f'{_row_id(task)} / {uid}'
            if not pred.get('relation_type'):
                plan.warnings.append(PlanNote(RELATION_TYPE_INVALID, row))
                continue
            if not pred.get('lag_exact'):
                plan.warnings.append(PlanNote(LAG_NOT_WHOLE_DAYS, row))
                continue
            if uid in summary_ids:
                plan.warnings.append(PlanNote(PREDECESSOR_IS_SUMMARY, row))
                continue
            if uid not in known_ids or uid not in stored_ids:
                plan.warnings.append(PlanNote(PREDECESSOR_MISSING, row))
                continue
            if task.uid not in stored_ids:
                continue
            plan.links.append({
                'predecessor_uid': uid,
                'successor_uid': task.uid,
                'relation_type': pred['relation_type'],
                'lag_days': pred.get('lag_days') or 0,
            })

    if not plan.packages and not plan.activities:
        plan.warnings.append(PlanNote(EMPTY_IMPORT, ''))
    return plan


def preview_payload(plan: ResolvedPlan) -> dict:
    nodes = {
        task.node_key: {
            'wbs_code': _task_code(task),
            'wbs_name': task.name,
            'depth': 1,
            'is_summary': True,
            'activities': [],
            'children': [],
            '_outline': task.outline_number or task.node_key,
        }
        for task in plan.packages
    }
    roots = []
    for task in plan.packages:
        node = nodes[task.node_key]
        parent = nodes.get(task.parent_key or '')
        if parent is None:
            roots.append(node)
        else:
            parent['children'].append(node)

    def assign_depth(node, depth):
        node['depth'] = depth
        for child in node['children']:
            assign_depth(child, depth + 1)

    for root in roots:
        assign_depth(root, 1)

    flat = []
    for task in plan.activities:
        item = {
            'activity_code': _task_code(task),
            'activity_name': task.name,
            'outline_number': task.outline_number,
            'duration_days': task.duration_days,
        }
        parent = nodes.get(task.parent_key or '')
        if parent is not None:
            parent['activities'].append({
                'activity_code': item['activity_code'],
                'activity_name': item['activity_name'],
                'duration_days': item['duration_days'],
            })
        flat.append(item)

    def sort_node(node):
        node['activities'].sort(key=lambda item: item.get('activity_code') or '')
        node['children'].sort(key=lambda item: item.get('_outline') or '')
        for child in node['children']:
            sort_node(child)

    for root in roots:
        sort_node(root)
    roots.sort(key=lambda item: item.get('_outline') or '')

    def strip(node):
        node.pop('_outline', None)
        for child in node['children']:
            strip(child)

    for root in roots:
        strip(root)

    return {
        'wbs_tree': roots,
        'activities': flat,
        'warnings': plan.warning_texts(),
        'warning_items': [{'code': note.code, 'row': note.row} for note in plan.warnings],
        'blocking': [{'code': note.code, 'row': note.row} for note in plan.blocking],
        'counts': plan.counts(),
    }


def note_existing(plan: ResolvedPlan, wbs_codes, activity_codes) -> ResolvedPlan:
    plan.existing_wbs_codes = set(wbs_codes or [])
    plan.existing_activity_codes = set(activity_codes or [])
    for task in plan.packages:
        if _task_code(task) in plan.existing_wbs_codes:
            plan.warnings.append(PlanNote(DUPLICATE_EXISTING, _row_id(task)))
    for task in plan.activities:
        if _task_code(task) in plan.existing_activity_codes:
            plan.warnings.append(PlanNote(DUPLICATE_EXISTING, _row_id(task)))
    return plan


def refresh_cached_wbs(cache: dict) -> None:
    from projects.models import WBS

    if not cache:
        return
    fresh = {
        row.pk: row
        for row in WBS.objects.filter(pk__in=[node.pk for node in cache.values()])
    }
    for key, node in list(cache.items()):
        updated = fresh.get(node.pk)
        if updated is not None:
            cache[key] = updated


def unchanged_result(plan: ResolvedPlan) -> dict:
    return {
        'wbs_nodes_created': 0,
        'activities_created': 0,
        'relations_created': 0,
        'wbs_nodes_removed': 0,
        'activities_removed': 0,
        'relations_removed': 0,
        'warnings': plan.warning_texts(),
        'warning_items': [{'code': note.code, 'row': note.row} for note in plan.warnings],
        'blocking': [{'code': note.code, 'row': note.row} for note in plan.blocking],
        'duplicates': [],
        'schedule_version_changed': False,
        'baseline_id': None,
        'nothing_changed': True,
        **plan.counts(),
    }

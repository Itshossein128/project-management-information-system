"""Microsoft Project XML import parser and executor."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from projects.models import Activity, ActivityRelation, Project, RelationType, WBS
from schedule.models import BaselineActivity, BaselineSchedule

MSP_RELATION_MAP = {
    '1': RelationType.FS,
    '2': RelationType.SS,
    '3': RelationType.FF,
    '4': RelationType.SF,
    0: RelationType.FS,
    1: RelationType.FS,
    2: RelationType.SS,
    3: RelationType.FF,
    4: RelationType.SF,
}


def _local(tag: str) -> str:
    return tag.split('}')[-1] if '}' in tag else tag


def _text(el, name: str, default: str = '') -> str:
    if el is None:
        return default
    for child in el:
        if _local(child.tag) == name:
            return (child.text or '').strip()
    return default


def _parse_msp_date(value: str) -> date | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(value[:19], fmt).date()
        except ValueError:
            continue
    return None


def _parse_duration_days(value: str) -> int | None:
    if not value:
        return None
    # PT480H0M0S or P10D
    m = re.match(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?)?', value)
    if m:
        days = int(m.group(1) or 0)
        hours = int(m.group(2) or 0)
        if days:
            return days
        if hours:
            return max(1, round(hours / 8))
    return None


@dataclass
class ParsedTask:
    uid: str
    outline_level: int
    outline_number: str
    wbs_code: str
    name: str
    is_summary: bool
    start: date | None = None
    finish: date | None = None
    duration_days: int | None = None
    percent_complete: Decimal | None = None
    total_slack: int | None = None
    free_slack: int | None = None
    is_critical: bool = False
    predecessors: list[dict] = field(default_factory=list)


@dataclass
class ParseResult:
    tasks: list[ParsedTask]
    warnings: list[str] = field(default_factory=list)


def parse_msp_xml(file_bytes: bytes) -> ParseResult:
    warnings: list[str] = []
    try:
        root = ET.fromstring(file_bytes)
    except ET.ParseError as exc:
        raise ValueError(f'Invalid XML: {exc}') from exc

    if _local(root.tag) != 'Project':
        raise ValueError('File must be a Microsoft Project XML export with <Project> root.')

    tasks_el = None
    for child in root:
        if _local(child.tag) == 'Tasks':
            tasks_el = child
            break
    if tasks_el is None:
        raise ValueError('No <Tasks> section found in MSP XML.')

    tasks: list[ParsedTask] = []
    for task_el in tasks_el:
        if _local(task_el.tag) != 'Task':
            continue
        uid = _text(task_el, 'UID')
        if not uid or uid == '0':
            continue
        outline_level = int(_text(task_el, 'OutlineLevel', '1') or '1')
        outline_number = _text(task_el, 'OutlineNumber') or _text(task_el, 'WBS')
        wbs_code = _text(task_el, 'WBS') or outline_number
        name = _text(task_el, 'Name')
        if not name:
            warnings.append(f'Task UID {uid} has no name — skipped.')
            continue
        summary = _text(task_el, 'Summary', '0') in ('1', 'true', 'True')
        duration_raw = _text(task_el, 'Duration')
        duration_days = _parse_duration_days(duration_raw)
        if duration_raw and duration_days is None:
            warnings.append(f'Could not parse duration "{duration_raw}" for task {name}.')

        preds = []
        for rel in task_el:
            if _local(rel.tag) == 'PredecessorLink':
                preds.append({
                    'uid': _text(rel, 'PredecessorUID'),
                    'type': _text(rel, 'Type', '1'),
                    'lag': int(_text(rel, 'LinkLag', '0') or '0'),
                })

        pct = _text(task_el, 'PercentComplete')
        tasks.append(
            ParsedTask(
                uid=uid,
                outline_level=outline_level,
                outline_number=outline_number,
                wbs_code=wbs_code,
                name=name,
                is_summary=summary,
                start=_parse_msp_date(_text(task_el, 'Start')),
                finish=_parse_msp_date(_text(task_el, 'Finish')),
                duration_days=duration_days,
                percent_complete=Decimal(pct) if pct else None,
                total_slack=int(_text(task_el, 'TotalSlack', '0') or '0') or None,
                free_slack=int(_text(task_el, 'FreeSlack', '0') or '0') or None,
                is_critical=_text(task_el, 'Critical', '0') in ('1', 'true'),
                predecessors=preds,
            )
        )

    return ParseResult(tasks=tasks, warnings=warnings)


def build_preview(parsed: ParseResult) -> dict:
    """Non-destructive preview tree."""
    wbs_tree: list[dict] = []
    stack: dict[int, dict] = {}

    for task in sorted(parsed.tasks, key=lambda t: t.outline_number):
        node = {
            'wbs_code': task.wbs_code or task.outline_number,
            'wbs_name': task.name,
            'depth': task.outline_level,
            'is_summary': task.is_summary,
            'activities': [] if task.is_summary else [{
                'activity_code': task.wbs_code or task.uid,
                'activity_name': task.name,
                'duration_days': task.duration_days,
            }],
            'children': [],
        }
        level = max(task.outline_level - 1, 0)
        if level == 0:
            wbs_tree.append(node)
        elif level - 1 in stack:
            stack[level - 1]['children'].append(node)
        stack[level] = node

    activities = [
        {
            'activity_code': t.wbs_code or t.uid,
            'activity_name': t.name,
            'outline_number': t.outline_number,
            'duration_days': t.duration_days,
        }
        for t in parsed.tasks
        if not t.is_summary
    ]
    return {'wbs_tree': wbs_tree, 'activities': activities, 'warnings': parsed.warnings}


@transaction.atomic
def execute_msp_import(
    project: Project,
    file_bytes: bytes,
    *,
    filename: str,
    replace: bool = False,
    progress_callback=None,
    user=None,
) -> dict:
    parsed = parse_msp_xml(file_bytes)
    warnings = list(parsed.warnings)

    if replace:
        ActivityRelation._base_manager.filter(
            predecessor__project=project,
        ).delete()
        Activity._base_manager.filter(project=project).delete()
        WBS.objects.filter(project=project).delete()

    audit_user = user
    if audit_user is None:
        from django.contrib.auth import get_user_model
        audit_user = get_user_model().objects.order_by('created_at').first()

    uid_to_activity: dict[str, Activity] = {}
    outline_to_wbs: dict[str, WBS] = {}
    wbs_count = 0
    activity_count = 0
    relation_count = 0

    summary_tasks = [t for t in parsed.tasks if t.is_summary]
    if not summary_tasks:
        summary_tasks = parsed.tasks

    level_parents: dict[int, WBS] = {}

    total = len(summary_tasks) + len([t for t in parsed.tasks if not t.is_summary])
    done = 0

    for task in sorted(summary_tasks, key=lambda t: t.outline_number):
        code = task.wbs_code or task.outline_number
        if not code:
            warnings.append(f'Summary task "{task.name}" has no WBS code.')
            continue
        if WBS.objects.filter(project=project, wbs_code=code).exists():
            warnings.append(f'Duplicate WBS code "{code}" — skipped.')
            outline_to_wbs[task.outline_number] = WBS.objects.get(project=project, wbs_code=code)
            continue

        level = task.outline_level
        parent = level_parents.get(level - 1) if level > 1 else None

        if project.max_depth is not None and level > project.max_depth:
            warnings.append(f'WBS "{code}" exceeds project max_depth — skipped.')
            continue

        if parent:
            wbs = parent.add_child(
                project_id=project.id,
                wbs_code=code,
                wbs_name=task.name,
            )
        else:
            wbs = WBS.add_root(project_id=project.id, wbs_code=code, wbs_name=task.name)

        outline_to_wbs[task.outline_number] = wbs
        level_parents[level] = wbs
        wbs_count += 1
        done += 1
        if progress_callback:
            progress_callback(int(done / max(total, 1) * 80))

    for task in parsed.tasks:
        if task.is_summary:
            continue
        parent_key = '.'.join(task.outline_number.split('.')[:-1])
        wbs = outline_to_wbs.get(parent_key)
        if wbs is None and outline_to_wbs:
            wbs = list(outline_to_wbs.values())[0]
        if wbs is None:
            warnings.append(f'Activity "{task.name}" has no WBS parent.')
            continue

        code = task.wbs_code or task.uid
        if Activity.objects.filter(project=project, activity_code=code).exists():
            warnings.append(f'Duplicate activity code "{code}" — skipped.')
            continue

        act = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code=code,
            activity_name=task.name,
            planned_start=task.start,
            planned_finish=task.finish,
            created_by=audit_user,
            updated_by=audit_user,
        )
        uid_to_activity[task.uid] = act
        activity_count += 1
        done += 1

    baseline = BaselineSchedule.objects.create(
        project=project,
        version_name=f'MSP Import — {filename} — {timezone.now().strftime("%Y-%m-%d %H:%M")}',
        is_current=True,
    )

    for task in parsed.tasks:
        if task.is_summary or task.uid not in uid_to_activity:
            continue
        act = uid_to_activity[task.uid]
        BaselineActivity.objects.create(
            baseline=baseline,
            activity=act,
            planned_start=task.start,
            planned_finish=task.finish,
            planned_duration=task.duration_days,
            planned_progress=task.percent_complete,
            total_float=task.total_slack,
            free_float=task.free_slack,
            is_critical=task.is_critical,
        )

    for task in parsed.tasks:
        if task.uid not in uid_to_activity:
            continue
        successor = uid_to_activity[task.uid]
        for pred in task.predecessors:
            predecessor = uid_to_activity.get(pred['uid'])
            if predecessor is None:
                warnings.append(f'Predecessor UID {pred["uid"]} not found for {task.name}.')
                continue
            rel_type = MSP_RELATION_MAP.get(pred['type'], RelationType.FS)
            ActivityRelation.objects.get_or_create(
                predecessor=predecessor,
                successor=successor,
                defaults={
                    'relation_type': rel_type,
                    'lag_days': pred.get('lag', 0),
                    'created_by': audit_user,
                    'updated_by': audit_user,
                },
            )
            relation_count += 1

    if progress_callback:
        progress_callback(100)

    return {
        'wbs_nodes_created': wbs_count,
        'activities_created': activity_count,
        'relations_created': relation_count,
        'warnings': warnings,
    }

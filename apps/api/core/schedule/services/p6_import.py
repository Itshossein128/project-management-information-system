"""Primavera P6 XER import parser and executor."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from projects.models import Activity, ActivityRelation, Project, RelationType, WBS
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.services.msp_import import ParseResult, ParsedTask, build_preview

P6_RELATION_MAP = {
    'PR_FS': RelationType.FS,
    'PR_SS': RelationType.SS,
    'PR_FF': RelationType.FF,
    'PR_SF': RelationType.SF,
    '0': RelationType.FS,
    '1': RelationType.SS,
    '2': RelationType.FF,
    '3': RelationType.SF,
}


def _parse_xer_tables(file_bytes: bytes) -> dict[str, list[dict[str, str]]]:
    try:
        text = file_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = file_bytes.decode('latin-1')

    tables: dict[str, list[dict[str, str]]] = {}
    current_table: str | None = None
    fields: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip('\r\n')
        if not line or line.startswith('ERMHDR'):
            continue
        parts = line.split('\t')
        marker = parts[0]
        if marker == '%T':
            current_table = parts[1] if len(parts) > 1 else None
            fields = []
            if current_table and current_table not in tables:
                tables[current_table] = []
        elif marker == '%F' and current_table:
            fields = parts[1:]
        elif marker == '%R' and current_table and fields:
            values = parts[1:]
            row = {fields[i]: values[i] if i < len(values) else '' for i in range(len(fields))}
            tables[current_table].append(row)
    return tables


def _parse_p6_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(value[:16], fmt).date()
        except ValueError:
            continue
    return None


def _hours_to_days(hours: str) -> int | None:
    if not hours:
        return None
    try:
        return max(1, round(float(hours) / 8))
    except ValueError:
        return None


def parse_p6_xer(file_bytes: bytes) -> ParseResult:
    tables = _parse_xer_tables(file_bytes)
    projwbs = tables.get('PROJWBS') or []
    tasks = tables.get('TASK') or []
    preds = tables.get('TASKPRED') or []

    if not projwbs and not tasks:
        raise ValueError('No PROJWBS or TASK tables found in XER file.')

    wbs_by_id = {row.get('wbs_id', ''): row for row in projwbs if row.get('wbs_id')}
    depth_cache: dict[str, int] = {}

    def depth_for_wbs(wbs_id: str, seen: set[str] | None = None) -> int:
        if wbs_id in depth_cache:
            return depth_cache[wbs_id]
        if seen is None:
            seen = set()
        if wbs_id in seen:
            return 1
        seen.add(wbs_id)
        row = wbs_by_id.get(wbs_id)
        if not row:
            return 1
        parent = row.get('parent_wbs_id', '')
        depth = 1 + (depth_for_wbs(parent, seen) if parent else 0)
        depth_cache[wbs_id] = depth
        return depth

    pred_map: dict[str, list[dict]] = {}
    for row in preds:
        task_id = row.get('task_id', '')
        pred_map.setdefault(task_id, []).append({
            'uid': row.get('pred_task_id', ''),
            'type': row.get('pred_type', 'PR_FS'),
            'lag': int(float(row.get('lag_hr_cnt') or 0) // 8),
        })

    parsed_tasks: list[ParsedTask] = []
    warnings: list[str] = []

    for row in sorted(projwbs, key=lambda r: (depth_for_wbs(r.get('wbs_id', '')), r.get('seq_num', ''))):
        wbs_id = row.get('wbs_id', '')
        code = row.get('wbs_short_name') or row.get('wbs_id') or ''
        name = row.get('wbs_name') or code
        if not code:
            continue
        depth = depth_for_wbs(wbs_id)
        parsed_tasks.append(
            ParsedTask(
                uid=f'wbs-{wbs_id}',
                outline_level=depth,
                outline_number=code,
                wbs_code=code,
                name=name,
                is_summary=True,
            )
        )

    for row in tasks:
        task_id = row.get('task_id', '')
        code = row.get('task_code') or task_id
        name = row.get('task_name') or code
        if not name:
            warnings.append(f'Task {task_id} has no name — skipped.')
            continue
        wbs_id = row.get('wbs_id', '')
        wbs_row = wbs_by_id.get(wbs_id, {})
        wbs_code = wbs_row.get('wbs_short_name') or wbs_id
        depth = depth_for_wbs(wbs_id) + 1 if wbs_id else 1
        parsed_tasks.append(
            ParsedTask(
                uid=task_id,
                outline_level=depth,
                outline_number=f'{wbs_code}.{code}' if wbs_code else code,
                wbs_code=code,
                name=name,
                is_summary=False,
                start=_parse_p6_date(row.get('target_start_date') or row.get('act_start_date', '')),
                finish=_parse_p6_date(row.get('target_end_date') or row.get('act_end_date', '')),
                duration_days=_hours_to_days(row.get('target_drtn_hr_cnt') or row.get('remain_drtn_hr_cnt', '')),
                percent_complete=Decimal(row['phys_complete_pct']) if row.get('phys_complete_pct') else None,
                predecessors=pred_map.get(task_id, []),
            )
        )

    return ParseResult(tasks=parsed_tasks, warnings=warnings)


@transaction.atomic
def execute_p6_import(
    project: Project,
    file_bytes: bytes,
    *,
    filename: str,
    replace: bool = False,
    progress_callback=None,
    user=None,
) -> dict:
    parsed = parse_p6_xer(file_bytes)
    warnings = list(parsed.warnings)

    if replace:
        ActivityRelation._base_manager.filter(predecessor__project=project).delete()
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
    level_parents: dict[int, WBS] = {}

    summary_tasks = [t for t in parsed.tasks if t.is_summary]
    leaf_tasks = [t for t in parsed.tasks if not t.is_summary]
    total = len(summary_tasks) + len(leaf_tasks)
    done = 0

    for task in sorted(summary_tasks, key=lambda t: (t.outline_level, t.wbs_code)):
        code = task.wbs_code
        if WBS.objects.filter(project=project, wbs_code=code).exists():
            outline_to_wbs[task.outline_number] = WBS.objects.get(project=project, wbs_code=code)
            warnings.append(f'Duplicate WBS code "{code}" — skipped.')
            continue
        level = task.outline_level
        parent = level_parents.get(level - 1) if level > 1 else None
        if parent:
            wbs = parent.add_child(project_id=project.id, wbs_code=code, wbs_name=task.name)
        else:
            wbs = WBS.add_root(project_id=project.id, wbs_code=code, wbs_name=task.name)
        outline_to_wbs[task.outline_number] = wbs
        level_parents[level] = wbs
        wbs_count += 1
        done += 1
        if progress_callback:
            progress_callback(int(done / max(total, 1) * 80))

    for task in leaf_tasks:
        parent_key = '.'.join(task.outline_number.split('.')[:-1])
        wbs = outline_to_wbs.get(parent_key)
        if wbs is None:
            for key in sorted(outline_to_wbs.keys(), key=len, reverse=True):
                if task.outline_number.startswith(key):
                    wbs = outline_to_wbs[key]
                    break
        if wbs is None and outline_to_wbs:
            wbs = list(outline_to_wbs.values())[-1]
        if wbs is None:
            warnings.append(f'Activity "{task.name}" has no WBS parent.')
            continue
        code = task.wbs_code
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
        version_name=f'P6 Import — {filename} — {timezone.now().strftime("%Y-%m-%d %H:%M")}',
        is_current=True,
    )

    for task in leaf_tasks:
        if task.uid not in uid_to_activity:
            continue
        act = uid_to_activity[task.uid]
        BaselineActivity.objects.create(
            baseline=baseline,
            activity=act,
            planned_start=task.start,
            planned_finish=task.finish,
            planned_duration=task.duration_days,
            planned_progress=task.percent_complete,
        )

    for task in leaf_tasks:
        if task.uid not in uid_to_activity:
            continue
        successor = uid_to_activity[task.uid]
        for pred in task.predecessors:
            predecessor = uid_to_activity.get(pred['uid'])
            if predecessor is None:
                warnings.append(f'Predecessor {pred["uid"]} not found for {task.name}.')
                continue
            rel_type = P6_RELATION_MAP.get(pred['type'], RelationType.FS)
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


__all__ = ['parse_p6_xer', 'build_preview', 'execute_p6_import']

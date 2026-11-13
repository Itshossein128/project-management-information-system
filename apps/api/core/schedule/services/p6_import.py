"""Primavera P6 XER import parser and executor."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from django.db import transaction

from projects.models import Activity, ActivityRelation, Project, WBS
from schedule.models import BaselineActivity
from schedule.services.import_safety import (
    baseline_rows_for,
    duplicate_messages,
    guard_and_maybe_replace,
    open_working_copy,
    result_flags,
)
from schedule.services.import_fidelity import (
    ImportFidelityError,
    days_from_hours,
    annotate_project,
    display_result,
    refresh_cached_wbs,
    relation_type_for,
    resolve,
    unchanged_result,
)
from schedule.services.msp_import import ParseResult, ParsedTask, build_preview
from schedule.services.shared_import import extract_activities_from_tasks, bulk_create_relations


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
    days, inexact = days_from_hours(hours)
    if inexact:
        return None
    return days


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
        raw_type = row.get('pred_type', '')
        lag_days, lag_inexact = days_from_hours(row.get('lag_hr_cnt') or '0')
        pred_map.setdefault(task_id, []).append({
            'uid': row.get('pred_task_id', ''),
            'type': raw_type,
            'relation_type': relation_type_for(raw_type, prima=True),
            'lag_days': lag_days,
            'lag_exact': not lag_inexact,
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
                node_key=f'wbs:{wbs_id}',
                parent_key=f'wbs:{row.get("parent_wbs_id")}' if row.get('parent_wbs_id') else None,
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
        wbs_code = wbs_row.get('wbs_short_name') or ''
        depth = depth_for_wbs(wbs_id) + 1 if wbs_id else 1
        duration_days, duration_inexact = days_from_hours(row.get('target_drtn_hr_cnt', ''))
        percent = Decimal(row['phys_complete_pct']) if row.get('phys_complete_pct') else None
        percent_invalid = percent is not None and (percent < 0 or percent > 100)
        task_type = row.get('task_type', '')

        def _hours_field(key: str):
            raw = row.get(key, '')
            if key not in row or str(raw).strip() == '':
                return None, False
            days, inexact = days_from_hours(str(raw))
            return (None if inexact else days), inexact

        total_days, total_inexact = _hours_field('total_float_hr_cnt')
        free_days, free_inexact = _hours_field('free_float_hr_cnt')
        crit_raw = row.get('crit_path_flag', '')
        critical_known = 'crit_path_flag' in row and str(crit_raw).strip() != ''
        is_critical = str(crit_raw).strip().lower() in {'y', 'yes', '1', 'true'} if critical_known else None
        weight_raw = row.get('weight', '')
        weight_invalid = False
        if 'weight' in row and str(weight_raw).strip() != '':
            try:
                share = Decimal(str(weight_raw))
            except Exception:
                weight_invalid = True
            else:
                weight_invalid = share < 0 or share > 1
        parsed_tasks.append(
            ParsedTask(
                uid=task_id,
                outline_level=depth,
                outline_number=f'{wbs_code}.{code}' if wbs_code else code,
                wbs_code=code,
                name=name,
                is_summary=False,
                start=_parse_p6_date(row.get('target_start_date', '')),
                finish=_parse_p6_date(row.get('target_end_date', '')),
                actual_start=_parse_p6_date(row.get('act_start_date', '')),
                actual_finish=_parse_p6_date(row.get('act_end_date', '')),
                duration_days=None if duration_inexact else duration_days,
                duration_inexact=duration_inexact,
                percent_complete=None if percent_invalid else percent,
                percent_invalid=percent_invalid,
                predecessors=pred_map.get(task_id, []),
                node_key=f'task:{task_id}',
                parent_key=f'wbs:{wbs_id}' if wbs_id else None,
                milestone_flag=task_type in ('TT_Mile', 'TT_FinMile'),
                total_slack_days=None if total_inexact else total_days,
                free_slack_days=None if free_inexact else free_days,
                slack_inexact=total_inexact,
                free_slack_inexact=free_inexact,
                is_critical=is_critical,
                critical_known=critical_known,
                weight_invalid=weight_invalid,
            )
        )

    parsed = ParseResult(tasks=parsed_tasks, warnings=warnings, has_calendar='CALENDAR' in tables)
    parsed.recognized_kind = 'xer'
    return parsed


@transaction.atomic
def execute_p6_import(
    project: Project,
    file_bytes: bytes,
    *,
    filename: str,
    replace: bool = False,
    progress_callback=None,
    user=None,
    prepared=None,
) -> dict:
    parsed = prepared if prepared is not None else parse_p6_xer(file_bytes)
    plan = resolve(parsed, max_depth=project.max_depth)
    if plan.blocking:
        raise ImportFidelityError(plan.blocking)
    if not plan.packages and not plan.activities:
        from schedule.services.import_safety import assert_can_import
        assert_can_import(project, user)
        return unchanged_result(plan)
    removed = guard_and_maybe_replace(project, user, replace)
    plan = annotate_project(plan, project)
    audit_user = user
    warnings = list(parsed.warnings)
    warnings.extend(plan.warning_texts())

    uid_to_activity: dict[str, Activity] = {}
    outline_to_wbs: dict[str, WBS] = {}
    wbs_count = 0
    activity_count = 0
    existing_wbs = {wbs.wbs_code: wbs for wbs in WBS.objects.filter(project=project)}
    pending = list(plan.packages)
    while pending:
        progressed = False
        next_pending = []
        for task in pending:
            refresh_cached_wbs(outline_to_wbs)
            parent = outline_to_wbs.get(task.parent_key) if task.parent_key else None
            if task.parent_key and parent is None:
                next_pending.append(task)
                continue
            code = task.wbs_code
            if code in existing_wbs:
                warnings.append(f'Duplicate WBS code "{code}" — skipped.')
                outline_to_wbs[task.node_key] = existing_wbs[code]
                progressed = True
                continue
            node_fields = {
                'project_id': project.id,
                'wbs_code': code,
                'wbs_name': task.name,
                'created_by': audit_user,
                'updated_by': audit_user,
            }
            if parent is not None:
                wbs = parent.add_child(**node_fields)
            else:
                wbs = WBS.add_root(**node_fields)
            outline_to_wbs[task.node_key] = wbs
            existing_wbs[code] = wbs
            wbs_count += 1
            progressed = True
        if not progressed:
            break
        pending = next_pending

    def get_wbs_p6(task, outline_map, warning_list):
        wbs = outline_map.get(task.parent_key)
        if wbs is None:
            warning_list.append(f'activity_without_parent: {task.name}')
            return None
        return wbs

    existing_activities = set(Activity.objects.filter(project=project).values_list('activity_code', flat=True))
    done, activity_count = extract_activities_from_tasks(
        plan.activities, project, existing_activities, uid_to_activity,
        outline_to_wbs, warnings, audit_user, 0, activity_count, get_wbs_p6,
    )
    relations_to_create = []
    for link in plan.links:
        predecessor = uid_to_activity.get(link['predecessor_uid'])
        successor = uid_to_activity.get(link['successor_uid'])
        if predecessor is None or successor is None:
            continue
        relations_to_create.append(ActivityRelation(
            predecessor=predecessor,
            successor=successor,
            relation_type=link['relation_type'],
            lag_days=link['lag_days'],
            created_by=audit_user,
            updated_by=audit_user,
        ))
    relation_result = bulk_create_relations(
        relations_to_create, wbs_count, activity_count, warnings, progress_callback
    )
    created_any = any(
        relation_result[key] for key in ('wbs_nodes_created', 'activities_created', 'relations_created')
    )
    baseline = open_working_copy(project, audit_user, filename, 'P6 Import', created_any)
    if baseline is not None:
        BaselineActivity.objects.bulk_create(
            baseline_rows_for(baseline, plan.activities, uid_to_activity)
        )
    return {
        **relation_result,
        **result_flags(removed, relation_result, baseline, duplicate_messages(warnings)),
        **display_result(plan, relation_result),
    }


__all__ = ['parse_p6_xer', 'build_preview', 'execute_p6_import']

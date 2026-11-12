"""Microsoft Project XML import parser and executor."""
from __future__ import annotations

import defusedxml.ElementTree as ET
from defusedxml.common import DefusedXmlException, DTDForbidden
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

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
    days_from_msp_duration,
    note_existing,
    refresh_cached_wbs,
    unchanged_result,
    days_from_tenths,
    preview_payload,
    relation_type_for,
    resolve,
)
from schedule.services.shared_import import extract_activities_from_tasks, bulk_create_relations


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
    days, inexact = days_from_msp_duration(value)
    if inexact:
        return None
    return days


def _child(el, name: str):
    if el is None:
        return None
    for child in el:
        if _local(child.tag) == name:
            return child
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
    is_critical: bool | None = None
    predecessors: list[dict] = field(default_factory=list)
    node_key: str = ''
    parent_key: str | None = None
    is_milestone: bool = False
    milestone_flag: bool = False
    duration_inexact: bool = False
    actual_start: date | None = None
    actual_finish: date | None = None
    percent_invalid: bool = False
    critical_known: bool = False
    total_slack_days: int | None = None
    free_slack_days: int | None = None
    slack_inexact: bool = False
    free_slack_inexact: bool = False
    weight_invalid: bool = False


@dataclass
class ParseResult:
    tasks: list[ParsedTask]
    warnings: list[str] = field(default_factory=list)
    has_calendar: bool = False


def is_mpp_bytes(file_bytes: bytes) -> bool:
    from schedule.services.mpp_errors import OLE_MAGIC

    return bool(file_bytes) and file_bytes.startswith(OLE_MAGIC)


def parse_msp_family(file_bytes: bytes, *, filename: str = '') -> ParseResult:
    """Parse MSP XML or native MPP (convert then XML) into ParseResult."""
    name = (filename or '').lower()
    if name.endswith('.mpp') or is_mpp_bytes(file_bytes):
        from schedule.services.mpp_convert import convert_mpp_to_mspdi

        xml_bytes = convert_mpp_to_mspdi(file_bytes)
        return parse_msp_xml(xml_bytes)
    return parse_msp_xml(file_bytes)


def parse_msp_xml(file_bytes: bytes) -> ParseResult:
    # defusedxml protects against XML bomb, XXE, and billion laughs attacks on
    # user-uploaded MSP XML files. Never revert to stdlib xml.etree on user input.
    warnings: list[str] = []
    try:
        root = ET.fromstring(file_bytes)
    except (ET.ParseError, DefusedXmlException, DTDForbidden):
        raise ValueError('Invalid XML')

    if _local(root.tag) != 'Project':
        raise ValueError('File must be a Microsoft Project XML export with <Project> root.')
    has_calendar = any(_local(element.tag) == 'Calendar' for element in root.iter())

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
        outline_number = _text(task_el, 'OutlineNumber')
        wbs_code = _text(task_el, 'WBS') or outline_number
        name = _text(task_el, 'Name')
        if not name:
            warnings.append(f'Task UID {uid} has no name — skipped.')
            continue
        summary = _text(task_el, 'Summary', '0') in ('1', 'true', 'True')
        duration_raw = _text(task_el, 'Duration')
        duration_days, duration_inexact = days_from_msp_duration(duration_raw)
        if outline_number:
            node_key = outline_number
            parent_key = outline_number.rsplit('.', 1)[0] if '.' in outline_number else None
        else:
            node_key = f'uid:{uid}'
            parent_key = None
        weight_text = _text(task_el, 'Weight')
        weight_invalid = False
        if weight_text:
            try:
                share = Decimal(weight_text)
            except Exception:
                weight_invalid = True
            else:
                weight_invalid = share < 0 or share > 1

        preds = []
        for rel in task_el:
            if _local(rel.tag) != 'PredecessorLink':
                continue
            raw_lag = int(_text(rel, 'LinkLag', '0') or '0')
            lag_days, lag_inexact = days_from_tenths(raw_lag)
            preds.append({
                'uid': _text(rel, 'PredecessorUID'),
                'type': _text(rel, 'Type', ''),
                'relation_type': relation_type_for(_text(rel, 'Type', ''), prima=False),
                'lag_days': lag_days,
                'lag_exact': not lag_inexact,
            })

        pct = _text(task_el, 'PercentComplete')
        percent = Decimal(pct) if pct else None
        percent_invalid = percent is not None and (percent < 0 or percent > 100)
        critical_el = _child(task_el, 'Critical')
        total_el = _child(task_el, 'TotalSlack')
        free_el = _child(task_el, 'FreeSlack')
        total_days, total_inexact = (None, False)
        free_days, free_inexact = (None, False)
        if total_el is not None and (total_el.text or '').strip():
            total_days, total_inexact = days_from_tenths(int((total_el.text or '0').strip()))
        if free_el is not None and (free_el.text or '').strip():
            free_days, free_inexact = days_from_tenths(int((free_el.text or '0').strip()))
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
                duration_days=None if duration_inexact else duration_days,
                percent_complete=None if percent_invalid else percent,
                total_slack=None if total_inexact else total_days,
                free_slack=None if free_inexact else free_days,
                is_critical=(
                    (critical_el.text or '').strip() in ('1', 'true', 'True')
                    if critical_el is not None else None
                ),
                predecessors=preds,
                node_key=node_key,
                parent_key=parent_key,
                milestone_flag=_text(task_el, 'Milestone', '0') in ('1', 'true', 'True'),
                duration_inexact=duration_inexact,
                actual_start=_parse_msp_date(_text(task_el, 'ActualStart')),
                actual_finish=_parse_msp_date(_text(task_el, 'ActualFinish')),
                percent_invalid=percent_invalid,
                critical_known=critical_el is not None,
                total_slack_days=None if total_inexact else total_days,
                free_slack_days=None if free_inexact else free_days,
                slack_inexact=total_inexact,
                free_slack_inexact=free_inexact,
                weight_invalid=weight_invalid,
            )
        )

    return ParseResult(tasks=tasks, warnings=warnings, has_calendar=has_calendar)


def build_preview(parsed: ParseResult, max_depth: int | None = None, existing_wbs_codes=None, existing_activity_codes=None) -> dict:
    """Non-destructive preview tree from the same plan confirm will store."""
    plan = note_existing(resolve(parsed, max_depth=max_depth), existing_wbs_codes, existing_activity_codes)
    return preview_payload(plan)


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
    parsed = parse_msp_family(file_bytes, filename=filename)
    plan = note_existing(
        resolve(parsed, max_depth=project.max_depth),
        WBS.objects.filter(project=project, is_deleted=False).values_list('wbs_code', flat=True),
        Activity.objects.filter(project=project, is_deleted=False).values_list('activity_code', flat=True),
    )
    if plan.blocking:
        raise ImportFidelityError(plan.blocking)
    if not plan.packages and not plan.activities:
        from schedule.services.import_safety import assert_can_import
        assert_can_import(project, user)
        return unchanged_result(plan)
    removed = guard_and_maybe_replace(project, user, replace)
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
            code = task.wbs_code or task.outline_number
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

    def get_wbs_msp(task, outline_map, warning_list):
        wbs = outline_map.get(task.parent_key)
        if wbs is None:
            warning_list.append(f'activity_without_parent: {task.name}')
            return None
        return wbs

    existing_activities = set(Activity.objects.filter(project=project).values_list('activity_code', flat=True))
    done, activity_count = extract_activities_from_tasks(
        plan.activities, project, existing_activities, uid_to_activity,
        outline_to_wbs, warnings, audit_user, 0, activity_count, get_wbs_msp,
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
    baseline = open_working_copy(project, audit_user, filename, 'MSP Import', created_any)
    if baseline is not None:
        BaselineActivity.objects.bulk_create(
            baseline_rows_for(baseline, parsed.tasks, uid_to_activity)
        )
    return {
        **relation_result,
        **result_flags(removed, relation_result, baseline, duplicate_messages(warnings)),
        'warning_items': [{'code': note.code, 'row': note.row} for note in plan.warnings],
        'blocking': [],
        **plan.counts(),
    }

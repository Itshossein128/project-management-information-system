"""Gantt chart data preparation."""

from __future__ import annotations

from projects.models import Activity, ActivityRelation
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule
from schedule.services.critical_path_validity import evaluate_critical_path_validity


def get_gantt_data(project_id, baseline_id=None) -> dict:
    baseline = None
    if baseline_id:
        baseline = BaselineSchedule.objects.filter(pk=baseline_id, project_id=project_id).first()
    if not baseline:
        baseline = BaselineSchedule.objects.filter(project_id=project_id, is_current=True).first()

    validity = evaluate_critical_path_validity(project_id)
    critical_ids = set()
    baseline_map = {}
    if baseline:
        for ba in BaselineActivity.objects.filter(baseline=baseline).select_related('activity'):
            baseline_map[ba.activity_id] = ba
            if validity['valid'] and ba.is_critical:
                critical_ids.add(ba.activity_id)

    activities = Activity.objects.filter(project_id=project_id, is_deleted=False).select_related('wbs', 'responsible')

    # ⚡ Bolt: Bulk fetch dependencies for all project activities in a single query to eliminate N+1 calls
    deps_map: dict[str, list[str]] = {}
    for rel in ActivityRelation.objects.filter(
        successor__project_id=project_id,
        successor__is_deleted=False,
        is_deleted=False,
    ).select_related('predecessor'):
        if rel.predecessor_id and rel.predecessor.activity_code:
            deps_map.setdefault(rel.successor_id, []).append(rel.predecessor.activity_code)

    # ⚡ Bolt: Bulk fetch progress records ordered by report_date ascending so that the latest record overwrites earlier ones in progress_map
    progress_map = {}
    for p in ActivityProgress.objects.filter(
        activity__project_id=project_id,
        activity__is_deleted=False,
    ).order_by('report_date'):
        progress_map[p.activity_id] = p

    tasks = []
    for act in activities:
        ba = baseline_map.get(act.id)
        dep_codes = deps_map.get(act.id, [])

        prog = progress_map.get(act.id)
        progress_pct = int(float(prog.actual_progress or 0) * 100) if prog else 0

        baseline_finish = ba.planned_finish if ba else None
        compare_finish = act.forecast_finish or act.actual_finish
        delay_days = (compare_finish - baseline_finish).days if compare_finish and baseline_finish else None
        tasks.append({
            'id': act.activity_code,
            'name': act.activity_name,
            'start': act.planned_start.isoformat() if act.planned_start else None,
            'end': act.planned_finish.isoformat() if act.planned_finish else None,
            'planned_start': act.planned_start.isoformat() if act.planned_start else None,
            'planned_finish': act.planned_finish.isoformat() if act.planned_finish else None,
            'actual_start': act.actual_start.isoformat() if act.actual_start else None,
            'actual_finish': act.actual_finish.isoformat() if act.actual_finish else None,
            'forecast_start': act.forecast_start.isoformat() if act.forecast_start else None,
            'forecast_finish': act.forecast_finish.isoformat() if act.forecast_finish else None,
            'progress': progress_pct,
            'dependencies': ','.join(dep_codes),
            'wbs_code': act.wbs.wbs_code if act.wbs_id else '',
            'is_critical': act.id in critical_ids,
            'is_milestone': act.is_milestone,
            'baseline_start': ba.planned_start.isoformat() if ba and ba.planned_start else None,
            'baseline_end': ba.planned_finish.isoformat() if ba and ba.planned_finish else None,
            'delay_days': delay_days,
            'status': act.status,
            'responsible': act.responsible.full_name if act.responsible_id else '',
            'activity_id': str(act.id),
        })

    dates = [t['start'] for t in tasks if t['start']] + [t['end'] for t in tasks if t['end']]
    return {
        'tasks': tasks,
        'baseline_name': baseline.version_name if baseline else '',
        'project_start': min(dates) if dates else None,
        'project_end': max(dates) if dates else None,
        'critical_path': validity,
    }

"""Gantt chart data preparation."""

from __future__ import annotations

from projects.models import Activity, ActivityRelation
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule


def get_gantt_data(project_id, baseline_id=None) -> dict:
    baseline = None
    if baseline_id:
        baseline = BaselineSchedule.objects.filter(pk=baseline_id, project_id=project_id).first()
    if not baseline:
        baseline = BaselineSchedule.objects.filter(project_id=project_id, is_current=True).first()

    critical_ids = set()
    baseline_map = {}
    if baseline:
        for ba in BaselineActivity.objects.filter(baseline=baseline).select_related('activity'):
            baseline_map[ba.activity_id] = ba
            if ba.is_critical:
                critical_ids.add(ba.activity_id)

    activities = Activity.objects.filter(project_id=project_id, is_deleted=False).select_related('wbs', 'responsible')
    tasks = []
    for act in activities:
        ba = baseline_map.get(act.id)
        deps = ActivityRelation.objects.filter(successor=act, is_deleted=False).select_related('predecessor')
        dep_codes = [d.predecessor.activity_code for d in deps if d.predecessor_id]

        prog = ActivityProgress.objects.filter(activity=act).order_by('-report_date').first()
        progress_pct = int(float(prog.actual_progress or 0) * 100) if prog else 0

        tasks.append({
            'id': act.activity_code,
            'name': act.activity_name,
            'start': act.planned_start.isoformat() if act.planned_start else None,
            'end': act.planned_finish.isoformat() if act.planned_finish else None,
            'progress': progress_pct,
            'dependencies': ','.join(dep_codes),
            'wbs_code': act.wbs.wbs_code if act.wbs_id else '',
            'is_critical': act.id in critical_ids,
            'baseline_start': ba.planned_start.isoformat() if ba and ba.planned_start else None,
            'baseline_end': ba.planned_finish.isoformat() if ba and ba.planned_finish else None,
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
    }

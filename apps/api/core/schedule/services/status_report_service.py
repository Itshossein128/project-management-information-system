"""Schedule status / milestone-delay report aggregator."""

from __future__ import annotations

from datetime import date

from django.utils import timezone

from projects.models import Activity
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.services.critical_path_validity import evaluate_critical_path_validity


def build_schedule_status(project_id, *, as_of: date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    activities = list(
        Activity.objects.filter(project_id=project_id, is_deleted=False).order_by('activity_code'),
    )

    baseline = BaselineSchedule.objects.filter(
        project_id=project_id,
        is_current=True,
        is_locked=True,
    ).first()
    if baseline is None:
        baseline = BaselineSchedule.objects.filter(
            project_id=project_id,
            is_current=True,
        ).first()

    baseline_finish_map: dict = {}
    if baseline:
        for ba in BaselineActivity.objects.filter(baseline=baseline):
            baseline_finish_map[ba.activity_id] = ba.planned_finish

    critical_path = evaluate_critical_path_validity(project_id)
    critical_set = set(critical_path.get('critical_activity_ids') or [])
    near_set = set(critical_path.get('near_critical_activity_ids') or [])

    has_planned = False
    has_actual = False
    has_forecast = False
    forecast_candidates: list[date] = []

    milestones = []
    delays = []

    for act in activities:
        if act.planned_finish or act.planned_start:
            has_planned = True
        if act.actual_finish or act.actual_start:
            has_actual = True
        if act.forecast_finish or act.forecast_start:
            has_forecast = True

        finish_for_forecast = act.forecast_finish or act.planned_finish
        if finish_for_forecast:
            forecast_candidates.append(finish_for_forecast)

        baseline_finish = baseline_finish_map.get(act.id)
        delay_days = None
        compare_finish = act.forecast_finish or act.actual_finish
        ref_finish = baseline_finish or act.planned_finish
        if compare_finish and ref_finish:
            delay_days = (compare_finish - ref_finish).days

        if act.is_milestone:
            milestones.append({
                'activity_id': str(act.id),
                'activity_code': act.activity_code,
                'activity_name': act.activity_name,
                'planned_finish': act.planned_finish.isoformat() if act.planned_finish else None,
                'forecast_finish': act.forecast_finish.isoformat() if act.forecast_finish else None,
                'actual_finish': act.actual_finish.isoformat() if act.actual_finish else None,
                'baseline_finish': baseline_finish.isoformat() if baseline_finish else None,
                'delay_days': delay_days,
            })

        is_delayed = delay_days is not None and delay_days > 0
        overdue = (
            act.planned_finish is not None
            and act.planned_finish < as_of
            and act.actual_finish is None
        )
        if is_delayed or overdue:
            delays.append({
                'activity_id': str(act.id),
                'activity_code': act.activity_code,
                'is_critical': str(act.id) in critical_set,
                'is_near_critical': str(act.id) in near_set,
                'planned_finish': act.planned_finish.isoformat() if act.planned_finish else None,
                'forecast_finish': act.forecast_finish.isoformat() if act.forecast_finish else None,
                'baseline_finish': baseline_finish.isoformat() if baseline_finish else None,
                'actual_finish': act.actual_finish.isoformat() if act.actual_finish else None,
                'delay_days': delay_days if delay_days is not None else (
                    (as_of - act.planned_finish).days if overdue and act.planned_finish else None
                ),
            })

    return {
        'as_of': as_of.isoformat(),
        'forecast_project_finish': max(forecast_candidates).isoformat() if forecast_candidates else None,
        'date_sets': {
            'approved_baseline_id': str(baseline.id) if baseline else None,
            'has_planned': has_planned,
            'has_actual': has_actual,
            'has_forecast': has_forecast,
        },
        'critical_path': critical_path,
        'milestones': milestones,
        'delays': delays,
    }

"""Activity date / milestone / calendar validation (FR-SCH)."""

from __future__ import annotations

from datetime import date
from typing import Any

from config.exceptions import CodedValidationError
from projects.models import Activity
from schedule.models import WorkingCalendar
from schedule.services.calendar_service import (
    get_project_default_calendar,
    is_working_day,
    resolve_calendar_for_activity,
)


def _raise(code: str, message: str) -> None:
    raise CodedValidationError(detail=message, code=code)


def resolve_calendar(
    *,
    project_id,
    working_calendar_id=None,
    activity: Activity | None = None,
) -> WorkingCalendar | None:
    if working_calendar_id is not None:
        if working_calendar_id == '':
            return get_project_default_calendar(project_id)
        cal = WorkingCalendar.objects.filter(
            pk=working_calendar_id,
            project_id=project_id,
            is_deleted=False,
        ).first()
        if cal is None:
            _raise('validation_error', 'Working calendar not found for this project.')
        return cal
    if activity is not None:
        return resolve_calendar_for_activity(activity)
    return get_project_default_calendar(project_id)


def _assert_working(calendar: WorkingCalendar | None, day: date | None, label: str) -> None:
    if day is None or calendar is None:
        return
    if not is_working_day(calendar, day):
        _raise('non_working_day', f'{label} falls on a non-working day.')


def validate_activity_dates(
    *,
    project_id,
    planned_start: date | None = None,
    planned_finish: date | None = None,
    forecast_start: date | None = None,
    forecast_finish: date | None = None,
    duration_days: int | None = None,
    is_milestone: bool = False,
    working_calendar_id=None,
    activity: Activity | None = None,
    check_calendar: bool = True,
) -> None:
    """Validate date invariants. Raises CodedValidationError with stable codes."""
    if is_milestone and duration_days != 0:
        _raise('invalid_milestone', 'Milestone activities must have duration_days=0.')

    if planned_start and planned_finish and planned_finish < planned_start:
        if not is_milestone:
            _raise('impossible_planned_dates', 'planned_finish must be on or after planned_start.')

    if forecast_start and forecast_finish and forecast_finish < forecast_start:
        _raise('impossible_forecast_dates', 'forecast_finish must be on or after forecast_start.')

    if not check_calendar:
        return

    calendar = resolve_calendar(
        project_id=project_id,
        working_calendar_id=working_calendar_id,
        activity=activity,
    )
    _assert_working(calendar, planned_start, 'planned_start')
    _assert_working(calendar, planned_finish, 'planned_finish')
    _assert_working(calendar, forecast_start, 'forecast_start')
    _assert_working(calendar, forecast_finish, 'forecast_finish')


def validate_activity_payload(project_id, data: dict[str, Any], *, instance: Activity | None = None) -> None:
    """Merge instance values with partial payload then validate."""
    def pick(key, default=None):
        if key in data:
            return data[key]
        if instance is not None:
            return getattr(instance, key)
        return default

    working_calendar_id = data['working_calendar_id'] if 'working_calendar_id' in data else (
        instance.working_calendar_id if instance is not None else None
    )

    validate_activity_dates(
        project_id=project_id,
        planned_start=pick('planned_start'),
        planned_finish=pick('planned_finish'),
        forecast_start=pick('forecast_start'),
        forecast_finish=pick('forecast_finish'),
        duration_days=pick('duration_days'),
        is_milestone=bool(pick('is_milestone', False)),
        working_calendar_id=working_calendar_id,
        activity=instance,
    )

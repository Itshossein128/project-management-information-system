"""Working calendar CRUD and working-day resolution."""

from __future__ import annotations

from datetime import date

from django.db import transaction

from config.exceptions import ConflictError
from projects.models import Activity
from schedule.models import CalendarException, WorkingCalendar

WEEKDAY_FLAGS = (
    'work_monday',
    'work_tuesday',
    'work_wednesday',
    'work_thursday',
    'work_friday',
    'work_saturday',
    'work_sunday',
)


def list_calendars(project_id):
    return WorkingCalendar.objects.filter(project_id=project_id).order_by('name')


@transaction.atomic
def create_calendar(*, project_id, user, name, is_default=False, **weekday_kwargs) -> WorkingCalendar:
    calendar = WorkingCalendar(
        project_id=project_id,
        name=name,
        is_default=bool(is_default),
        created_by=user,
        updated_by=user,
    )
    for flag in WEEKDAY_FLAGS:
        if flag in weekday_kwargs and weekday_kwargs[flag] is not None:
            setattr(calendar, flag, bool(weekday_kwargs[flag]))
    calendar.save()
    if calendar.is_default:
        _clear_other_defaults(project_id, calendar.pk)
    return calendar


@transaction.atomic
def update_calendar(calendar: WorkingCalendar, user, **fields) -> WorkingCalendar:
    for key, value in fields.items():
        if key in ('name', 'is_default', *WEEKDAY_FLAGS) and value is not None:
            setattr(calendar, key, value)
    calendar.updated_by = user
    calendar.save()
    if calendar.is_default:
        _clear_other_defaults(calendar.project_id, calendar.pk)
    return calendar


def soft_delete_calendar(calendar: WorkingCalendar, user) -> None:
    if Activity.objects.filter(working_calendar_id=calendar.pk, is_deleted=False).exists():
        raise ConflictError('Calendar is referenced by activities.', code='calendar_in_use')
    calendar.soft_delete(user=user)


def _clear_other_defaults(project_id, calendar_id) -> None:
    WorkingCalendar.objects.filter(
        project_id=project_id,
        is_default=True,
        is_deleted=False,
    ).exclude(pk=calendar_id).update(is_default=False)


def get_project_default_calendar(project_id) -> WorkingCalendar | None:
    return WorkingCalendar.objects.filter(
        project_id=project_id,
        is_default=True,
        is_deleted=False,
    ).first()


def resolve_calendar_for_activity(activity: Activity) -> WorkingCalendar | None:
    if activity.working_calendar_id:
        cal = activity.working_calendar
        if cal and not cal.is_deleted:
            return cal
    return get_project_default_calendar(activity.project_id)


def is_working_day(calendar: WorkingCalendar | None, day: date) -> bool:
    """Return True if day is a working day on the calendar (or True if no calendar)."""
    if calendar is None:
        return True

    exception = CalendarException.objects.filter(
        calendar=calendar,
        exception_date=day,
        is_deleted=False,
    ).first()
    if exception is not None:
        return bool(exception.is_working)

    flag = WEEKDAY_FLAGS[day.weekday()]  # Monday=0
    return bool(getattr(calendar, flag))


@transaction.atomic
def create_exception(*, calendar, user, exception_date, is_working=False, name='') -> CalendarException:
    if CalendarException.objects.filter(
        calendar=calendar,
        exception_date=exception_date,
        is_deleted=False,
    ).exists():
        raise ConflictError('Exception already exists for this date.', code='calendar_exception_duplicate')
    return CalendarException.objects.create(
        calendar=calendar,
        exception_date=exception_date,
        is_working=bool(is_working),
        name=name or '',
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def update_exception(exc: CalendarException, user, **fields) -> CalendarException:
    if 'exception_date' in fields and fields['exception_date'] is not None:
        new_date = fields['exception_date']
        if (
            CalendarException.objects.filter(
                calendar_id=exc.calendar_id,
                exception_date=new_date,
                is_deleted=False,
            )
            .exclude(pk=exc.pk)
            .exists()
        ):
            raise ConflictError('Exception already exists for this date.', code='calendar_exception_duplicate')
        exc.exception_date = new_date
    if 'is_working' in fields and fields['is_working'] is not None:
        exc.is_working = bool(fields['is_working'])
    if 'name' in fields and fields['name'] is not None:
        exc.name = fields['name']
    exc.updated_by = user
    exc.save()
    return exc


def soft_delete_exception(exc: CalendarException, user) -> None:
    exc.soft_delete(user=user)

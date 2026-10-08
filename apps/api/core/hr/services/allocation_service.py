from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model

from config.exceptions import ConflictError, CodedValidationError
from hr.models import (
    CapacityException,
    CapacityExceptionStatus,
    ResourceAllocation,
    ResourceAllocationStatus,
)
from hr.services.capacity_service import assert_person_active_for_allocation, check_conflict, hours_to_percent
from projects.models import Activity, Project, WBS

User = get_user_model()


def _validate_scope(project_id, wbs_id, activity_id) -> None:
    if wbs_id is not None:
        if not WBS.objects.filter(pk=wbs_id, project_id=project_id, is_deleted=False).exists():
            raise CodedValidationError(detail='WBS is not in this project.', code='scope_mismatch')
    if activity_id is not None:
        activity = Activity.objects.filter(pk=activity_id, project_id=project_id, is_deleted=False).first()
        if activity is None:
            raise CodedValidationError(detail='Activity is not in this project.', code='scope_mismatch')
        if wbs_id is not None and activity.wbs_id != wbs_id:
            raise CodedValidationError(
                detail='Activity WBS does not match allocation WBS.',
                code='scope_mismatch',
            )


def _resolve_capacity_percent(capacity_percent, capacity_hours) -> Decimal:
    if capacity_percent is not None:
        return Decimal(capacity_percent)
    if capacity_hours is not None:
        return hours_to_percent(Decimal(capacity_hours))
    raise CodedValidationError(detail='capacity_percent or capacity_hours is required.', code='validation_error')


def _validate_exception(capacity_exception_id, person_id, project_id, requested_percent) -> CapacityException | None:
    if capacity_exception_id is None:
        return None
    exc = CapacityException.objects.filter(
        pk=capacity_exception_id,
        project_id=project_id,
        person_id=person_id,
        is_deleted=False,
    ).first()
    if exc is None:
        raise CodedValidationError(detail='Capacity exception not found.', code='exception_not_approved')
    if exc.status != CapacityExceptionStatus.APPROVED:
        raise CodedValidationError(detail='Capacity exception is not approved.', code='exception_not_approved')
    if Decimal(exc.requested_capacity_percent) < Decimal(requested_percent):
        raise CodedValidationError(
            detail='Approved exception does not cover requested capacity.',
            code='exception_not_approved',
        )
    return exc


def _enforce_capacity(person, start_date, end_date, requested_percent, *, exclude_id, exception_id, project_id):
    conflict = check_conflict(
        person,
        start_date,
        end_date,
        requested_percent,
        exclude_allocation_id=exclude_id,
    )
    if not conflict['would_conflict']:
        return None, False

    exc = _validate_exception(exception_id, person.id, project_id, requested_percent)
    if exc is None:
        raise ConflictError(
            detail={
                'available': str(conflict['available']),
                'committed': str(conflict['committed']),
                'requested': str(conflict['requested']),
                'overlapping_allocation_ids': conflict['overlapping_allocation_ids'],
            },
            code='capacity_conflict',
        )
    return exc, True


def create_allocation(
    *,
    project: Project,
    person_id: UUID,
    user,
    data: dict,
) -> ResourceAllocation:
    person = User.objects.get(pk=person_id)
    assert_person_active_for_allocation(person)

    start_date = data['start_date']
    end_date = data['end_date']
    if end_date < start_date:
        raise CodedValidationError(detail='end_date must be on or after start_date.', code='validation_error')

    wbs_id = data.get('wbs_id')
    activity_id = data.get('activity_id')
    _validate_scope(project.id, wbs_id, activity_id)

    requested_percent = _resolve_capacity_percent(data.get('capacity_percent'), data.get('capacity_hours'))

    exc, has_exception = _enforce_capacity(
        person,
        start_date,
        end_date,
        requested_percent,
        exclude_id=None,
        exception_id=data.get('capacity_exception_id'),
        project_id=project.id,
    )

    allocation = ResourceAllocation.objects.create(
        project=project,
        person=person,
        wbs_id=wbs_id,
        activity_id=activity_id,
        start_date=start_date,
        end_date=end_date,
        role=data['role'],
        capacity_percent=requested_percent,
        capacity_hours=data.get('capacity_hours'),
        work_location=data.get('work_location') or '',
        supervisor_id=data.get('supervisor_id'),
        status=data.get('status') or ResourceAllocationStatus.PLANNED,
        has_capacity_exception=has_exception,
        capacity_exception=exc,
        created_by=user,
        updated_by=user,
    )
    if exc is not None and exc.allocation_id is None:
        exc.allocation = allocation
        exc.save(update_fields=['allocation', 'updated_at'])
    return allocation


def update_allocation(allocation: ResourceAllocation, user, data: dict) -> ResourceAllocation:
    person = allocation.person
    if 'person_id' in data:
        person = User.objects.get(pk=data['person_id'])
    assert_person_active_for_allocation(person)

    start_date = data.get('start_date', allocation.start_date)
    end_date = data.get('end_date', allocation.end_date)
    if end_date < start_date:
        raise CodedValidationError(detail='end_date must be on or after start_date.', code='validation_error')

    wbs_id = data.get('wbs_id', allocation.wbs_id)
    activity_id = data.get('activity_id', allocation.activity_id)
    _validate_scope(allocation.project_id, wbs_id, activity_id)

    capacity_percent = data.get('capacity_percent', allocation.capacity_percent)
    capacity_hours = data.get('capacity_hours', allocation.capacity_hours)
    if 'capacity_hours' in data and data.get('capacity_percent') is None and data.get('capacity_hours') is not None:
        capacity_percent = hours_to_percent(Decimal(data['capacity_hours']))
    elif 'capacity_percent' in data:
        capacity_percent = Decimal(data['capacity_percent'])

    exception_id = data.get('capacity_exception_id', allocation.capacity_exception_id)
    exc, has_exception = _enforce_capacity(
        person,
        start_date,
        end_date,
        Decimal(capacity_percent),
        exclude_id=allocation.id,
        exception_id=exception_id,
        project_id=allocation.project_id,
    )

    for field, attr in (
        ('role', 'role'),
        ('work_location', 'work_location'),
        ('status', 'status'),
    ):
        if field in data:
            setattr(allocation, attr, data[field])

    allocation.person = person
    allocation.wbs_id = wbs_id
    allocation.activity_id = activity_id
    allocation.start_date = start_date
    allocation.end_date = end_date
    allocation.capacity_percent = Decimal(capacity_percent)
    allocation.capacity_hours = capacity_hours
    allocation.supervisor_id = data.get('supervisor_id', allocation.supervisor_id)
    allocation.has_capacity_exception = has_exception
    allocation.capacity_exception = exc
    allocation.updated_by = user
    allocation.save()
    return allocation


def soft_delete_allocation(allocation: ResourceAllocation, user) -> None:
    allocation.soft_delete(user=user)

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db.models import Q

from authentication.models import User, UserStatus
from hr.models import ResourceAllocation, ResourceAllocationStatus

STANDARD_DAY_HOURS = Decimal('8')


def hours_to_percent(hours: Decimal) -> Decimal:
    return (Decimal(hours) / STANDARD_DAY_HOURS) * Decimal('100')


def _overlap_filter(start_date: date, end_date: date) -> Q:
    return Q(start_date__lte=end_date, end_date__gte=start_date)


def compute_committed(
    person: User,
    from_date: date,
    to_date: date,
    *,
    exclude_allocation_id: UUID | None = None,
) -> Decimal:
    qs = ResourceAllocation.objects.filter(
        person=person,
        is_deleted=False,
    ).exclude(status=ResourceAllocationStatus.CANCELLED)
    qs = qs.filter(_overlap_filter(from_date, to_date))
    if exclude_allocation_id is not None:
        qs = qs.exclude(pk=exclude_allocation_id)

    total = Decimal('0')
    for row in qs.only('capacity_percent'):
        total += Decimal(row.capacity_percent)
    return total


def check_conflict(
    person: User,
    from_date: date,
    to_date: date,
    requested_percent: Decimal,
    *,
    exclude_allocation_id: UUID | None = None,
) -> dict:
    available = Decimal(person.default_capacity_percent)
    committed = compute_committed(
        person,
        from_date,
        to_date,
        exclude_allocation_id=exclude_allocation_id,
    )
    requested = Decimal(requested_percent)
    overlapping_ids = list(
        ResourceAllocation.objects.filter(
            person=person,
            is_deleted=False,
        )
        .exclude(status=ResourceAllocationStatus.CANCELLED)
        .filter(_overlap_filter(from_date, to_date))
        .values_list('id', flat=True)
    )
    if exclude_allocation_id is not None:
        overlapping_ids = [i for i in overlapping_ids if i != exclude_allocation_id]

    would_conflict = (committed + requested) > available
    return {
        'available': available,
        'committed': committed,
        'requested': requested,
        'overlapping_allocation_ids': [str(i) for i in overlapping_ids],
        'would_conflict': would_conflict,
    }


def assert_person_active_for_allocation(person: User) -> None:
    from config.exceptions import CodedValidationError

    if not person.is_active or person.status in (UserStatus.INACTIVE, UserStatus.SUSPENDED):
        raise CodedValidationError(detail='Person is not active for allocation.', code='person_inactive')

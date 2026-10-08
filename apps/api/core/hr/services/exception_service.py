from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from config.exceptions import CodedValidationError
from hr.models import CapacityException, CapacityExceptionStatus
from hr.services.capacity_service import check_conflict


def create_exception(*, project, person, user, data: dict) -> CapacityException:
    start_date = data['start_date']
    end_date = data['end_date']
    if end_date < start_date:
        raise CodedValidationError(detail='end_date must be on or after start_date.', code='validation_error')

    requested = Decimal(data['requested_capacity_percent'])
    conflict = check_conflict(person, start_date, end_date, requested)

    status = CapacityExceptionStatus.DRAFT
    submitted_at = None
    reason = data.get('reason') or ''
    if data.get('submit'):
        if not reason.strip():
            raise CodedValidationError(detail='Reason is required to submit.', code='validation_error')
        status = CapacityExceptionStatus.SUBMITTED
        submitted_at = timezone.now()

    exc = CapacityException.objects.create(
        project=project,
        person=person,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status=status,
        requested_capacity_percent=requested,
        overlapping_snapshot={
            'available': str(conflict['available']),
            'committed': str(conflict['committed']),
            'requested': str(conflict['requested']),
            'overlapping_allocation_ids': conflict['overlapping_allocation_ids'],
        },
        submitted_at=submitted_at,
        allocation_id=data.get('allocation_id'),
        created_by=user,
        updated_by=user,
    )
    return exc


def submit_exception(exc: CapacityException, user) -> CapacityException:
    if exc.status != CapacityExceptionStatus.DRAFT:
        raise CodedValidationError(detail='Only draft exceptions can be submitted.', code='invalid_status_transition')
    if not exc.reason.strip():
        raise CodedValidationError(detail='Reason is required to submit.', code='validation_error')
    exc.status = CapacityExceptionStatus.SUBMITTED
    exc.submitted_at = timezone.now()
    exc.updated_by = user
    exc.save(update_fields=['status', 'submitted_at', 'updated_by', 'updated_at'])
    return exc


def approve_exception(exc: CapacityException, user, decision_notes: str = '') -> tuple[CapacityException, bool]:
    """Approve exception. Returns (exception, soft_sod_warn) when approver == creator."""
    if exc.status != CapacityExceptionStatus.SUBMITTED:
        raise CodedValidationError(detail='Only submitted exceptions can be approved.', code='invalid_status_transition')
    soft_sod_warn = bool(exc.created_by_id and exc.created_by_id == getattr(user, 'id', None))
    exc.status = CapacityExceptionStatus.APPROVED
    exc.decided_by = user
    exc.decided_at = timezone.now()
    exc.decision_notes = decision_notes or ''
    exc.updated_by = user
    exc.save()
    return exc, soft_sod_warn


def reject_exception(exc: CapacityException, user, decision_notes: str = '') -> CapacityException:
    if exc.status not in (CapacityExceptionStatus.SUBMITTED, CapacityExceptionStatus.DRAFT):
        raise CodedValidationError(detail='Exception already decided.', code='already_decided')
    if exc.status == CapacityExceptionStatus.DRAFT:
        raise CodedValidationError(detail='Submit before reject.', code='invalid_status_transition')
    exc.status = CapacityExceptionStatus.REJECTED
    exc.decided_by = user
    exc.decided_at = timezone.now()
    exc.decision_notes = decision_notes or ''
    exc.updated_by = user
    exc.save()
    return exc

"""Fiscal period lock + duplicate document warnings (FR-CORE-013/015)."""
from __future__ import annotations

from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from projects.models import FiscalPeriodLock


class FiscalPeriodLocked(ValidationError):
    def __init__(self, detail=None):
        super().__init__(
            detail
            or {
                'code': 'fiscal_period_locked',
                'message': 'This date falls in a closed fiscal period.',
            }
        )


class WarningsUnacknowledged(ValidationError):
    def __init__(self, warnings):
        super().__init__(
            {
                'code': 'warnings_unacknowledged',
                'message': 'Acknowledge warnings to finalize.',
                'warnings': warnings,
            }
        )


def create_fiscal_lock(*, project, period_start, period_end, reason, user) -> FiscalPeriodLock:
    reason = (reason or '').strip()
    if period_end < period_start:
        raise ValidationError({'period_end': 'period_end must be >= period_start'})
    if len(reason) < 3:
        raise ValidationError({'reason': 'reason must be at least 3 characters'})

    overlap = FiscalPeriodLock.objects.filter(
        project=project,
        is_active=True,
        period_start__lte=period_end,
        period_end__gte=period_start,
    ).exists()
    if overlap:
        raise ValidationError(
            {'code': 'overlapping_fiscal_lock', 'message': 'Overlaps an active fiscal lock.'}
        )

    return FiscalPeriodLock.objects.create(
        project=project,
        period_start=period_start,
        period_end=period_end,
        reason=reason,
        closed_at=timezone.now(),
        closed_by=user,
        is_active=True,
    )


def deactivate_fiscal_lock(lock: FiscalPeriodLock, *, user, reason: str = '') -> FiscalPeriodLock:
    lock.is_active = False
    lock.save(update_fields=['is_active', 'updated_at'])
    return lock


def find_active_lock(project, document_date: date) -> FiscalPeriodLock | None:
    if document_date is None:
        return None
    return (
        FiscalPeriodLock.objects.filter(
            project=project,
            is_active=True,
            period_start__lte=document_date,
            period_end__gte=document_date,
        )
        .order_by('-closed_at')
        .first()
    )


def assert_fiscal_writable(
    project,
    document_date: date,
    *,
    corrective: bool = False,
    correction_reason: str = '',
) -> FiscalPeriodLock | None:
    lock = find_active_lock(project, document_date)
    if lock is None:
        return None
    if corrective:
        if not (correction_reason or '').strip():
            raise ValidationError({'correction_reason': 'Required for corrective edits.'})
        return lock
    raise FiscalPeriodLocked()


def duplicate_document_warnings(model, project, field_name: str, value: str, *, exclude_pk=None):
    value = (value or '').strip()
    if not value:
        return []
    qs = model.objects.filter(project=project).filter(**{field_name: value})
    if hasattr(model, 'is_deleted'):
        qs = qs.filter(is_deleted=False)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        return [
            {
                'code': 'duplicate_document_ref',
                'message': f'Duplicate {field_name}: {value}',
                'field': field_name,
                'value': value,
            }
        ]
    return []


def require_warning_ack(warnings, acknowledge_warnings: bool):
    if warnings and not acknowledge_warnings:
        raise WarningsUnacknowledged(warnings)

"""Project change requests for protected identity fields."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from config.exceptions import CodedValidationError, ConflictError
from projects.lifecycle_service import assert_not_archived_mutable
from projects.models import (
    PROTECTED_PROJECT_FIELDS,
    Project,
    ProjectChangeRequest,
    ProjectChangeRequestStatus,
    ProjectStatus,
)

OPEN_STATUSES = (
    ProjectChangeRequestStatus.DRAFT,
    ProjectChangeRequestStatus.SUBMITTED,
)

CR_ALLOWED_PROJECT_STATUSES = (
    ProjectStatus.ACTIVE,
    ProjectStatus.SUSPENDED,
)


def _serialize_value(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _deserialize_value(key: str, value):
    if value is None or value == '':
        return None
    if key in ('start_date', 'planned_finish_date'):
        if hasattr(value, 'year'):
            return value
        return parse_date(str(value))
    if key == 'contract_amount':
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError) as exc:
            raise CodedValidationError(
                {'contract_amount': 'Invalid amount'},
                code='invalid_proposed_keys',
            ) from exc
    return value


def _validate_proposed(proposed: dict) -> dict:
    if not proposed or not isinstance(proposed, dict):
        raise CodedValidationError(
            {'proposed_changes': 'At least one protected field is required.'},
            code='invalid_proposed_keys',
        )
    cleaned = {}
    for key, value in proposed.items():
        if key not in PROTECTED_PROJECT_FIELDS:
            raise CodedValidationError(
                {'proposed_changes': f'Key not allowed: {key}'},
                code='invalid_proposed_keys',
            )
        cleaned[key] = _deserialize_value(key, value)
    return cleaned


def _assert_no_open(project: Project, exclude_id=None) -> None:
    qs = ProjectChangeRequest.objects.filter(
        project=project,
        status__in=OPEN_STATUSES,
        is_deleted=False,
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    if qs.exists():
        raise ConflictError(
            'An open project change request already exists.',
            code='change_request_already_open',
        )


def list_change_requests(project_id):
    return ProjectChangeRequest.objects.filter(project_id=project_id, is_deleted=False)


@transaction.atomic
def create_change_request(*, project: Project, user, reason: str, proposed_changes: dict) -> ProjectChangeRequest:
    assert_not_archived_mutable(project, user)
    if project.status not in CR_ALLOWED_PROJECT_STATUSES:
        raise CodedValidationError(
            {'detail': 'Change requests are only allowed for active or suspended projects.'},
            code='invalid_change_request_status',
        )
    reason = (reason or '').strip()
    if len(reason) < 10:
        raise CodedValidationError({'reason': 'Reason must be at least 10 characters.'}, code='reason_required')
    cleaned = _validate_proposed(proposed_changes)
    _assert_no_open(project)
    return ProjectChangeRequest.objects.create(
        project=project,
        reason=reason,
        proposed_changes={k: _serialize_value(v) for k, v in cleaned.items()},
        requested_by=user,
        created_by=user,
        updated_by=user,
        status=ProjectChangeRequestStatus.DRAFT,
    )


@transaction.atomic
def update_change_request(cr: ProjectChangeRequest, user, **fields) -> ProjectChangeRequest:
    assert_not_archived_mutable(cr.project, user)
    if cr.status != ProjectChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'detail': 'Only draft change requests can be edited.'},
            code='invalid_change_request_status',
        )
    if 'reason' in fields:
        reason = (fields['reason'] or '').strip()
        if len(reason) < 10:
            raise CodedValidationError({'reason': 'Reason must be at least 10 characters.'}, code='reason_required')
        cr.reason = reason
    if 'proposed_changes' in fields:
        cleaned = _validate_proposed(fields['proposed_changes'])
        cr.proposed_changes = {k: _serialize_value(v) for k, v in cleaned.items()}
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def submit_change_request(cr: ProjectChangeRequest, user) -> ProjectChangeRequest:
    assert_not_archived_mutable(cr.project, user)
    if cr.status != ProjectChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'detail': 'Only draft change requests can be submitted.'},
            code='invalid_change_request_status',
        )
    _assert_no_open(cr.project, exclude_id=cr.pk)
    previous = {}
    for key in cr.proposed_changes.keys():
        previous[key] = _serialize_value(getattr(cr.project, key, None))
    cr.previous_values = previous
    cr.status = ProjectChangeRequestStatus.SUBMITTED
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def approve_change_request(cr: ProjectChangeRequest, user, decision_notes: str = '') -> ProjectChangeRequest:
    assert_not_archived_mutable(cr.project, user)
    if cr.status != ProjectChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'detail': 'Only submitted change requests can be approved.'},
            code='invalid_change_request_status',
        )
    project = cr.project
    for key, raw in cr.proposed_changes.items():
        setattr(project, key, _deserialize_value(key, raw))
    project.save()
    cr.status = ProjectChangeRequestStatus.APPROVED
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def reject_change_request(cr: ProjectChangeRequest, user, decision_notes: str = '') -> ProjectChangeRequest:
    assert_not_archived_mutable(cr.project, user)
    if cr.status != ProjectChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'detail': 'Only submitted change requests can be rejected.'},
            code='invalid_change_request_status',
        )
    cr.status = ProjectChangeRequestStatus.REJECTED
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def cancel_change_request(cr: ProjectChangeRequest, user) -> ProjectChangeRequest:
    assert_not_archived_mutable(cr.project, user)
    if cr.status not in OPEN_STATUSES:
        raise CodedValidationError(
            {'detail': 'Only open change requests can be cancelled.'},
            code='invalid_change_request_status',
        )
    cr.status = ProjectChangeRequestStatus.CANCELLED
    cr.updated_by = user
    cr.save()
    return cr

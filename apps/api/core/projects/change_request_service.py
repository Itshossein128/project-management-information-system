"""Project change requests for protected identity fields."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date

from config.exceptions import CodedValidationError, ConflictError
from permissions.sod import assert_not_self_final_approve
from projects.lifecycle_service import assert_not_archived_mutable, lock_project, save_project, require_restore_admin
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



def _assert_restore_remediation(project, user, proposed, cycle=None):
    require_restore_admin(user)
    if project.status != ProjectStatus.ARCHIVED or project.archived_from_status != ProjectStatus.ACTIVE or (cycle and cycle != project.archive_cycle_id):
        raise ConflictError({'detail': _('The project changed. Review its current state and confirm again.')}, code='restore_context_changed')
    missing = set()
    if not (project.scope_description or '').strip(): missing.add('scope_description')
    if project.contract_amount is None: missing.add('contract_amount')
    if not proposed or not set(proposed) <= missing or ('scope_description' in proposed and not str(proposed['scope_description'] or '').strip()) or ('contract_amount' in proposed and proposed['contract_amount'] is None):
        raise CodedValidationError({'detail': _('Use a change request only to complete the missing scope or contract amount.')}, code='invalid_change_request_status')


def _assert_completion_remediation(project, user, proposed, event_id=None):
    from projects.status_undo_service import require_authority, source_context, conflict
    from django.core.exceptions import ValidationError
    user = require_authority(user, project.pk, 'undo_completion')
    if project.status != ProjectStatus.COMPLETED or project.completed_from_status != ProjectStatus.ACTIVE or (event_id and event_id != project.completion_event_id):
        conflict(project)
    source_context(project, 'undo_completion')
    missing = set()
    if not (project.scope_description or '').strip(): missing.add('scope_description')
    if project.contract_amount is None: missing.add('contract_amount')
    if not proposed or not set(proposed) <= missing or ('scope_description' in proposed and (not isinstance(proposed['scope_description'], str) or not proposed['scope_description'].strip())) or ('contract_amount' in proposed and proposed['contract_amount'] is None):
        raise CodedValidationError({'detail': _('Use a change request only to complete the missing scope or contract amount.')}, code='invalid_change_request_status')
    if 'contract_amount' in proposed:
        try: Project._meta.get_field('contract_amount').clean(proposed['contract_amount'], project)
        except ValidationError:
            raise CodedValidationError({'detail': _('Enter a valid contract amount.')}, code='invalid_proposed_keys')


def _check_bound_remediation(project, cr, user, proposed=None):
    if cr.restore_completion_event_id:
        _assert_completion_remediation(project, user, _validate_proposed(cr.proposed_changes) if proposed is None else proposed, cr.restore_completion_event_id)
    elif cr.restore_archive_cycle_id:
        _assert_restore_remediation(project, user, _validate_proposed(cr.proposed_changes) if proposed is None else proposed, cr.restore_archive_cycle_id)


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
            number = Decimal(str(value))
            if not number.is_finite(): raise InvalidOperation
            return number
        except (InvalidOperation, TypeError) as exc:
            raise CodedValidationError(
                {'contract_amount': _('Invalid amount')},
                code='invalid_proposed_keys',
            ) from exc
    return value


def _validate_proposed(proposed: dict) -> dict:
    if not proposed or not isinstance(proposed, dict):
        raise CodedValidationError(
            {'proposed_changes': _('At least one protected field is required.')},
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
            _('An open project change request already exists.'),
            code='change_request_already_open',
        )


def list_change_requests(project_id):
    return ProjectChangeRequest.objects.filter(project_id=project_id, is_deleted=False)


@transaction.atomic
def create_change_request(*, project: Project, user, reason: str, proposed_changes: dict) -> ProjectChangeRequest:
    project = lock_project(project)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    assert_not_archived_mutable(project, user)
    cleaned = _validate_proposed(proposed_changes)
    if project.status == ProjectStatus.ARCHIVED:
        _assert_restore_remediation(project, user, cleaned)
    elif project.status == ProjectStatus.COMPLETED:
        _assert_completion_remediation(project, user, cleaned)
    elif project.status not in CR_ALLOWED_PROJECT_STATUSES:
        raise CodedValidationError(
            {'detail': 'Change requests are only allowed for active or suspended projects.'},
            code='invalid_change_request_status',
        )
    reason = (reason or '').strip()
    if len(reason) < 10:
        raise CodedValidationError({'reason': _('Reason must be at least 10 characters.')}, code='reason_required')
    cleaned = _validate_proposed(proposed_changes)
    _assert_no_open(project)
    return ProjectChangeRequest.objects.create(
        project=project,
        restore_archive_cycle_id=project.archive_cycle_id if project.status == ProjectStatus.ARCHIVED else None,
        restore_completion_event_id=project.completion_event_id if project.status == ProjectStatus.COMPLETED else None,
        reason=reason,
        proposed_changes={k: _serialize_value(v) for k, v in cleaned.items()},
        requested_by=user,
        created_by=user,
        updated_by=user,
        status=ProjectChangeRequestStatus.DRAFT,
    )


@transaction.atomic
def update_change_request(cr: ProjectChangeRequest, user, **fields) -> ProjectChangeRequest:
    project = lock_project(cr.project_id)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    cr = ProjectChangeRequest.objects.select_for_update().get(pk=cr.pk, project=project, is_deleted=False)
    cr.project = project
    if cr.restore_completion_event_id:
        from projects.status_undo_service import require_authority
        user = require_authority(user, project.pk, 'undo_completion')
    assert_not_archived_mutable(project, user)
    if cr.status != ProjectChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'detail': _('Only draft change requests can be edited.')},
            code='invalid_change_request_status',
        )
    _check_bound_remediation(project, cr, user, _validate_proposed(fields.get('proposed_changes', cr.proposed_changes)))
    if 'reason' in fields:
        reason = (fields['reason'] or '').strip()
        if len(reason) < 10:
            raise CodedValidationError({'reason': _('Reason must be at least 10 characters.')}, code='reason_required')
        cr.reason = reason
    if 'proposed_changes' in fields:
        cleaned = _validate_proposed(fields['proposed_changes'])
        cr.proposed_changes = {k: _serialize_value(v) for k, v in cleaned.items()}
    cr.updated_by = user
    cr.save(update_fields=[*fields.keys(), 'updated_by', 'updated_at'])
    return cr


@transaction.atomic
def submit_change_request(cr: ProjectChangeRequest, user) -> ProjectChangeRequest:
    project = lock_project(cr.project_id)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    cr = ProjectChangeRequest.objects.select_for_update().get(pk=cr.pk, project=project, is_deleted=False)
    cr.project = project
    if cr.restore_completion_event_id:
        from projects.status_undo_service import require_authority
        user = require_authority(user, project.pk, 'undo_completion')
    assert_not_archived_mutable(project, user)
    if cr.status != ProjectChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'detail': _('Only draft change requests can be submitted.')},
            code='invalid_change_request_status',
        )
    _check_bound_remediation(project, cr, user)
    _assert_no_open(cr.project, exclude_id=cr.pk)
    previous = {}
    for key in cr.proposed_changes.keys():
        previous[key] = _serialize_value(getattr(cr.project, key, None))
    cr.previous_values = previous
    cr.status = ProjectChangeRequestStatus.SUBMITTED
    cr.updated_by = user
    cr.save(update_fields=['previous_values', 'status', 'updated_by', 'updated_at'])
    return cr


@transaction.atomic
def approve_change_request(cr: ProjectChangeRequest, user, decision_notes: str = '') -> ProjectChangeRequest:
    project = lock_project(cr.project_id)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    cr = ProjectChangeRequest.objects.select_for_update().get(pk=cr.pk, project=project, is_deleted=False)
    cr.project = project
    if cr.restore_completion_event_id:
        from projects.status_undo_service import require_authority
        user = require_authority(user, project.pk, 'undo_completion')
    assert_not_archived_mutable(project, user)
    try:
        assert_not_self_final_approve(cr.requested_by_id, user)
    except CodedValidationError:
        if project.status == ProjectStatus.ARCHIVED or cr.restore_completion_event_id:
            raise CodedValidationError({'detail': _('Another authorized person must approve this change request.')}, code='sod_self_approve')
        raise
    if cr.status != ProjectChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'detail': _('Only submitted change requests can be approved.')},
            code='invalid_change_request_status',
        )
    _check_bound_remediation(project, cr, user)
    project = cr.project
    for key, raw in cr.proposed_changes.items():
        setattr(project, key, _deserialize_value(key, raw))
    save_project(project, list(cr.proposed_changes))
    cr.status = ProjectChangeRequestStatus.APPROVED
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save(update_fields=['status', 'decided_by', 'decided_at', 'decision_notes', 'updated_by', 'updated_at'])
    return cr


@transaction.atomic
def reject_change_request(cr: ProjectChangeRequest, user, decision_notes: str = '') -> ProjectChangeRequest:
    project = lock_project(cr.project_id)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    cr = ProjectChangeRequest.objects.select_for_update().get(pk=cr.pk, project=project, is_deleted=False)
    cr.project = project
    assert_not_archived_mutable(project, user)
    if cr.status != ProjectChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'detail': _('Only submitted change requests can be rejected.')},
            code='invalid_change_request_status',
        )
    cr.status = ProjectChangeRequestStatus.REJECTED
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save(update_fields=['status', 'decided_by', 'decided_at', 'decision_notes', 'updated_by', 'updated_at'])
    return cr


@transaction.atomic
def cancel_change_request(cr: ProjectChangeRequest, user) -> ProjectChangeRequest:
    project = lock_project(cr.project_id)
    if project.status == ProjectStatus.ARCHIVED: user = require_restore_admin(user)
    cr = ProjectChangeRequest.objects.select_for_update().get(pk=cr.pk, project=project, is_deleted=False)
    cr.project = project
    if cr.restore_completion_event_id:
        from projects.status_undo_service import require_authority
        user = require_authority(user, project.pk, 'undo_completion')
    assert_not_archived_mutable(project, user)
    if cr.status not in OPEN_STATUSES:
        raise CodedValidationError(
            {'detail': _('Only open change requests can be cancelled.')},
            code='invalid_change_request_status',
        )
    cr.status = ProjectChangeRequestStatus.CANCELLED
    cr.updated_by = user
    cr.save(update_fields=['status', 'updated_by', 'updated_at'])
    return cr

"""Project lifecycle transitions (FR-PRJ)."""

from __future__ import annotations

from uuid import uuid4

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from config.exceptions import CodedValidationError
from permissions.project import _is_global_admin
from projects.models import Project, ProjectStatus



def lock_project(project):
    """Re-read only the root row; callers must own an atomic transaction."""
    return get_object_or_404(Project.objects.select_for_update(), pk=getattr(project, 'pk', project))


def save_project(project, fields):
    fields = list(fields)
    if set(fields) & {'status', 'project_name', 'project_manager', 'scope_description', 'contract_amount'}:
        project.lifecycle_version += 1
        fields.append('lifecycle_version')
    project.save(update_fields=list(dict.fromkeys([*fields, 'updated_at'])))


def activation_missing(project: Project) -> list[str]:
    missing: list[str] = []
    if not project.project_manager_id:
        missing.append('project_manager')
    if not (project.scope_description or '').strip():
        missing.append('scope_description')
    if project.contract_amount is None:
        missing.append('budget_approved')
    return missing


def assert_not_archived_mutable(project: Project, user) -> None:
    if project.status == ProjectStatus.ARCHIVED and not _is_global_admin(user):
        raise CodedValidationError(
            {'code': 'project_archived', 'detail': 'Archived projects are read-only.'},
            code='project_archived',
        )


def _transition(project: Project, *, allowed_from: set[str], to: str, code='invalid_status_transition'):
    if project.status not in allowed_from:
        raise CodedValidationError(
            {
                'code': code,
                'detail': f'Cannot transition from {project.status} to {to}.',
                'from': project.status,
                'to': to,
            },
            code=code,
        )


@transaction.atomic
def submit_for_approval(project: Project, user) -> Project:
    project = lock_project(project)
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.DRAFT}, to=ProjectStatus.PENDING_APPROVAL)
    project.status = ProjectStatus.PENDING_APPROVAL
    save_project(project, ['status'])
    return project


@transaction.atomic
def approve(project: Project, user) -> Project:
    project = lock_project(project)
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.PENDING_APPROVAL}, to=ProjectStatus.ACTIVE)
    missing = activation_missing(project)
    if missing:
        raise CodedValidationError(
            {
                'code': 'activation_gates_failed',
                'detail': 'Activation requirements not met.',
                'missing': missing,
            },
            code='activation_gates_failed',
        )
    if project.budget_approved_at is None:
        project.budget_approved_at = timezone.now()
        project.budget_approved_by = user
    project.status = ProjectStatus.ACTIVE
    save_project(project, ['status', 'budget_approved_at', 'budget_approved_by'])
    return project


@transaction.atomic
def reject(project: Project, user, reason: str = '') -> Project:
    project = lock_project(project)
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.PENDING_APPROVAL}, to=ProjectStatus.DRAFT)
    project.status = ProjectStatus.DRAFT
    save_project(project, ['status'])
    return project


def _original_event(project, user, to_status):
    from audit.service import persist_audit_log
    before = project.lifecycle_version
    event = 'project.suspended' if to_status == ProjectStatus.SUSPENDED else 'project.completed'
    return persist_audit_log({
        'actor_id': str(user.pk), 'project_id': str(project.pk), 'http_method': 'POST',
        'path': f'/api/v1/projects/{project.pk}/{"suspend" if to_status == ProjectStatus.SUSPENDED else "complete"}/',
        'resource_type': 'project', 'resource_id': str(project.pk),
        'changes': {
            'schema_version': 1, 'event': event, 'from_status': project.status, 'to_status': to_status,
            'version_before': before, 'version_after': before + 1,
            'actor': {'id': str(user.pk), 'display_name': user.full_name or user.username},
            'project': {'id': str(project.pk), 'project_code': project.project_code, 'project_name': project.project_name},
            'suspension_event_id': str(project.suspension_event_id) if project.status == ProjectStatus.SUSPENDED and to_status == ProjectStatus.COMPLETED else None,
        },
    })


@transaction.atomic
def suspend(project: Project, user) -> Project:
    project = lock_project(project)
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.ACTIVE}, to=ProjectStatus.SUSPENDED)
    project.suspension_event = _original_event(project, user, ProjectStatus.SUSPENDED)
    project.status = ProjectStatus.SUSPENDED
    save_project(project, ['status', 'suspension_event'])
    return project


def resume(project: Project, user, *, request_id, confirmation_token, reason):
    from projects.status_undo_service import undo
    return undo(project, user, 'resume', request_id=request_id, confirmation_token=confirmation_token, reason=reason)


@transaction.atomic
def complete(project: Project, user) -> Project:
    project = lock_project(project)
    assert_not_archived_mutable(project, user)
    _transition(
        project,
        allowed_from={ProjectStatus.ACTIVE, ProjectStatus.SUSPENDED},
        to=ProjectStatus.COMPLETED,
    )
    project.completion_event = _original_event(project, user, ProjectStatus.COMPLETED)
    project.completed_from_status = project.status
    project.status = ProjectStatus.COMPLETED
    save_project(project, ['status', 'completion_event', 'completed_from_status'])
    return project


@transaction.atomic
def archive(project: Project, user) -> Project:
    project = lock_project(project)
    _transition(
        project,
        allowed_from={
            ProjectStatus.COMPLETED,
            ProjectStatus.ACTIVE,
            ProjectStatus.SUSPENDED,
        },
        to=ProjectStatus.ARCHIVED,
    )
    project.archived_from_status = project.status
    project.archive_cycle_id = uuid4()
    project.status = ProjectStatus.ARCHIVED
    save_project(project, ['status', 'archived_from_status', 'archive_cycle_id'])
    return project


# Restoration uses its own narrow receipt; it never invokes approval or finance.
def require_restore_admin(user):
    from django.contrib.auth import get_user_model
    from django.utils.translation import gettext as _
    from rest_framework.exceptions import PermissionDenied
    fresh = get_user_model().objects.filter(pk=getattr(user, 'pk', None), is_active=True).first()
    if fresh is None or not _is_global_admin(fresh):
        raise PermissionDenied(_('Only a system administrator can restore an archived project.'))
    return fresh


def current_project_data(project):
    return {
        'project_id': str(project.pk), 'project_name': project.project_name,
        'status': project.status,
        'archive_cycle_id': str(project.archive_cycle_id) if project.archive_cycle_id else None,
        'lifecycle_version': project.lifecycle_version,
    }


def restore_receipt_data(receipt):
    return {
        'id': str(receipt.pk), 'project_id': str(receipt.project_id),
        'project_name': receipt.project_snapshot['project_name'],
        'archive_cycle_id': str(receipt.archive_cycle_id), 'request_id': str(receipt.request_id),
        'actor': receipt.actor_snapshot, 'restored_at': receipt.restored_at.isoformat(),
        'reason': receipt.reason, 'from_status': receipt.from_status, 'to_status': receipt.to_status,
    }


def _digest(value):
    import hashlib
    import json
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def _restore_context(project, user):
    snapshot = {
        **current_project_data(project), 'origin': project.archived_from_status,
        'manager': str(project.project_manager_id) if project.project_manager_id else None,
        'scope': (project.scope_description or '').strip(),
        'amount': str(project.contract_amount.normalize()) if project.contract_amount is not None else None,
    }
    return {
        'project_id': str(project.pk), 'actor_id': str(user.pk),
        'archive_cycle_id': str(project.archive_cycle_id),
        'to_status': project.archived_from_status,
        'lifecycle_version': project.lifecycle_version, 'snapshot_hash': _digest(snapshot),
    }


def _remediation(missing):
    return [{'field': f, 'action': 'project_settings' if f == 'project_manager' else 'project_change_request'} for f in missing]


def _restore_conflict(project, code='restore_context_changed', receipt=None):
    from config.exceptions import ConflictError
    from django.utils.translation import gettext as _
    details = {'detail': _('The project changed. Review its current state and confirm again.'), 'current_project': current_project_data(project)}
    if receipt is not None:
        details['receipt'] = restore_receipt_data(receipt)
    raise ConflictError(details, code=code)


def restore_preview(project, user):
    from django.core import signing
    user = require_restore_admin(user)
    project = get_object_or_404(Project, pk=getattr(project, 'pk', project))
    if project.status != ProjectStatus.ARCHIVED:
        _restore_conflict(project)
    missing = activation_missing(project) if project.archived_from_status == ProjectStatus.ACTIVE else []
    return {
        **current_project_data(project), 'from_status': 'archived', 'to_status': project.archived_from_status,
        'confirmation_token': signing.dumps(_restore_context(project, user), salt='projects.archive.restore.v1'),
        'can_confirm': not missing, 'missing': missing, 'remediation': _remediation(missing),
    }


@transaction.atomic
def restore(project, user, *, request_id, confirmation_token, reason):
    from uuid import UUID
    from django.core import signing
    from django.utils.translation import gettext as _
    from rest_framework.exceptions import PermissionDenied
    from projects.models import ProjectArchiveRestore
    from audit import service as audit_service
    # Recheck authority and re-read the actual row even for direct service callers.
    user = require_restore_admin(user)
    project = lock_project(project)
    user = require_restore_admin(user)
    if not isinstance(reason, str) or not reason.strip():
        raise CodedValidationError({'detail': _('Enter a reason for restoration.'), 'fields': {'reason': _('A reason is required.')}}, code='reason_required')
    reason = reason.strip()
    try:
        request_id = UUID(str(request_id))
        context = signing.loads(confirmation_token, salt='projects.archive.restore.v1')
        if not isinstance(context, dict) or set(context) != {'project_id','actor_id','archive_cycle_id','to_status','lifecycle_version','snapshot_hash'}:
            raise ValueError('Invalid confirmation shape')
        cycle = UUID(context['archive_cycle_id'])
    except (signing.BadSignature, ValueError, TypeError, KeyError):
        raise CodedValidationError({'detail': _('Invalid restoration confirmation. Open a new preview.')}, code='invalid_restore_request')
    if context['project_id'] != str(project.pk) or context['actor_id'] != str(user.pk):
        raise PermissionDenied(_('This restoration confirmation belongs to another user or project.'))
    fingerprint = _digest({'context': context, 'reason': reason})
    previous = ProjectArchiveRestore.objects.filter(project=project, request_id=request_id).first()
    if previous:
        if previous.request_fingerprint != fingerprint:
            _restore_conflict(project, 'restore_request_conflict')
        return {'outcome': 'replayed', 'receipt': restore_receipt_data(previous), 'current_project': current_project_data(project)}
    previous = ProjectArchiveRestore.objects.filter(project=project, archive_cycle_id=cycle).first()
    if previous:
        _restore_conflict(project, 'archive_already_restored', previous)
    if project.status != ProjectStatus.ARCHIVED or context != _restore_context(project, user):
        _restore_conflict(project)
    missing = activation_missing(project) if project.archived_from_status == ProjectStatus.ACTIVE else []
    if missing:
        raise CodedValidationError({'detail': _('Complete the missing activation information before restoration.'), 'missing': missing, 'remediation': _remediation(missing)}, code='activation_gates_failed')
    target = project.archived_from_status
    receipt_id = uuid4()
    actor_snapshot = {'id': str(user.pk), 'display_name': user.full_name or user.username}
    project_snapshot = {'id': str(project.pk), 'project_code': project.project_code, 'project_name': project.project_name}
    project.status = target
    save_project(project, ['status'])
    audit = audit_service.persist_audit_log(audit_service.build_audit_payload(
        actor_id=user.pk, project_id=project.pk, http_method='POST',
        path=f'/api/v1/projects/{project.pk}/restore/', resource_type='project', resource_id=project.pk,
        changes={'event': 'project.restored_from_archive', 'receipt_id': str(receipt_id), 'archive_cycle_id': str(cycle), 'request_id': str(request_id), 'actor': actor_snapshot, 'project': project_snapshot, 'reason': reason, 'from_status': 'archived', 'to_status': target},
        ip_address=None,
    ))
    receipt = ProjectArchiveRestore.objects.create(
        id=receipt_id, project=project, archive_cycle_id=cycle, request_id=request_id,
        request_fingerprint=fingerprint, confirmation_version=context['lifecycle_version'],
        actor=user, actor_snapshot=actor_snapshot, project_snapshot=project_snapshot, reason=reason,
        from_status='archived', to_status=target, restored_at=audit.created_at, audit_log=audit,
    )
    return {'outcome': 'restored', 'receipt': restore_receipt_data(receipt), 'current_project': current_project_data(project)}

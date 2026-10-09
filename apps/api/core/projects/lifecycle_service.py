"""Project lifecycle transitions (FR-PRJ)."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from config.exceptions import CodedValidationError
from permissions.project import _is_global_admin
from projects.models import Project, ProjectStatus


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
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.DRAFT}, to=ProjectStatus.PENDING_APPROVAL)
    project.status = ProjectStatus.PENDING_APPROVAL
    project.save(update_fields=['status', 'updated_at'])
    return project


@transaction.atomic
def approve(project: Project, user) -> Project:
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
    project.save(
        update_fields=['status', 'budget_approved_at', 'budget_approved_by', 'updated_at'],
    )
    return project


@transaction.atomic
def reject(project: Project, user, reason: str = '') -> Project:
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.PENDING_APPROVAL}, to=ProjectStatus.DRAFT)
    project.status = ProjectStatus.DRAFT
    project.save(update_fields=['status', 'updated_at'])
    return project


@transaction.atomic
def suspend(project: Project, user) -> Project:
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.ACTIVE}, to=ProjectStatus.SUSPENDED)
    project.status = ProjectStatus.SUSPENDED
    project.save(update_fields=['status', 'updated_at'])
    return project


@transaction.atomic
def resume(project: Project, user) -> Project:
    assert_not_archived_mutable(project, user)
    _transition(project, allowed_from={ProjectStatus.SUSPENDED}, to=ProjectStatus.ACTIVE)
    missing = activation_missing(project)
    if missing:
        raise CodedValidationError(
            {
                'code': 'activation_gates_failed',
                'detail': 'Cannot resume until activation gates are met.',
                'missing': missing,
            },
            code='activation_gates_failed',
        )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


@transaction.atomic
def complete(project: Project, user) -> Project:
    assert_not_archived_mutable(project, user)
    _transition(
        project,
        allowed_from={ProjectStatus.ACTIVE, ProjectStatus.SUSPENDED},
        to=ProjectStatus.COMPLETED,
    )
    project.status = ProjectStatus.COMPLETED
    project.save(update_fields=['status', 'updated_at'])
    return project


@transaction.atomic
def archive(project: Project, user) -> Project:
    _transition(
        project,
        allowed_from={
            ProjectStatus.COMPLETED,
            ProjectStatus.ACTIVE,
            ProjectStatus.SUSPENDED,
        },
        to=ProjectStatus.ARCHIVED,
    )
    project.status = ProjectStatus.ARCHIVED
    project.save(update_fields=['status', 'updated_at'])
    return project

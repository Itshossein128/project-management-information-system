"""Fixtures helpers for contractor-stakeholder-select tests."""

from __future__ import annotations

from django.utils import timezone

from projects.models import ProjectStatus, Stakeholder, StakeholderStatus
from projects.services import create_project_with_creator


def make_stakeholder(
    project,
    *,
    name: str,
    user,
    role: str = '',
    status: str = StakeholderStatus.ACTIVE,
    organization_name: str = '',
) -> Stakeholder:
    return Stakeholder.objects.create(
        project=project,
        name=name,
        organization_name=organization_name,
        role=role,
        status=status,
        created_by=user,
        updated_by=user,
    )


def make_active_contractor(project, user, name: str = 'Contractor Alpha') -> Stakeholder:
    return make_stakeholder(
        project, user=user, name=name, role='contractor', status=StakeholderStatus.ACTIVE
    )


def make_inactive_contractor(project, user, name: str = 'Contractor Inactive') -> Stakeholder:
    return make_stakeholder(
        project,
        user=user,
        name=name,
        role='contractor',
        status=StakeholderStatus.INACTIVE,
    )


def make_non_contractor(
    project, user, name: str = 'Owner Party', role: str = 'Owner'
) -> Stakeholder:
    return make_stakeholder(project, user=user, name=name, role=role, status=StakeholderStatus.ACTIVE)


def make_second_project(user, *, code: str = 'PRJ-002', name: str = 'Other Project'):
    project = create_project_with_creator(
        creator=user,
        project_code=code,
        project_name=name,
        employer='Other Co',
        start_date='2024-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.scope_description = 'Other scope'
    if project.contract_amount is None:
        project.contract_amount = 1
    project.budget_approved_at = timezone.now()
    project.save(
        update_fields=[
            'status',
            'scope_description',
            'contract_amount',
            'budget_approved_at',
            'updated_at',
        ],
    )
    return project

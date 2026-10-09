"""Project readiness gates for definitive baselines and binding commitments."""

from __future__ import annotations

from config.exceptions import CodedValidationError
from projects.models import Project, ProjectStatus


def assert_project_allows_definitive_baseline(project: Project) -> None:
    if project.status != ProjectStatus.ACTIVE:
        raise CodedValidationError(
            {
                'code': 'project_not_active_for_baseline',
                'detail': 'Definitive locked baseline requires an active project.',
                'status': project.status,
            },
            code='project_not_active_for_baseline',
        )


def assert_project_allows_binding_commitment(project: Project) -> None:
    if project.status != ProjectStatus.ACTIVE:
        raise CodedValidationError(
            {
                'code': 'project_not_active_for_commitment',
                'detail': 'Binding financial commitment requires an active project.',
                'status': project.status,
            },
            code='project_not_active_for_commitment',
        )

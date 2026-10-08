"""Project kickoff charter get/upsert."""

from __future__ import annotations

from django.db import transaction

from projects.lifecycle_service import assert_not_archived_mutable
from projects.models import Project, ProjectKickoffCharter

CHARTER_FIELDS = (
    'justification',
    'success_criteria',
    'constraints',
    'assumptions',
    'key_stakeholders_summary',
    'pm_authority',
)


def get_charter(project: Project) -> ProjectKickoffCharter | None:
    try:
        return project.kickoff_charter
    except ProjectKickoffCharter.DoesNotExist:
        return None


@transaction.atomic
def upsert_charter(project: Project, user, *, partial: bool = False, **fields) -> ProjectKickoffCharter:
    assert_not_archived_mutable(project, user)
    charter = get_charter(project)
    if charter is None:
        charter = ProjectKickoffCharter(
            project=project,
            created_by=user,
            updated_by=user,
            **{k: (fields.get(k) or '') for k in CHARTER_FIELDS},
        )
        charter.save()
        return charter

    for key in CHARTER_FIELDS:
        if not partial or key in fields:
            setattr(charter, key, fields.get(key, getattr(charter, key)) or '')
    charter.updated_by = user
    charter.save()
    return charter

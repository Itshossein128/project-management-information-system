"""Membership-filtered project visibility for cash-flow portfolio APIs."""

from __future__ import annotations

from master_data.models import MemberStatus, ProjectMember
from permissions.project import _is_global_admin, member_has_codename
from projects.models import Project


def projects_visible_for_cashflow(user):
    """Return Project queryset the user may view for cash-flow portfolio APIs."""
    base = Project.objects.all()
    if _is_global_admin(user):
        return base
    if not user or not user.is_authenticated:
        return base.none()

    member_ids = list(
        ProjectMember.objects.filter(
            user_id=user.id,
            status=MemberStatus.ACTIVE,
        ).values_list('project_id', flat=True)
    )
    allowed = [
        pid
        for pid in member_ids
        if member_has_codename(user, pid, 'view_cashflow')
    ]
    return base.filter(pk__in=allowed)

"""Contractor classification helpers for stakeholder-backed پیمانکار selection."""

from __future__ import annotations

from uuid import UUID

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from projects.models import Stakeholder, StakeholderStatus

CONTRACTOR_ROLE = 'contractor'
CONTRACTOR_ROLE_ALIASES = {
    'contractor',
    'پیمانکار',
    'Contractor',
}


def normalize_stakeholder_role(role: str | None) -> str:
    """Normalize write aliases to canonical contractor code; leave other roles as trimmed text."""
    text = (role or '').strip()
    if not text:
        return ''
    if text in CONTRACTOR_ROLE_ALIASES or text.casefold() == CONTRACTOR_ROLE:
        return CONTRACTOR_ROLE
    return text


def contractor_queryset(project_id, *, active_only: bool = True):
    qs = Stakeholder.objects.filter(
        project_id=project_id,
        is_deleted=False,
        role=CONTRACTOR_ROLE,
    )
    if active_only:
        qs = qs.filter(status=StakeholderStatus.ACTIVE)
    return qs


def resolve_active_contractor(*, project_id, contractor_id=None, name: str | None = None) -> Stakeholder:
    """
    Resolve a contractor for writes/imports.

    Predicate: project_id match AND is_deleted=false AND status=active AND role=contractor.
    """
    qs = contractor_queryset(project_id, active_only=True)
    if contractor_id:
        try:
            return qs.get(pk=contractor_id)
        except (Stakeholder.DoesNotExist, ValueError, TypeError) as exc:
            raise ValidationError({'contractor_ref': _('Select a valid active contractor.')}) from exc

    if name is not None:
        trimmed = str(name).strip()
        if not trimmed:
            raise ValidationError({'contractor': _('This field is required.')})
        matches = list(qs.filter(name__iexact=trimmed)[:2])
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 0:
            # Exact trimmed case-sensitive fallback after iexact miss on weird collation
            matches = list(qs.filter(name=trimmed)[:2])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValidationError(
                {'contractor': _('Multiple contractors match this name; use the contractor id.')}
            )
        raise ValidationError(
            {
                'contractor': _(
                    'Unknown contractor. Register the contractor on stakeholders (ذینفعان) first.'
                )
            }
        )

    raise ValidationError({'contractor_ref': _('This field is required.')})


def parse_contractor_id(value) -> UUID | None:
    if value is None or value == '':
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None

"""Segregation of duties helpers (FR-RPT / A6-P4).

Break-glass: only an explicit superuser request with a non-empty reason may
bypass the self-approve rule. Membership, approve permission, and record status
remain the caller's responsibility. Null creator does not skip the check.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError


@dataclass(frozen=True)
class SodDecision:
    """Result of a SoD check before final approve."""

    allowed: bool
    used_break_glass: bool = False
    reason: str = ''


def assert_not_self_final_approve(
    created_by_id,
    actor,
    *,
    break_glass_reason: str | None = None,
    project=None,
    record_id=None,
    record_type: str | None = None,
) -> SodDecision:
    """Enforce submitter ≠ final approver unless explicit audited break-glass.

    Returns ``SodDecision``. Callers that receive ``used_break_glass=True`` MUST
    persist an access-history row before completing approval. If audit cannot be
    written, the approve MUST NOT proceed.

    Raises ``CodedValidationError`` with ``sod_self_approve`` when blocked.
    """
    from permissions.role_services import record_access_change

    if actor is None:
        raise CodedValidationError(
            detail=_('An actor is required for final approval.'),
            code='sod_actor_required',
        )

    actor_id = getattr(actor, 'id', None)
    if actor_id is None:
        raise CodedValidationError(
            detail=_('An actor is required for final approval.'),
            code='sod_actor_required',
        )

    if created_by_id is None:
        reason = (break_glass_reason or '').strip()
        unknown_creator = reason in ('unknown_creator', 'ثبت‌کننده نامعلوم')
        if getattr(actor, 'is_superuser', False) and unknown_creator:
            return SodDecision(allowed=True, used_break_glass=True, reason=reason)
        exc = CodedValidationError(
            detail=_('A record without a recorded creator cannot take the normal final-approve path.'),
            code='sod_missing_creator',
        )
        if project is not None:
            record_access_change(
                actor=actor,
                project=project,
                subject_user=None,
                role=None,
                action='sod_refusal',
                before={'code': exc.default_code, 'record_id': str(record_id) if record_id else None},
                after={'record_type': record_type or '', 'exception': False},
            )
        raise exc

    if str(created_by_id) != str(actor_id):
        return SodDecision(allowed=True, used_break_glass=False, reason='')

    reason = (break_glass_reason or '').strip()
    if getattr(actor, 'is_superuser', False) and reason:
        return SodDecision(allowed=True, used_break_glass=True, reason=reason)

    exc = CodedValidationError(
        detail=_('The creator cannot alone complete final approval of this transaction.'),
        code='sod_self_approve',
    )
    if project is not None:
        from django.contrib.auth import get_user_model

        try:
            subject = get_user_model().objects.get(pk=created_by_id)
        except get_user_model().DoesNotExist:
            subject = None
        record_access_change(
            actor=actor,
            project=project,
            subject_user=subject,
            role=None,
            action='sod_refusal',
            before={'code': exc.default_code, 'record_id': str(record_id) if record_id else None},
            after={'record_type': record_type or '', 'exception': False},
        )
    raise exc


def repair_missing_creator(*, record, field_name: str, creator, actor, project, record_type: str):
    """Assign a real creator to a legacy null-creator row and audit the repair.

    Does not approve the record. Never assigns the approver as a silent bypass:
    callers choose ``creator`` from evidence. System jobs must pass an explicit
    system user identity, not a forged human.
    """
    from permissions.role_services import record_access_change

    if creator is None or getattr(creator, 'id', None) is None:
        raise CodedValidationError(
            detail=_('A valid creator is required to repair attribution.'),
            code='sod_creator_repair_invalid',
        )
    actor_id = getattr(actor, 'id', None)
    if actor_id is not None and str(actor_id) == str(creator.id):
        raise CodedValidationError(
            detail=_('The repairing actor cannot assign themselves as creator.'),
            code='sod_creator_repair_invalid',
        )
    previous = getattr(record, field_name, None)
    if previous is not None:
        raise CodedValidationError(
            detail=_('This record already has a creator.'),
            code='sod_creator_already_set',
        )
    setattr(record, field_name, creator)
    update_fields = [field_name]
    if hasattr(record, 'updated_at'):
        update_fields.append('updated_at')
    record.save(update_fields=update_fields)
    record_access_change(
        actor=actor,
        project=project,
        subject_user=creator,
        role=None,
        action='sod_creator_repaired',
        before={'created_by': None, 'record_type': record_type},
        after={
            'created_by': str(creator.id),
            'record_type': record_type,
            'record_id': str(getattr(record, 'id', '')),
        },
    )
    return record

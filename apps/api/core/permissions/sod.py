"""Segregation of duties helpers (FR-RPT).

Break-glass: only ``user.is_superuser`` may bypass self-approve checks in v1.
"""

from __future__ import annotations

from config.exceptions import CodedValidationError


def assert_not_self_final_approve(created_by_id, actor) -> None:
    """Raise ``sod_self_approve`` when the actor is the creator of a material transaction.

    No-op when ``created_by_id`` is null or actor is a Django superuser.
    """
    if created_by_id is None or actor is None:
        return
    if getattr(actor, 'is_superuser', False):
        return
    actor_id = getattr(actor, 'id', None)
    if actor_id is None:
        return
    if str(created_by_id) == str(actor_id):
        raise CodedValidationError(
            detail='The creator cannot alone complete final approval of this transaction.',
            code='sod_self_approve',
        )

"""Schedule + budget baseline validity for EVM reports."""

from __future__ import annotations

from typing import Any

from cost_control.models import BudgetVersion, BudgetVersionStatus
from schedule.models import BaselineSchedule


def resolve_evm_baseline_validity(project_id) -> dict[str, Any]:
    """Return validity, warnings, and baseline snapshots for a project.

    Fully valid only when schedule baseline is locked and a control/approved
    budget version exists.
    """
    warnings: list[str] = []

    schedule_bl = (
        BaselineSchedule.objects.filter(
            project_id=project_id,
            is_deleted=False,
            is_locked=True,
        )
        .order_by('-locked_at', '-created_at')
        .first()
    )
    schedule_locked = schedule_bl is not None
    schedule_baseline = {
        'locked': schedule_locked,
        'baseline_id': str(schedule_bl.id) if schedule_bl else None,
        'locked_at': schedule_bl.locked_at.isoformat() if schedule_bl and schedule_bl.locked_at else None,
    }
    if not schedule_locked:
        warnings.append('baseline_not_locked')

    control = (
        BudgetVersion.objects.filter(
            project_id=project_id,
            is_deleted=False,
            is_control=True,
            status=BudgetVersionStatus.APPROVED,
        )
        .order_by('-version_number')
        .first()
    )
    if control is None:
        control = (
            BudgetVersion.objects.filter(
                project_id=project_id,
                is_deleted=False,
                status=BudgetVersionStatus.APPROVED,
            )
            .order_by('-version_number')
            .first()
        )

    budget_approved = control is not None
    budget_is_control = bool(control and control.is_control)
    budget_baseline = {
        'approved': budget_approved,
        'is_control': budget_is_control,
        'version_id': str(control.id) if control else None,
        'currency': control.currency if control else None,
    }
    if not budget_approved:
        warnings.append('budget_baseline_not_approved')
    elif not budget_is_control:
        warnings.append('budget_baseline_not_control')

    if schedule_locked and budget_approved:
        validity = 'valid'
    elif schedule_locked or budget_approved:
        validity = 'partial'
    else:
        validity = 'partial' if warnings else 'invalid'
        if not warnings:
            validity = 'invalid'

    # Unlocked schedule or missing budget → never fully valid (FR-001)
    if 'baseline_not_locked' in warnings or 'budget_baseline_not_approved' in warnings:
        if validity == 'valid':
            validity = 'partial'

    return {
        'validity': validity,
        'warnings': warnings,
        'schedule_baseline': schedule_baseline,
        'budget_baseline': budget_baseline,
        'budget_version': control,
    }

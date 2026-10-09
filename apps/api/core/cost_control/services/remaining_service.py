"""Remaining allocatable and intra-budget transfers."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from config.exceptions import CodedValidationError
from cost_control.models import (
    ActualCost,
    Budget,
    BudgetTransfer,
    BudgetVersionStatus,
    Commitment,
    CommitmentStatus,
)
from cost_control.services.budget_version_service import get_control_version, project_ceiling


def _actuals_counting_toward_consumed(project_id):
    """Only approved actuals consume remaining (draft/void excluded)."""
    from cost_control.models import ActualCostStatus

    return ActualCost.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=ActualCostStatus.APPROVED,
    )


def _heading_key(line: Budget) -> str:
    if line.cbs_id:
        return f'cbs:{line.cbs_id}|{line.cost_category}'
    if line.wbs_id:
        return f'wbs:{line.wbs_id}|{line.cost_category}'
    if line.contract_id:
        return f'contract:{line.contract_id}|{line.cost_category}'
    return f'project|{line.cost_category}'


def remaining_allocatable(project_id, version_id=None) -> dict:
    if version_id:
        from cost_control.models import BudgetVersion

        version = BudgetVersion.objects.get(pk=version_id, project_id=project_id, is_deleted=False)
    else:
        version = get_control_version(project_id)
        if not version:
            return {
                'version_id': None,
                'project_ceiling': 0.0,
                'headings': [],
            }

    lines = list(Budget.objects.filter(version=version, is_deleted=False))
    ceiling = float(project_ceiling(project_id)) if version.is_control else float(
        sum((l.budget_amount for l in lines), Decimal('0'))
    )

    # Aggregate approved/consumed/committed by heading
    approved: dict[str, Decimal] = {}
    meta: dict[str, dict] = {}
    for line in lines:
        key = _heading_key(line)
        approved[key] = approved.get(key, Decimal('0')) + Decimal(line.budget_amount)
        meta[key] = {
            'level': line.level,
            'wbs': str(line.wbs_id) if line.wbs_id else None,
            'cbs': str(line.cbs_id) if line.cbs_id else None,
            'contract': str(line.contract_id) if line.contract_id else None,
            'cost_category': line.cost_category,
            'cbs_missing_warning': bool(line.wbs_id and not line.cbs_id),
        }

    committed_qs = Commitment.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=CommitmentStatus.APPROVED,
    )
    consumed_qs = _actuals_counting_toward_consumed(project_id)

    def _heading_actuals(info: dict):
        qs = consumed_qs
        if info['cbs']:
            qs = qs.filter(cbs_id=info['cbs'])
        elif info['wbs']:
            qs = qs.filter(wbs_id=info['wbs'])
        else:
            return ActualCost.objects.none()
        if info['cost_category']:
            cat_qs = qs.filter(cost_category=info['cost_category'])
            if cat_qs.exists():
                return cat_qs
        return qs

    def _heading_commitments(info: dict):
        qs = committed_qs
        if info['cbs']:
            return qs.filter(cbs_id=info['cbs'])
        if info['wbs']:
            return qs.filter(wbs_id=info['wbs'])
        return Commitment.objects.none()

    def _open_committed(commitments, actuals_for_heading) -> Decimal:
        """Open commitment = max(0, amount − linked approved actuals on heading)."""
        total = Decimal('0')
        linked_by_commitment: dict = {}
        for row in actuals_for_heading.filter(commitment_id__isnull=False).values(
            'commitment_id'
        ).annotate(t=Sum('amount')):
            linked_by_commitment[row['commitment_id']] = Decimal(row['t'] or 0)
        for c in commitments:
            linked = linked_by_commitment.get(c.id, Decimal('0'))
            total += max(Decimal('0'), Decimal(c.amount) - linked)
        return total

    headings = []
    for key, approved_amt in approved.items():
        info = meta[key]
        heading_actuals = _heading_actuals(info)
        heading_commitments = list(_heading_commitments(info))
        if not info['cbs'] and not info['wbs']:
            committed = Decimal('0')
            consumed = Decimal('0')
        else:
            consumed = heading_actuals.aggregate(t=Sum('amount'))['t'] or Decimal('0')
            committed = _open_committed(heading_commitments, heading_actuals)

        raw_remaining = Decimal(approved_amt) - Decimal(committed) - Decimal(consumed)
        overrun = raw_remaining < 0
        headings.append(
            {
                'key': key,
                'level': info['level'],
                'wbs': info['wbs'],
                'cbs': info['cbs'],
                'contract': info['contract'],
                'cost_category': info['cost_category'],
                'approved': float(approved_amt),
                'committed': float(committed),
                'consumed': float(consumed),
                'remaining': float(max(raw_remaining, Decimal('0'))),
                'overrun': overrun,
                'cbs_missing_warning': info['cbs_missing_warning'],
            }
        )

    return {
        'version_id': str(version.id),
        'project_ceiling': ceiling,
        'headings': headings,
    }


@transaction.atomic
def transfer_budget(
    *,
    project_id,
    user,
    from_line_id,
    to_line_id,
    amount,
    note: str = '',
) -> BudgetTransfer:
    amount = Decimal(str(amount))
    if amount <= 0:
        raise CodedValidationError(
            {'amount': 'Transfer amount must be positive.'},
            code='transfer_invalid_amount',
        )

    from_line = Budget.objects.select_related('version').get(
        pk=from_line_id, project_id=project_id, is_deleted=False
    )
    to_line = Budget.objects.select_related('version').get(
        pk=to_line_id, project_id=project_id, is_deleted=False
    )

    if from_line.version_id != to_line.version_id:
        raise CodedValidationError(
            {'version': 'Both lines must belong to the same budget version.'},
            code='transfer_version_mismatch',
        )

    version = from_line.version
    if (
        not version
        or version.status != BudgetVersionStatus.APPROVED
        or not version.is_control
    ):
        raise CodedValidationError(
            {'version': 'Transfers are only allowed on the approved control version.'},
            code='budget_version_locked',
        )

    if Decimal(from_line.budget_amount) < amount:
        raise CodedValidationError(
            {'amount': 'Insufficient amount on source line.'},
            code='transfer_insufficient_source',
        )

    # Snapshot ceiling and version total before mutation (net-zero must preserve total).
    ceiling_before = project_ceiling(project_id)
    total_before = (
        Budget.objects.filter(version=version, is_deleted=False).aggregate(t=Sum('budget_amount'))[
            't'
        ]
        or Decimal('0')
    )

    from_line.budget_amount = Decimal(from_line.budget_amount) - amount
    to_line.budget_amount = Decimal(to_line.budget_amount) + amount
    from_line.updated_by = user
    to_line.updated_by = user
    from_line.save(update_fields=['budget_amount', 'updated_by', 'updated_at'])
    to_line.save(update_fields=['budget_amount', 'updated_by', 'updated_at'])

    total_after = (
        Budget.objects.filter(version=version, is_deleted=False).aggregate(t=Sum('budget_amount'))[
            't'
        ]
        or Decimal('0')
    )
    if Decimal(total_after) != Decimal(total_before):
        raise CodedValidationError(
            {'amount': 'Transfer must be net-zero on the control version total.'},
            code='project_ceiling_exceeded',
        )
    if ceiling_before > 0 and Decimal(total_after) > ceiling_before + Decimal('0.01'):
        raise CodedValidationError(
            {'ceiling': 'Transfer would exceed project budget ceiling.'},
            code='project_ceiling_exceeded',
        )

    return BudgetTransfer.objects.create(
        project_id=project_id,
        version=version,
        from_line=from_line,
        to_line=to_line,
        amount=amount,
        note=note or '',
        created_by=user,
        updated_by=user,
    )

"""CBS tree + commitment/payment services."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from cost_control.models import (
    ActualCost,
    Budget,
    Commitment,
    CommitmentStatus,
    CostBreakdownNode,
    Payment,
    PaymentStatus,
)


class CBSConflictError(Exception):
    pass


@transaction.atomic
def create_cbs_node(*, project_id, parent_id=None, cbs_code, cbs_name, cost_type='', description='', created_by=None):
    cbs_code = cbs_code.strip()
    if CostBreakdownNode.objects.filter(project_id=project_id, cbs_code=cbs_code, is_deleted=False).exists():
        raise ValidationError({'cbs_code': 'Must be unique within the project.'})
    kwargs = dict(
        project_id=project_id,
        cbs_code=cbs_code,
        cbs_name=cbs_name,
        cost_type=cost_type or '',
        description=description or '',
        created_by=created_by,
        updated_by=created_by,
    )
    if parent_id:
        parent = CostBreakdownNode.objects.get(pk=parent_id, project_id=project_id, is_deleted=False)
        return parent.add_child(**kwargs)
    return CostBreakdownNode.add_root(**kwargs)


def delete_cbs_node(node: CostBreakdownNode, user=None):
    if node.get_children().filter(is_deleted=False).exists():
        raise CBSConflictError('Cannot delete a CBS node that has children.')
    if Budget.objects.filter(cbs=node, is_deleted=False).exists():
        raise CBSConflictError('Cannot delete a CBS node linked to budget.')
    if Commitment.objects.filter(cbs=node, is_deleted=False).exists():
        raise CBSConflictError('Cannot delete a CBS node linked to commitment.')
    if ActualCost.objects.filter(cbs=node, is_deleted=False).exists():
        raise CBSConflictError('Cannot delete a CBS node linked to actual cost.')
    node.soft_delete(user=user)


def approve_commitment(commitment: Commitment):
    if not commitment.wbs_id and not commitment.cbs_id:
        raise ValidationError({'code': 'wbs_or_cbs_required', 'message': 'Approve requires wbs or cbs.'})
    commitment.status = CommitmentStatus.APPROVED
    commitment.save(update_fields=['status', 'updated_at'])
    return commitment


def posted_payments_total(commitment: Commitment) -> Decimal:
    total = (
        Payment.objects.filter(
            commitment=commitment,
            is_deleted=False,
            status=PaymentStatus.POSTED,
        ).aggregate(t=Sum('amount'))['t']
        or 0
    )
    return Decimal(total)


def create_payment(*, project, commitment=None, actual_cost=None, amount, paid_at, user, currency='IRR', document_ref='', fx_rate=None):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError({'amount': 'Must be greater than zero'})
    if commitment is not None:
        if posted_payments_total(commitment) + amount > Decimal(commitment.amount):
            raise ValidationError(
                {
                    'code': 'payment_exceeds_commitment',
                    'message': 'Payment would exceed commitment amount.',
                }
            )
    return Payment.objects.create(
        project=project,
        commitment=commitment,
        actual_cost=actual_cost,
        amount=amount,
        currency=currency or 'IRR',
        fx_rate=fx_rate,
        paid_at=paid_at,
        document_ref=document_ref or '',
        status=PaymentStatus.POSTED,
        created_by=user,
        updated_by=user,
    )

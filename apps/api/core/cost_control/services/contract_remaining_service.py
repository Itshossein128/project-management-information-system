"""Contract remaining via cost_control payments on linked commitments."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from contracts.models import Contract
from cost_control.models import Commitment, Payment, PaymentStatus


def contract_cost_remaining(project_id, contract_id) -> dict:
    contract = get_object_or_404(
        Contract,
        pk=contract_id,
        project_id=project_id,
        is_deleted=False,
    )
    approved_amount = Decimal(str(contract.effective_amount))
    commitment_ids = Commitment.objects.filter(
        project_id=project_id,
        contract_id=contract_id,
        is_deleted=False,
    ).values_list('id', flat=True)
    paid_total = (
        Payment.objects.filter(
            project_id=project_id,
            commitment_id__in=commitment_ids,
            is_deleted=False,
            status=PaymentStatus.POSTED,
        ).aggregate(t=Sum('amount'))['t']
        or Decimal('0')
    )
    remaining = Decimal(approved_amount) - Decimal(paid_total)
    return {
        'contract_id': str(contract.id),
        'approved_amount': float(approved_amount),
        'paid_total': float(paid_total),
        'remaining': float(remaining),
    }

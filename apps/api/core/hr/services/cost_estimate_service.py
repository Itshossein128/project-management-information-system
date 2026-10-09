from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Q

from hr.models import ApprovedLaborRate


def _find_rate(project_id, person_id, as_of: date) -> ApprovedLaborRate | None:
    effective_q = Q(effective_to__isnull=True) | Q(effective_to__gte=as_of)
    qs = (
        ApprovedLaborRate.objects.filter(
            project_id=project_id,
            is_deleted=False,
            effective_from__lte=as_of,
        )
        .filter(effective_q)
        .order_by('-effective_from')
    )
    person_rate = qs.filter(person_id=person_id).first()
    if person_rate is not None:
        return person_rate
    return qs.filter(person__isnull=True).first()


def estimate_labor_cost(*, project_id, person_id, approved_hours: Decimal, as_of: date) -> dict:
    rate = _find_rate(project_id, person_id, as_of)
    hours = Decimal(approved_hours)
    if rate is None:
        return {
            'amount': None,
            'currency': None,
            'rate_amount': None,
            'hours': str(hours),
            'warning': 'missing_approved_rate',
        }
    amount = Decimal(rate.amount) * hours
    return {
        'amount': str(amount.quantize(Decimal('0.01'))),
        'currency': rate.currency,
        'rate_amount': str(rate.amount),
        'hours': str(hours),
        'warning': None,
    }

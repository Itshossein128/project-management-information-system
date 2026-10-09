"""Document-traceable cost–commitment–payment ledger report."""

from __future__ import annotations

from django.db.models import Q

from cost_control.models import ActualCost, Commitment, Payment, PaymentStatus


def build_ledger_report(
    project_id,
    *,
    date_from=None,
    date_to=None,
    commitment_id=None,
    document_ref: str | None = None,
) -> dict:
    rows: list[dict] = []

    commitments = Commitment.objects.filter(project_id=project_id, is_deleted=False)
    actuals = ActualCost.objects.filter(project_id=project_id, is_deleted=False)
    payments = Payment.objects.filter(project_id=project_id, is_deleted=False)

    if commitment_id:
        commitments = commitments.filter(pk=commitment_id)
        actuals = actuals.filter(commitment_id=commitment_id)
        payments = payments.filter(commitment_id=commitment_id)
    if document_ref:
        doc = document_ref.strip()
        commitments = commitments.filter(document_ref=doc)
        actuals = actuals.filter(Q(document_ref=doc) | Q(invoice_number=doc))
        payments = payments.filter(document_ref=doc)
    if date_from:
        commitments = commitments.filter(commitment_date__gte=date_from)
        actuals = actuals.filter(cost_date__gte=date_from)
        payments = payments.filter(paid_at__gte=date_from)
    if date_to:
        commitments = commitments.filter(commitment_date__lte=date_to)
        actuals = actuals.filter(cost_date__lte=date_to)
        payments = payments.filter(paid_at__lte=date_to)

    for c in commitments.order_by('commitment_date', 'commitment_number'):
        rows.append(
            {
                'row_type': 'commitment',
                'id': str(c.id),
                'amount': float(c.amount),
                'currency': c.currency,
                'document_ref': c.document_ref or '',
                'status': c.status,
                'date': c.commitment_date.isoformat() if c.commitment_date else None,
                'commitment_id': str(c.id),
                'actual_cost_id': None,
                'contract_id': str(c.contract_id) if c.contract_id else None,
                'requisition_id': str(c.requisition_id) if c.requisition_id else None,
            }
        )

    for a in actuals.order_by('cost_date', 'id'):
        rows.append(
            {
                'row_type': 'actual',
                'id': str(a.id),
                'amount': float(a.amount),
                'currency': 'IRR',
                'document_ref': (a.document_ref or a.invoice_number or ''),
                'status': a.status,
                'date': a.cost_date.isoformat() if a.cost_date else None,
                'commitment_id': str(a.commitment_id) if a.commitment_id else None,
                'actual_cost_id': str(a.id),
                'contract_id': None,
                'requisition_id': None,
            }
        )

    for p in payments.filter(status=PaymentStatus.POSTED).order_by('paid_at', 'id'):
        rows.append(
            {
                'row_type': 'payment',
                'id': str(p.id),
                'amount': float(p.amount),
                'currency': p.currency,
                'document_ref': p.document_ref or '',
                'status': p.status,
                'date': p.paid_at.isoformat() if p.paid_at else None,
                'commitment_id': str(p.commitment_id) if p.commitment_id else None,
                'actual_cost_id': str(p.actual_cost_id) if p.actual_cost_id else None,
                'contract_id': None,
                'requisition_id': None,
            }
        )

    return {'rows': rows}

"""Create commitments from approved purchase requisitions."""

from __future__ import annotations

from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from cost_control.models import Commitment, CommitmentStatus
from procurement.models import RequisitionHeader, RequisitionStatus


def assert_requisition_approved_for_commitment(requisition: RequisitionHeader, project_id):
    if str(requisition.project_id) != str(project_id):
        raise ValidationError(
            {'requisition': 'Must belong to this project.'},
            code='requisition_project_mismatch',
        )
    if requisition.status != RequisitionStatus.APPROVED:
        raise ValidationError(
            {
                'code': 'requisition_not_approved',
                'message': 'Requisition must be approved before creating a commitment.',
            }
        )


def create_commitment_from_requisition(
    *,
    project,
    requisition_id,
    user,
    commitment_number: str,
    amount,
    commitment_date,
    currency: str = 'IRR',
    cbs_id=None,
    wbs_id=None,
    payment_terms: str = '',
    contract_id=None,
    counterparty: str = '',
    description: str = '',
    document_ref: str = '',
) -> Commitment:
    requisition = get_object_or_404(
        RequisitionHeader,
        pk=requisition_id,
        is_deleted=False,
    )
    assert_requisition_approved_for_commitment(requisition, project.id)
    return Commitment.objects.create(
        project=project,
        commitment_number=commitment_number,
        amount=Decimal(str(amount)),
        currency=currency or 'IRR',
        commitment_date=commitment_date,
        cbs_id=cbs_id,
        wbs_id=wbs_id,
        payment_terms=payment_terms or '',
        contract_id=contract_id,
        requisition=requisition,
        counterparty=counterparty or '',
        description=description or '',
        document_ref=document_ref or '',
        status=CommitmentStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )

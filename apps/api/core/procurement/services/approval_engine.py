"""State machine for 8-step procurement approval workflow."""
from __future__ import annotations

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from procurement.models import (
    ApprovalAction,
    ApprovalLog,
    RequisitionHeader,
    RequisitionItem,
    RequisitionStatus,
)


WORKFLOW_TRANSITIONS: dict[str, dict[str, str]] = {
    RequisitionStatus.DRAFT:               {'approve': RequisitionStatus.TECHNICAL_REVIEW},
    RequisitionStatus.TECHNICAL_REVIEW:    {'approve': RequisitionStatus.WORKSHOP_APPROVAL,  'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.DRAFT},
    RequisitionStatus.WORKSHOP_APPROVAL:   {'approve': RequisitionStatus.CONTROL_CHECK,      'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.TECHNICAL_REVIEW},
    RequisitionStatus.CONTROL_CHECK:       {'approve': RequisitionStatus.PM_APPROVAL,        'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.WORKSHOP_APPROVAL},
    RequisitionStatus.PM_APPROVAL:         {'approve': RequisitionStatus.PROCUREMENT_QUEUE,  'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.CONTROL_CHECK},
    RequisitionStatus.PROCUREMENT_QUEUE:   {'approve': RequisitionStatus.HQ_CONTROL_APPROVAL,'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.PM_APPROVAL},
    RequisitionStatus.HQ_CONTROL_APPROVAL: {'approve': RequisitionStatus.FINAL_APPROVAL,     'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.PROCUREMENT_QUEUE},
    RequisitionStatus.FINAL_APPROVAL:      {'approve': RequisitionStatus.APPROVED,            'reject': RequisitionStatus.REJECTED, 'return': RequisitionStatus.HQ_CONTROL_APPROVAL},
}

# Maps each step to the required role (for future permission checking)
STEP_REQUIRED_ROLES: dict[str, str] = {
    RequisitionStatus.DRAFT:               'block_engineer',
    RequisitionStatus.TECHNICAL_REVIEW:    'technical_office',
    RequisitionStatus.WORKSHOP_APPROVAL:   'workshop_supervisor',
    RequisitionStatus.CONTROL_CHECK:       'project_controller',
    RequisitionStatus.PM_APPROVAL:         'project_manager',
    RequisitionStatus.PROCUREMENT_QUEUE:   'procurement_officer',
    RequisitionStatus.HQ_CONTROL_APPROVAL: 'hq_project_controller',
    RequisitionStatus.FINAL_APPROVAL:      'ceo_or_pm_budget',
}


class ApprovalEngineError(ValidationError):
    pass


def _validate_control_check(requisition: RequisitionHeader) -> None:
    """Gate 1: total requested qty must not exceed estimated block budget per material."""
    for item in requisition.items.filter(is_deleted=False):
        total_requested = (
            RequisitionItem.objects.filter(
                header__block=requisition.block,
                material=item.material,
                status__in=[
                    'pending', 'approved', 'ordered',
                ],
                is_deleted=False,
            ).aggregate(total=Sum('requested_qty'))['total'] or 0
        )
        budget_qty = item.material.estimated_total_qty or 0
        if budget_qty > 0 and total_requested > budget_qty:
            raise ApprovalEngineError(
                {
                    'detail': (
                        f'مجموع درخواستها ({total_requested}) '
                        f'بیشتر از برآورد بلوک ({budget_qty}) است — متریال: {item.material}'
                    )
                }
            )


_VALIDATORS: dict[str, list] = {
    RequisitionStatus.CONTROL_CHECK: [_validate_control_check],
}


@transaction.atomic
def transition(
    requisition: RequisitionHeader,
    action: str,  # 'approve' | 'reject' | 'return'
    performed_by,
    comments: str = '',
) -> RequisitionHeader:
    """Advance (or reject/return) a requisition through the approval workflow."""
    current_status = requisition.status
    transitions = WORKFLOW_TRANSITIONS.get(current_status, {})

    if action not in transitions:
        raise ApprovalEngineError(
            {'detail': f'Action "{action}" is not allowed at step "{current_status}"'}
        )

    next_status = transitions[action]

    # Run validators for the transition target step
    for validator in _VALIDATORS.get(next_status, []):
        validator(requisition)

    step_from = current_status
    step_to = next_status

    ApprovalLog.objects.create(
        requisition=requisition,
        step_from=step_from,
        step_to=step_to,
        action=action,
        performed_by=performed_by,
        comments=comments,
    )

    requisition.status = next_status
    requisition.updated_by = performed_by
    requisition.save(update_fields=['status', 'updated_by', 'updated_at'])
    return requisition

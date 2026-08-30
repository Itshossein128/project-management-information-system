"""State machine for procurement requisition approval workflow."""
from __future__ import annotations

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from procurement.models import RequisitionHeader, RequisitionItem, RequisitionScope, RequisitionStatus

# Block-scoped requisitions include workshop_approval step.
BLOCK_WORKFLOW_TRANSITIONS: dict[str, dict[str, str]] = {
    RequisitionStatus.DRAFT: {
        'approve': RequisitionStatus.TECHNICAL_REVIEW,
        'reject': RequisitionStatus.REJECTED,
    },
    RequisitionStatus.TECHNICAL_REVIEW: {
        'approve': RequisitionStatus.WORKSHOP_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.DRAFT,
    },
    RequisitionStatus.WORKSHOP_APPROVAL: {
        'approve': RequisitionStatus.CONTROL_CHECK,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.TECHNICAL_REVIEW,
    },
    RequisitionStatus.CONTROL_CHECK: {
        'approve': RequisitionStatus.PM_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.WORKSHOP_APPROVAL,
    },
    RequisitionStatus.PM_APPROVAL: {
        'approve': RequisitionStatus.PROCUREMENT_QUEUE,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.CONTROL_CHECK,
    },
    RequisitionStatus.PROCUREMENT_QUEUE: {
        'approve': RequisitionStatus.HQ_CONTROL_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.PM_APPROVAL,
    },
    RequisitionStatus.HQ_CONTROL_APPROVAL: {
        'approve': RequisitionStatus.FINAL_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.PROCUREMENT_QUEUE,
    },
    RequisitionStatus.FINAL_APPROVAL: {
        'approve': RequisitionStatus.APPROVED,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.HQ_CONTROL_APPROVAL,
    },
}

# Workshop-scoped requisitions skip workshop_approval.
WORKSHOP_WORKFLOW_TRANSITIONS: dict[str, dict[str, str]] = {
    RequisitionStatus.DRAFT: {
        'approve': RequisitionStatus.TECHNICAL_REVIEW,
        'reject': RequisitionStatus.REJECTED,
    },
    RequisitionStatus.TECHNICAL_REVIEW: {
        'approve': RequisitionStatus.CONTROL_CHECK,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.DRAFT,
    },
    RequisitionStatus.CONTROL_CHECK: {
        'approve': RequisitionStatus.PM_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.TECHNICAL_REVIEW,
    },
    RequisitionStatus.PM_APPROVAL: {
        'approve': RequisitionStatus.PROCUREMENT_QUEUE,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.CONTROL_CHECK,
    },
    RequisitionStatus.PROCUREMENT_QUEUE: {
        'approve': RequisitionStatus.HQ_CONTROL_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.PM_APPROVAL,
    },
    RequisitionStatus.HQ_CONTROL_APPROVAL: {
        'approve': RequisitionStatus.FINAL_APPROVAL,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.PROCUREMENT_QUEUE,
    },
    RequisitionStatus.FINAL_APPROVAL: {
        'approve': RequisitionStatus.APPROVED,
        'reject': RequisitionStatus.REJECTED,
        'return': RequisitionStatus.HQ_CONTROL_APPROVAL,
    },
}

# Backward-compatible alias used by existing tests/imports.
WORKFLOW_TRANSITIONS = BLOCK_WORKFLOW_TRANSITIONS

# Maps each step to the required role (for permission checking).
STEP_REQUIRED_ROLES: dict[str, str] = {
    RequisitionStatus.DRAFT: 'block_engineer',
    RequisitionStatus.TECHNICAL_REVIEW: 'technical_office',
    RequisitionStatus.WORKSHOP_APPROVAL: 'workshop_supervisor',
    RequisitionStatus.CONTROL_CHECK: 'project_controller',
    RequisitionStatus.PM_APPROVAL: 'project_manager',
    RequisitionStatus.PROCUREMENT_QUEUE: 'procurement_officer',
    RequisitionStatus.HQ_CONTROL_APPROVAL: 'hq_project_controller',
    RequisitionStatus.FINAL_APPROVAL: 'ceo_or_pm_budget',
}

DRAFT_ROLE_BY_SCOPE: dict[str, str] = {
    RequisitionScope.BLOCK: 'block_engineer',
    RequisitionScope.WORKSHOP: 'workshop_supervisor',
}


class ApprovalEngineError(ValidationError):
    pass


def get_transitions(requisition: RequisitionHeader) -> dict[str, dict[str, str]]:
    if requisition.scope == RequisitionScope.WORKSHOP:
        return WORKSHOP_WORKFLOW_TRANSITIONS
    return BLOCK_WORKFLOW_TRANSITIONS


def get_required_role(requisition: RequisitionHeader) -> str | None:
    if requisition.status == RequisitionStatus.DRAFT:
        return DRAFT_ROLE_BY_SCOPE.get(requisition.scope, 'block_engineer')
    return STEP_REQUIRED_ROLES.get(requisition.status)


def _validate_control_check(requisition: RequisitionHeader) -> None:
    """Gate 1: total requested qty must not exceed estimated block budget per material."""
    block = requisition.block
    for item in requisition.items.filter(is_deleted=False):
        total_requested = (
            RequisitionItem.objects.filter(
                header__block=block,
                header__project=requisition.project,
                material=item.material,
                status__in=['pending', 'approved', 'ordered'],
                is_deleted=False,
            ).aggregate(total=Sum('requested_qty'))['total'] or 0
        )
        budget_qty = item.material.estimated_total_qty or 0
        if budget_qty > 0 and total_requested > budget_qty:
            scope_label = 'کارگاه' if requisition.scope == RequisitionScope.WORKSHOP else block.block_code
            raise ApprovalEngineError(
                {
                    'detail': (
                        f'مجموع درخواست‌ها ({total_requested}) '
                        f'بیشتر از برآورد بلوک ({budget_qty}) است — '
                        f'متریال: {item.material} — محدوده: {scope_label}'
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
    from procurement.models import ApprovalLog

    current_status = requisition.status
    transitions = get_transitions(requisition)

    if action not in transitions.get(current_status, {}):
        raise ApprovalEngineError(
            {'detail': f'Action "{action}" is not allowed at step "{current_status}"'}
        )

    next_status = transitions[current_status][action]

    for validator in _VALIDATORS.get(next_status, []):
        validator(requisition)

    ApprovalLog.objects.create(
        requisition=requisition,
        step_from=current_status,
        step_to=next_status,
        action=action,
        performed_by=performed_by,
        comments=comments,
    )

    requisition.status = next_status
    requisition.updated_by = performed_by
    requisition.save(update_fields=['status', 'updated_by', 'updated_at'])
    return requisition

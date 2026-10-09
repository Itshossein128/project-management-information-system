"""Budget change requests — approved-workflow edits to control baseline."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from config.exceptions import CodedValidationError, ConflictError
from cost_control.models import (
    Budget,
    BudgetChangeRequest,
    BudgetChangeRequestStatus,
    BudgetLineLevel,
    BudgetVersionKind,
    BudgetVersionStatus,
)
from cost_control.services.budget_version_service import (
    clone_version_lines,
    create_version,
    get_control_version,
    project_ceiling,
)

OPEN_STATUSES = (
    BudgetChangeRequestStatus.DRAFT,
    BudgetChangeRequestStatus.SUBMITTED,
)


def _assert_no_open(project_id, exclude_id=None) -> None:
    qs = BudgetChangeRequest.objects.filter(
        project_id=project_id,
        status__in=OPEN_STATUSES,
        is_deleted=False,
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    if qs.exists():
        raise ConflictError(
            'An open budget change request already exists.',
            code='change_request_already_open',
        )


def list_change_requests(project_id):
    return BudgetChangeRequest.objects.filter(project_id=project_id, is_deleted=False)


@transaction.atomic
def create_change_request(
    *,
    project_id,
    user,
    reason: str,
    project_impact: str,
    amount_delta,
    affected_lines: list,
) -> BudgetChangeRequest:
    if not reason or len(reason.strip()) < 10:
        raise CodedValidationError(
            {'reason': 'Reason must be at least 10 characters.'},
            code='reason_required',
        )
    if not project_impact or len(project_impact.strip()) < 3:
        raise CodedValidationError(
            {'project_impact': 'Project impact is required.'},
            code='project_impact_required',
        )
    control = get_control_version(project_id)
    if not control:
        raise CodedValidationError(
            {'base_version': 'No approved control budget version exists.'},
            code='no_control_budget',
        )
    _assert_no_open(project_id)
    return BudgetChangeRequest.objects.create(
        project_id=project_id,
        base_version=control,
        reason=reason.strip(),
        project_impact=project_impact.strip(),
        amount_delta=Decimal(str(amount_delta or 0)),
        affected_lines=affected_lines or [],
        status=BudgetChangeRequestStatus.DRAFT,
        requested_by=user,
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def update_change_request(cr: BudgetChangeRequest, user, **fields) -> BudgetChangeRequest:
    if cr.status != BudgetChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'status': 'Only draft change requests can be updated.'},
            code='invalid_change_request_status',
        )
    if 'reason' in fields:
        reason = fields['reason']
        if not reason or len(str(reason).strip()) < 10:
            raise CodedValidationError(
                {'reason': 'Reason must be at least 10 characters.'},
                code='reason_required',
            )
        cr.reason = str(reason).strip()
    if 'project_impact' in fields:
        impact = fields['project_impact']
        if not impact or len(str(impact).strip()) < 3:
            raise CodedValidationError(
                {'project_impact': 'Project impact is required.'},
                code='project_impact_required',
            )
        cr.project_impact = str(impact).strip()
    if 'amount_delta' in fields:
        cr.amount_delta = Decimal(str(fields['amount_delta'] or 0))
    if 'affected_lines' in fields:
        cr.affected_lines = fields['affected_lines'] or []
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def submit_change_request(cr: BudgetChangeRequest, user) -> BudgetChangeRequest:
    if cr.status != BudgetChangeRequestStatus.DRAFT:
        raise CodedValidationError(
            {'status': 'Only draft change requests can be submitted.'},
            code='invalid_change_request_status',
        )
    if not cr.affected_lines:
        raise CodedValidationError(
            {'affected_lines': 'At least one affected line is required.'},
            code='affected_lines_required',
        )
    cr.status = BudgetChangeRequestStatus.SUBMITTED
    cr.updated_by = user
    cr.save(update_fields=['status', 'updated_by', 'updated_at'])
    return cr


def _apply_ops(version, ops: list, user) -> None:
    for op in ops:
        action = (op or {}).get('op')
        if action == 'create':
            level = op.get('level') or BudgetLineLevel.WBS
            Budget.objects.create(
                project_id=version.project_id,
                version=version,
                level=level,
                wbs_id=op.get('wbs'),
                activity_id=op.get('activity'),
                cbs_id=op.get('cbs'),
                contract_id=op.get('contract'),
                cost_category=op['cost_category'],
                budget_amount=Decimal(str(op['budget_amount'])),
                period_start=op.get('period_start'),
                period_end=op.get('period_end'),
                notes=op.get('notes', ''),
                created_by=user,
                updated_by=user,
            )
        elif action == 'update':
            line = Budget.objects.get(
                pk=op['line_id'],
                version=version,
                is_deleted=False,
            )
            if 'budget_amount' in op:
                line.budget_amount = Decimal(str(op['budget_amount']))
            if 'notes' in op:
                line.notes = op.get('notes') or ''
            line.updated_by = user
            line.save()
        elif action == 'delete':
            line = Budget.objects.get(
                pk=op['line_id'],
                version=version,
                is_deleted=False,
            )
            line.soft_delete(user=user)
        else:
            raise CodedValidationError(
                {'affected_lines': f'Unknown op: {action}'},
                code='invalid_affected_lines',
            )


@transaction.atomic
def approve_change_request(cr: BudgetChangeRequest, user, decision_notes: str = '') -> BudgetChangeRequest:
    from permissions.sod import assert_not_self_final_approve

    if cr.status != BudgetChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'status': 'Only submitted change requests can be approved.'},
            code='invalid_change_request_status',
        )
    assert_not_self_final_approve(cr.created_by_id, user)
    control = get_control_version(cr.project_id)
    if not control or control.id != cr.base_version_id:
        # Still allow if base was control at create; re-clone from base_version
        control = cr.base_version

    new_version = create_version(
        project_id=cr.project_id,
        user=user,
        kind=BudgetVersionKind.REVISED,
        name=f'Revised from CR {cr.id}',
        currency=control.currency,
        notes=cr.reason,
    )
    clone_version_lines(control, new_version, user)

    # Remap update/delete line_ids from base version → cloned lines by matching key fields
    base_lines = {
        str(l.id): l for l in Budget.objects.filter(version=control, is_deleted=False)
    }
    clone_by_base: dict[str, Budget] = {}
    clones = list(Budget.objects.filter(version=new_version, is_deleted=False))
    for clone in clones:
        for base_id, base in base_lines.items():
            if (
                clone.level == base.level
                and clone.wbs_id == base.wbs_id
                and clone.activity_id == base.activity_id
                and clone.cbs_id == base.cbs_id
                and clone.contract_id == base.contract_id
                and clone.cost_category == base.cost_category
                and clone.period_start == base.period_start
                and clone.period_end == base.period_end
                and base_id not in clone_by_base
            ):
                clone_by_base[base_id] = clone
                break

    remapped = []
    for op in cr.affected_lines:
        op = dict(op)
        if op.get('op') in ('update', 'delete') and op.get('line_id'):
            mapped = clone_by_base.get(str(op['line_id']))
            if not mapped:
                raise CodedValidationError(
                    {'affected_lines': f'Line {op["line_id"]} not found on base version.'},
                    code='invalid_affected_lines',
                )
            op['line_id'] = str(mapped.id)
        remapped.append(op)

    _apply_ops(new_version, remapped, user)

    # Promote new version to approved control
    from cost_control.models import BudgetVersion

    BudgetVersion.objects.filter(
        project_id=cr.project_id,
        is_deleted=False,
        is_control=True,
    ).update(is_control=False, updated_at=timezone.now())

    new_version.status = BudgetVersionStatus.APPROVED
    new_version.is_control = True
    new_version.approved_at = timezone.now()
    new_version.approved_by = user
    new_version.submitted_at = timezone.now()
    new_version.submitted_by = user
    new_version.updated_by = user
    new_version.save()

    cr.status = BudgetChangeRequestStatus.APPROVED
    cr.resulting_version = new_version
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def reject_change_request(cr: BudgetChangeRequest, user, decision_notes: str = '') -> BudgetChangeRequest:
    if cr.status != BudgetChangeRequestStatus.SUBMITTED:
        raise CodedValidationError(
            {'status': 'Only submitted change requests can be rejected.'},
            code='invalid_change_request_status',
        )
    cr.status = BudgetChangeRequestStatus.REJECTED
    cr.decided_by = user
    cr.decided_at = timezone.now()
    cr.decision_notes = decision_notes or ''
    cr.updated_by = user
    cr.save()
    return cr


@transaction.atomic
def cancel_change_request(cr: BudgetChangeRequest, user) -> BudgetChangeRequest:
    if cr.status not in OPEN_STATUSES:
        raise CodedValidationError(
            {'status': 'Only draft or submitted change requests can be cancelled.'},
            code='invalid_change_request_status',
        )
    cr.status = BudgetChangeRequestStatus.CANCELLED
    cr.updated_by = user
    cr.save(update_fields=['status', 'updated_by', 'updated_at'])
    return cr


def current_spent_against_budget(project_id) -> Decimal:
    """Approved commitments + actual costs (project-level consumption)."""
    from cost_control.models import ActualCost, Commitment, CommitmentStatus

    committed = (
        Commitment.objects.filter(
            project_id=project_id,
            is_deleted=False,
            status=CommitmentStatus.APPROVED,
        ).aggregate(t=Sum('amount'))['t']
        or Decimal('0')
    )
    consumed = (
        ActualCost.objects.filter(project_id=project_id, is_deleted=False).aggregate(
            t=Sum('amount')
        )['t']
        or Decimal('0')
    )
    return Decimal(committed) + Decimal(consumed)


def assert_within_project_ceiling(project_id, proposed_total: Decimal) -> None:
    ceiling = project_ceiling(project_id)
    if ceiling <= 0:
        return
    if Decimal(proposed_total) > ceiling:
        raise CodedValidationError(
            {
                'ceiling': 'Allocation exceeds approved project budget ceiling.',
                'ceiling_amount': str(ceiling),
                'proposed_total': str(proposed_total),
            },
            code='project_ceiling_exceeded',
        )

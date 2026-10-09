"""Budget version lifecycle: create, submit, approve, reject, compare."""

from __future__ import annotations

from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone

from config.exceptions import CodedValidationError
from cost_control.models import (
    Budget,
    BudgetVersion,
    BudgetVersionKind,
    BudgetVersionStatus,
)


CONTROL_KINDS = (
    BudgetVersionKind.APPROVED,
    BudgetVersionKind.REVISED,
)


def next_version_number(project_id) -> int:
    current = (
        BudgetVersion.objects.filter(project_id=project_id, is_deleted=False)
        .aggregate(m=models.Max('version_number'))['m']
        or 0
    )
    return int(current) + 1


def get_control_version(project_id) -> BudgetVersion | None:
    return (
        BudgetVersion.objects.filter(
            project_id=project_id,
            is_deleted=False,
            is_control=True,
            status=BudgetVersionStatus.APPROVED,
        )
        .order_by('-version_number')
        .first()
    )


def project_ceiling(project_id) -> Decimal:
    control = get_control_version(project_id)
    if not control:
        return Decimal('0')
    total = (
        Budget.objects.filter(version=control, is_deleted=False).aggregate(
            total=Sum('budget_amount')
        )['total']
        or Decimal('0')
    )
    return Decimal(total)


def assert_version_editable(version: BudgetVersion) -> None:
    if version.status != BudgetVersionStatus.DRAFT:
        raise CodedValidationError(
            {'version': 'Only draft budget versions can be edited.'},
            code='budget_version_locked',
        )


def ensure_working_draft(project_id, user, *, currency: str = 'IRR') -> BudgetVersion:
    """Return an editable draft, creating initial draft if none exists."""
    draft = (
        BudgetVersion.objects.filter(
            project_id=project_id,
            is_deleted=False,
            status=BudgetVersionStatus.DRAFT,
        )
        .order_by('-version_number')
        .first()
    )
    if draft:
        return draft
    return create_version(
        project_id=project_id,
        user=user,
        kind=BudgetVersionKind.INITIAL,
        currency=currency,
        name='Working draft',
    )


@transaction.atomic
def create_version(
    *,
    project_id,
    user,
    kind: str,
    name: str = '',
    currency: str = 'IRR',
    notes: str = '',
) -> BudgetVersion:
    if kind == BudgetVersionKind.APPROVED:
        raise CodedValidationError(
            {'kind': 'Cannot create an approved version directly; submit and approve a draft.'},
            code='invalid_budget_kind',
        )
    if kind not in {c.value for c in BudgetVersionKind}:
        raise CodedValidationError({'kind': 'Invalid kind.'}, code='invalid_budget_kind')
    return BudgetVersion.objects.create(
        project_id=project_id,
        kind=kind,
        status=BudgetVersionStatus.DRAFT,
        version_number=next_version_number(project_id),
        name=name or '',
        currency=currency or 'IRR',
        notes=notes or '',
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def submit_version(version: BudgetVersion, user) -> BudgetVersion:
    if version.status != BudgetVersionStatus.DRAFT:
        raise CodedValidationError(
            {'status': 'Only draft versions can be submitted.'},
            code='invalid_budget_version_status',
        )
    if not Budget.objects.filter(version=version, is_deleted=False).exists():
        raise CodedValidationError(
            {'lines': 'At least one budget line is required before submit.'},
            code='budget_version_empty',
        )
    version.status = BudgetVersionStatus.SUBMITTED
    version.submitted_at = timezone.now()
    version.submitted_by = user
    version.updated_by = user
    version.save(
        update_fields=[
            'status',
            'submitted_at',
            'submitted_by',
            'updated_by',
            'updated_at',
        ]
    )
    return version


@transaction.atomic
def approve_version(
    version: BudgetVersion,
    user,
    *,
    promote_to_control: bool = False,
    from_change_request: bool = False,
) -> BudgetVersion:
    if version.status != BudgetVersionStatus.SUBMITTED:
        raise CodedValidationError(
            {'status': 'Only submitted versions can be approved.'},
            code='invalid_budget_version_status',
        )

    become_control = False
    if version.kind == BudgetVersionKind.FINAL_FORECAST:
        become_control = bool(promote_to_control)
    elif version.kind in (
        BudgetVersionKind.INITIAL,
        BudgetVersionKind.APPROVED,
        BudgetVersionKind.REVISED,
    ):
        become_control = True

    existing_control = get_control_version(version.project_id)
    if (
        become_control
        and existing_control
        and existing_control.id != version.id
        and not from_change_request
    ):
        # FR-003: replacing an approved control baseline requires a budget change request.
        raise CodedValidationError(
            {
                'version': (
                    'A control approved budget already exists. '
                    'Change amounts via a budget change request.'
                ),
            },
            code='budget_change_request_required',
        )

    if become_control:
        BudgetVersion.objects.filter(
            project_id=version.project_id,
            is_deleted=False,
            is_control=True,
        ).exclude(pk=version.pk).update(is_control=False, updated_at=timezone.now())

    if version.kind == BudgetVersionKind.INITIAL:
        version.kind = BudgetVersionKind.APPROVED

    version.status = BudgetVersionStatus.APPROVED
    version.is_control = become_control
    version.approved_at = timezone.now()
    version.approved_by = user
    version.updated_by = user
    version.save(
        update_fields=[
            'kind',
            'status',
            'is_control',
            'approved_at',
            'approved_by',
            'updated_by',
            'updated_at',
        ]
    )
    return version


@transaction.atomic
def reject_version(version: BudgetVersion, user, reason: str = '') -> BudgetVersion:
    if version.status != BudgetVersionStatus.SUBMITTED:
        raise CodedValidationError(
            {'status': 'Only submitted versions can be rejected.'},
            code='invalid_budget_version_status',
        )
    version.status = BudgetVersionStatus.REJECTED
    version.rejected_at = timezone.now()
    version.rejected_by = user
    version.rejection_reason = reason or ''
    version.updated_by = user
    version.save(
        update_fields=[
            'status',
            'rejected_at',
            'rejected_by',
            'rejection_reason',
            'updated_by',
            'updated_at',
        ]
    )
    return version


def clone_version_lines(source: BudgetVersion, target: BudgetVersion, user) -> list[Budget]:
    created: list[Budget] = []
    for line in Budget.objects.filter(version=source, is_deleted=False):
        created.append(
            Budget.objects.create(
                project_id=source.project_id,
                version=target,
                level=line.level,
                activity_id=line.activity_id,
                wbs_id=line.wbs_id,
                cbs_id=line.cbs_id,
                contract_id=line.contract_id,
                cost_category=line.cost_category,
                budget_amount=line.budget_amount,
                period_start=line.period_start,
                period_end=line.period_end,
                currency=line.currency,
                notes=line.notes,
                created_by=user,
                updated_by=user,
            )
        )
    return created


def compare_versions(
    left: BudgetVersion,
    right: BudgetVersion,
    *,
    fx_rate: Decimal | None = None,
) -> dict:
    if left.currency != right.currency and fx_rate is None:
        raise CodedValidationError(
            {'fx_rate': 'Explicit fx_rate required when comparing different currencies.'},
            code='fx_rate_required',
        )
    rate = fx_rate if fx_rate is not None else Decimal('1')

    def _key(line: Budget) -> str:
        return '|'.join(
            [
                line.level or '',
                str(line.wbs_id or ''),
                str(line.activity_id or ''),
                str(line.cbs_id or ''),
                str(line.contract_id or ''),
                line.cost_category or '',
                str(line.period_start or ''),
                str(line.period_end or ''),
            ]
        )

    left_map = {
        _key(l): l
        for l in Budget.objects.filter(version=left, is_deleted=False)
    }
    right_map = {
        _key(l): l
        for l in Budget.objects.filter(version=right, is_deleted=False)
    }
    keys = sorted(set(left_map) | set(right_map))
    diffs = []
    for key in keys:
        la = Decimal(left_map[key].budget_amount) if key in left_map else Decimal('0')
        ra = Decimal(right_map[key].budget_amount) if key in right_map else Decimal('0')
        ra_converted = ra * rate
        diffs.append(
            {
                'key': key,
                'left_amount': float(la),
                'right_amount': float(ra),
                'right_amount_converted': float(ra_converted),
                'delta': float(ra_converted - la),
            }
        )
    return {
        'left_id': str(left.id),
        'right_id': str(right.id),
        'fx_rate': float(rate),
        'diffs': diffs,
    }

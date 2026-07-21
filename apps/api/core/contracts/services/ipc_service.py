"""IPC auto-population and deduction services."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from contracts.models import ContractType, ContractItem, IPC, IPCDeduction, IPCItem, IPCStatus
from cash_flow.models import CashTransaction, CashTransactionType, InflowCategory, OutflowCategory
from schedule.models import ActivityProgress

logger = logging.getLogger(__name__)

MANUAL_DEDUCTION_TYPES = frozenset({'material_price_diff', 'other'})


def _invalidate(project_id):
    try:
        from common.cache_utils import invalidate_project_caches
        invalidate_project_caches(project_id)
    except Exception:
        pass


def _publish_ipc_submitted(ipc):
    try:
        from events.publisher import EventPublisher

        EventPublisher().publish(
            'ipc.submitted',
            {
                'ipc_id': str(ipc.id),
                'ipc_number': ipc.ipc_number,
                'contract_id': str(ipc.contract_id),
                'gross_amount': str(ipc.gross_amount or 0),
            },
            project_id=str(ipc.project_id),
        )
    except Exception:  # noqa: BLE001 - event bus optional in dev/tests
        logger.warning('Could not publish ipc.submitted for %s', ipc.id, exc_info=True)


def _ipc_cash_transaction_defaults(ipc, user, payment_date):
    contract = ipc.contract
    if contract.contract_type == ContractType.MAIN:
        tx_type = CashTransactionType.IN
        category = InflowCategory.IPC_RECEIPT
    elif contract.contract_type == ContractType.SUBCONTRACT:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.SUBCONTRACTOR_PAYMENT
    elif contract.contract_type == ContractType.PURCHASE:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.SUPPLIER_PAYMENT
    elif contract.contract_type == ContractType.EQUIPMENT_RENTAL:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.EQUIPMENT_RENTAL
    else:
        tx_type = CashTransactionType.OUT
        category = OutflowCategory.OTHER_EXPENSE

    return {
        'project_id': ipc.project_id,
        'tx_date': payment_date,
        'tx_type': tx_type,
        'category': category,
        'amount': ipc.net_amount or ipc.gross_amount,
        'description': (
            f'صدور موقت شماره {ipc.ipc_number} — '
            f'قرارداد {contract.contract_number or contract.counterparty}'
        ),
        'contract': contract,
        'counterparty': contract.counterparty,
        'is_forecast': False,
        'actual_date': payment_date,
        'updated_by': user,
        'is_deleted': False,
        'deleted_at': None,
    }


def _upsert_ipc_cash_transaction(ipc, user, payment_date=None):
    payment_date = payment_date or date.today()
    defaults = _ipc_cash_transaction_defaults(ipc, user, payment_date)
    existing = CashTransaction.objects.filter(ipc=ipc, is_deleted=False).first()
    if existing:
        for field, value in defaults.items():
            setattr(existing, field, value)
        existing.save()
    else:
        CashTransaction.objects.create(
            ipc=ipc,
            created_by=user,
            **defaults,
        )
    _invalidate(ipc.project_id)




@transaction.atomic
def create_ipc(project_id, contract, validated_data, user):
    ipc = IPC.objects.create(
        project_id=project_id,
        contract=contract,
        ipc_number=next_ipc_number(contract.id),
        period_start=validated_data.get('period_start'),
        period_end=validated_data.get('period_end'),
        prepared_date=validated_data.get('prepared_date') or date.today(),
        notes=validated_data.get('notes', ''),
        created_by=user,
        updated_by=user,
    )
    try:
        from contracts.tasks import populate_ipc_async
        populate_ipc_async.delay(str(ipc.id))
    except Exception:
        auto_populate_ipc(ipc.id)
        apply_deductions(ipc.id)
    ipc.refresh_from_db()
    return ipc



@transaction.atomic
def update_ipc(ipc, validated_data, user):
    from rest_framework.exceptions import ValidationError
    if ipc.status != IPCStatus.DRAFT:
        raise ValidationError({'detail': 'Only draft IPCs can be edited.'})
    for field in ('period_start', 'period_end', 'prepared_date', 'notes'):
        if field in validated_data:
            setattr(ipc, field, validated_data[field])
    ipc.updated_by = user
    ipc.save()
    return ipc


@transaction.atomic
def auto_populate_ipc(ipc_id):
    """
    Automatically populates the items of an Interim Payment Certificate (IPC) based on
    the schedule of values (SoV) defined in its parent contract.
    It links each IPC item to a contract item, carrying over the cumulative quantities
    from the previous IPC to serve as the baseline for the current period's claim.
    """
    ipc = IPC.objects.get(pk=ipc_id)
    contract = ipc.contract

    for item in contract.items.filter(is_deleted=False):
        previous_ipcs = IPC.objects.filter(
            contract=contract,
            ipc_number__lt=ipc.ipc_number,
            status__in=[IPCStatus.APPROVED, IPCStatus.PAID],
            is_deleted=False,
        )
        qty_previous = IPCItem.objects.filter(
            ipc__in=previous_ipcs,
            contract_item=item,
            is_deleted=False,
        ).aggregate(total=Sum('qty_current'))['total'] or Decimal('0')

        qty_current = Decimal('0')
        if item.activity_id and ipc.period_start and ipc.period_end:
            progress_records = ActivityProgress.objects.filter(
                activity_id=item.activity_id,
                report_date__gte=ipc.period_start,
                report_date__lte=ipc.period_end,
            )
            if progress_records.exists():
                latest = progress_records.order_by('-report_date').first()
                earliest_before = ActivityProgress.objects.filter(
                    activity_id=item.activity_id,
                    report_date__lt=ipc.period_start,
                ).order_by('-report_date').first()
                progress_start = float(earliest_before.actual_progress) if earliest_before else 0
                progress_end = float(latest.actual_progress)
                progress_delta = max(progress_end - progress_start, 0)
                qty_current = Decimal(str(progress_delta * float(item.activity.total_quantity or 0)))

        unit_price = item.unit_price or Decimal('0')
        qty_cum = qty_previous + qty_current
        audit_user = ipc.updated_by or ipc.created_by
        defaults = {
            'description': item.description,
            'unit': item.unit.name if item.unit_id else '',
            'unit_price': unit_price,
            'qty_previous': qty_previous,
            'qty_current': round(qty_current, 4),
            'qty_cumulative': qty_cum,
            'amount_current': unit_price * qty_current,
            'amount_cumulative': unit_price * qty_cum,
        }
        if audit_user:
            defaults['created_by'] = audit_user
            defaults['updated_by'] = audit_user
        IPCItem.objects.update_or_create(
            ipc=ipc,
            contract_item=item,
            defaults=defaults,
        )

    gross = IPCItem.objects.filter(ipc=ipc, is_deleted=False).aggregate(
        total=Sum('amount_current')
    )['total'] or Decimal('0')
    ipc.gross_amount = gross
    ipc.save(update_fields=['gross_amount', 'updated_at'])


@transaction.atomic
def apply_deductions(ipc_id):
    """
    Recalculates and applies standard automatic deductions (such as retention, tax, and
    advance payment recovery) to an IPC based on its contract's terms and the current
    gross amount claimed.
    It preserves manually entered deductions (e.g., material price differences) and
    updates the IPC's final net amount.
    """
    ipc = IPC.objects.get(pk=ipc_id)
    contract = ipc.contract
    gross = float(ipc.gross_amount or 0)

    from django.utils import timezone
    auto_types = ('retention', 'tax', 'insurance', 'advance_recovery')
    IPCDeduction.objects.filter(ipc=ipc, deduction_type__in=auto_types, is_deleted=False).update(
        is_deleted=True, deleted_at=timezone.now()
    )

    deductions = []

    if contract.retention_pct and float(contract.retention_pct) > 0:
        deductions.append(IPCDeduction(
            ipc=ipc,
            deduction_type='retention',
            amount=Decimal(str(gross * float(contract.retention_pct) / 100)),
            description=f'سپرده حسن انجام کار {contract.retention_pct}٪',
        ))

    if contract.tax_pct and float(contract.tax_pct) > 0:
        deductions.append(IPCDeduction(
            ipc=ipc,
            deduction_type='tax',
            amount=Decimal(str(gross * float(contract.tax_pct) / 100)),
            description=f'مالیات {contract.tax_pct}٪',
        ))

    if contract.insurance_pct and float(contract.insurance_pct) > 0:
        deductions.append(IPCDeduction(
            ipc=ipc,
            deduction_type='insurance',
            amount=Decimal(str(gross * float(contract.insurance_pct) / 100)),
            description=f'بیمه {contract.insurance_pct}٪',
        ))

    if contract.advance_payment_pct and float(contract.advance_payment_pct) > 0:
        advance_total = float(contract.effective_amount) * float(contract.advance_payment_pct) / 100
        already_recovered = IPCDeduction.objects.filter(
            ipc__contract=contract,
            ipc__status__in=[IPCStatus.APPROVED, IPCStatus.PAID],
            deduction_type='advance_recovery',
            ipc__is_deleted=False,
            is_deleted=False,
        ).exclude(ipc_id=ipc.id).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        remaining = advance_total - float(already_recovered)
        if remaining > 0:
            recovery = min(gross * float(contract.advance_payment_pct) / 100, remaining)
            deductions.append(IPCDeduction(
                ipc=ipc,
                deduction_type='advance_recovery',
                amount=Decimal(str(recovery)),
                description='استهلاک پیش‌پرداخت',
            ))

    audit_user = ipc.updated_by or ipc.created_by
    for d in deductions:
        if audit_user:
            d.created_by = audit_user
            d.updated_by = audit_user

    IPCDeduction.objects.bulk_create(deductions)

    total_deductions = sum(float(d.amount) for d in deductions)
    manual = IPCDeduction.objects.filter(
        ipc=ipc, is_deleted=False, deduction_type='material_price_diff'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    other_manual = IPCDeduction.objects.filter(
        ipc=ipc, is_deleted=False, deduction_type='other'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    ipc.net_amount = Decimal(str(gross)) - Decimal(str(total_deductions)) - manual - other_manual
    ipc.save(update_fields=['net_amount', 'updated_at'])


def next_ipc_number(contract_id) -> int:
    last = IPC.objects.filter(contract_id=contract_id, is_deleted=False).order_by('-ipc_number').first()
    return (last.ipc_number + 1) if last else 1


def next_change_number(contract_id) -> int:
    from contracts.models import ChangeOrder

    last = ChangeOrder.objects.filter(contract_id=contract_id, is_deleted=False).order_by('-change_number').first()
    return (last.change_number + 1) if last else 1


@transaction.atomic
def submit_ipc(ipc, user):
    if ipc.status != IPCStatus.DRAFT:
        raise ValueError('Only draft IPCs can be submitted.')
    ipc.status = IPCStatus.SUBMITTED
    ipc.submitted_date = date.today()
    ipc.rejection_reason = ''
    ipc.updated_by = user
    ipc.save()
    _publish_ipc_submitted(ipc)
    return ipc


@transaction.atomic
def approve_ipc(ipc, user):
    from datetime import timedelta
    ipc.status = IPCStatus.APPROVED
    ipc.approval_date = date.today()
    if not ipc.planned_payment_date:
        ipc.planned_payment_date = date.today() + timedelta(days=30)
    ipc.updated_by = user
    ipc.save()
    return ipc


@transaction.atomic
def pay_ipc(ipc, user, payment_date):
    ipc.status = IPCStatus.PAID
    ipc.actual_payment_date = payment_date
    ipc.updated_by = user
    ipc.save()
    _upsert_ipc_cash_transaction(ipc, user, payment_date)
    return ipc


@transaction.atomic
def reject_ipc(ipc, user, reason):
    ipc.status = IPCStatus.DRAFT
    ipc.rejection_reason = reason
    ipc.updated_by = user
    ipc.save()
    return ipc


@transaction.atomic
def update_ipc_item(ipc, item, qty_current, user):
    qty_current = Decimal(str(qty_current))
    item.qty_current = qty_current
    item.qty_cumulative = Decimal(str(item.qty_previous or 0)) + qty_current
    unit_price = Decimal(str(item.unit_price or 0))
    item.amount_current = unit_price * qty_current
    item.amount_cumulative = unit_price * item.qty_cumulative
    item.updated_by = user
    item.save()
    gross = IPCItem.objects.filter(ipc=ipc, is_deleted=False).aggregate(
        total=Sum('amount_current')
    )['total'] or 0
    ipc.gross_amount = gross
    ipc.save(update_fields=['gross_amount', 'updated_at'])
    apply_deductions(ipc.id)
    ipc.refresh_from_db()
    return ipc


@transaction.atomic
def add_manual_deduction(ipc, deduction_type, amount, description, user):
    if ipc.status != IPCStatus.DRAFT:
        raise ValueError('Deductions can only be edited on draft IPCs.')
    if deduction_type not in MANUAL_DEDUCTION_TYPES:
        raise ValueError('Only material_price_diff and other deductions can be added manually.')
    IPCDeduction.objects.create(
        ipc=ipc,
        deduction_type=deduction_type,
        amount=amount,
        description=description,
        created_by=user,
        updated_by=user,
    )
    apply_deductions(ipc.id)
    ipc.refresh_from_db()
    return ipc


@transaction.atomic
def update_manual_deduction(ipc, deduction, amount, description, user):
    if ipc.status != IPCStatus.DRAFT:
        raise ValueError('Deductions can only be edited on draft IPCs.')
    if amount is not None:
        deduction.amount = amount
    if description is not None:
        deduction.description = description
    deduction.updated_by = user
    deduction.save()
    apply_deductions(ipc.id)
    ipc.refresh_from_db()
    return ipc


@transaction.atomic
def delete_manual_deduction(ipc, deduction, user):
    if ipc.status != IPCStatus.DRAFT:
        raise ValueError('Deductions can only be edited on draft IPCs.')
    deduction.is_deleted = True
    deduction.deleted_at = timezone.now()
    deduction.updated_by = user
    deduction.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
    apply_deductions(ipc.id)
    ipc.refresh_from_db()
    return ipc

"""IPC auto-population and deduction services."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum

from contracts.models import ContractItem, IPC, IPCDeduction, IPCItem, IPCStatus
from schedule.models import ActivityProgress


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

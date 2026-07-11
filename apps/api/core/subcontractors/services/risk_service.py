"""Subcontractor risk and financial computation."""

from __future__ import annotations

from datetime import date

from django.db.models import Sum

from contracts.models import IPC, IPCStatus
from subcontractors.models import Subcontractor, SubcontractorStatus, WarningType


def financial_summary(sub: Subcontractor) -> dict:
    if not sub.contract_id:
        return {
            'total_billed': 0,
            'total_paid': 0,
            'outstanding': 0,
            'retention_held': 0,
            'advance_remaining': 0,
        }

    ipcs = IPC.objects.filter(contract_id=sub.contract_id, is_deleted=False)
    approved = ipcs.filter(status__in=[IPCStatus.APPROVED, IPCStatus.PAID])
    paid = ipcs.filter(status=IPCStatus.PAID)

    total_billed = float(approved.aggregate(t=Sum('gross_amount'))['t'] or 0)
    total_paid = float(paid.aggregate(t=Sum('net_amount'))['t'] or 0)

    from contracts.models import IPCDeduction

    retention = float(
        IPCDeduction.objects.filter(
            ipc__contract_id=sub.contract_id,
            deduction_type='retention',
            is_deleted=False,
        ).aggregate(t=Sum('amount'))['t'] or 0
    )

    contract = sub.contract
    advance_total = float(contract.effective_amount) * float(contract.advance_payment_pct or 0) / 100
    recovered = float(
        IPCDeduction.objects.filter(
            ipc__contract_id=sub.contract_id,
            deduction_type='advance_recovery',
            is_deleted=False,
        ).aggregate(t=Sum('amount'))['t'] or 0
    )

    return {
        'total_billed': total_billed,
        'total_paid': total_paid,
        'outstanding': total_billed - total_paid,
        'retention_held': retention,
        'advance_remaining': max(advance_total - recovered, 0),
    }


def compute_risk_flag(sub: Subcontractor) -> tuple[bool, list[str]]:
    reasons = []

    if sub.status == SubcontractorStatus.SUSPENDED:
        reasons.append('پیمانکار تعلیق شده است')

    latest = sub.scores.filter(is_deleted=False).order_by('-score_date').first()
    if latest and latest.overall_score is not None and float(latest.overall_score) < 6:
        reasons.append(f'آخرین نمره عملکرد ({latest.overall_score}) کمتر از ۶ است')

    if sub.warnings.filter(
        is_deleted=False,
        resolved=False,
        warning_type__in=[WarningType.WRITTEN, WarningType.FINAL, WarningType.CONTRACT_SUSPENSION],
    ).exists():
        reasons.append('اخطار کتبی یا نهایی حل‌نشده دارد')

    if sub.contract_id and sub.contract.finish_date:
        from schedule.models import ActivityProgress

        items = sub.contract.items.filter(is_deleted=False, activity_id__isnull=False)
        for item in items:
            prog = ActivityProgress.objects.filter(activity_id=item.activity_id).order_by('-report_date').first()
            if prog and float(prog.actual_progress or 0) < 85:
                planned_days = (sub.contract.finish_date - (sub.contract.start_date or date.today())).days or 1
                elapsed = (date.today() - (sub.contract.start_date or date.today())).days
                expected = min(100, elapsed / planned_days * 100) if planned_days > 0 else 100
                if float(prog.actual_progress or 0) < expected - 15:
                    reasons.append('پیشرفت بیش از ۱۵٪ از برنامه عقب است')
                    break

    return bool(reasons), reasons

"""Subcontractor risk and financial computation."""

from __future__ import annotations

from django.db.models import Sum

from contracts.models import IPC, IPCStatus
from subcontractors.models import Subcontractor, SubcontractorStatus, WarningType


def financial_summary(sub: Subcontractor) -> dict:
    empty = {
        'total_billed': 0,
        'total_paid': 0,
        'outstanding': 0,
        'retention_held': 0,
        'advance_paid': 0,
        'advance_recovered': 0,
        'advance_remaining': 0,
    }
    if not sub.contract_id:
        return empty

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
    advance_paid = contract.advance_amount
    advance_recovered = float(
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
        'advance_paid': advance_paid,
        'advance_recovered': advance_recovered,
        'advance_remaining': max(advance_paid - advance_recovered, 0),
    }


def compute_risk_flag(sub: Subcontractor) -> tuple[bool, list[str]]:
    reasons = []

    valid_scores = [s for s in sub.scores.all() if not s.is_deleted]
    latest = max(valid_scores, key=lambda x: x.score_date) if valid_scores else None
    if latest and latest.overall_score is not None and float(latest.overall_score) < 6:
        reasons.append('آخرین نمره عملکرد کمتر از 6 است')

    has_critical_warning = any(
        w.warning_type in [WarningType.WRITTEN, WarningType.FINAL, WarningType.CONTRACT_SUSPENSION]
        for w in sub.warnings.all()
        if not w.is_deleted and not w.resolved
    )
    if has_critical_warning:
        reasons.append('اخطار کتبی یا نهایی حل نشده دارد')

    if sub.status == SubcontractorStatus.SUSPENDED:
        reasons.append('وضعیت پیمانکار تعلیق است')

    if sub.contract_id:
        from schedule.models import ActivityProgress

        activity_ids = sub.contract.items.filter(
            is_deleted=False, activity_id__isnull=False
        ).values_list('activity_id', flat=True)

        if activity_ids:
            latest_progresses = (
                ActivityProgress.objects.filter(activity_id__in=activity_ids)
                .order_by('activity_id', '-report_date')
                .distinct('activity_id')
            )
            for prog in latest_progresses:
                planned = float(prog.planned_progress or 0)
                actual = float(prog.actual_progress or 0)
                if planned - actual > 0.15:
                    reasons.append('پیشرفت بیش از 15٪ از برنامه عقب است')
                    break

    return bool(reasons), reasons


def score_trend(sub: Subcontractor) -> str:
    scores = list(
        sub.scores.filter(is_deleted=False, overall_score__isnull=False)
        .order_by('-score_date')[:3]
    )
    if len(scores) < 2:
        return 'stable'
    newest = float(scores[0].overall_score)
    oldest = float(scores[-1].overall_score)
    if newest > oldest + 0.2:
        return 'improving'
    if newest < oldest - 0.2:
        return 'declining'
    return 'stable'


def average_overall_score(sub: Subcontractor) -> float | None:
    from django.db.models import Avg

    result = sub.scores.filter(is_deleted=False, overall_score__isnull=False).aggregate(
        avg=Avg('overall_score')
    )
    return float(result['avg']) if result['avg'] is not None else None

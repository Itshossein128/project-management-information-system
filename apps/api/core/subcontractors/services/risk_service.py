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


def _compute_risk_flag_with_data(sub: Subcontractor, latest_progresses_by_activity: dict, contract_items_by_contract: dict) -> tuple[bool, list[str]]:
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
        items = contract_items_by_contract.get(sub.contract_id)
        if items is None:
            # Fallback if not mapped (e.g., single sub call without prefetch)
            items = [item for item in sub.contract.items.all() if not item.is_deleted]

        activity_ids = [
            item.activity_id for item in items
            if not item.is_deleted and item.activity_id is not None
        ]

        if activity_ids:
            for act_id in activity_ids:
                prog = latest_progresses_by_activity.get(act_id)
                if prog:
                    planned = float(prog.planned_progress or 0)
                    actual = float(prog.actual_progress or 0)
                    if planned - actual > 0.15:
                        reasons.append('پیشرفت بیش از 15٪ از برنامه عقب است')
                        break

    return bool(reasons), reasons


def precalculate_risk_flags(subs: list[Subcontractor]) -> dict:
    from schedule.models import ActivityProgress
    from contracts.models import ContractItem

    activity_ids = set()
    contract_ids = {sub.contract_id for sub in subs if sub.contract_id}

    contract_items_by_contract = {}
    if contract_ids:
        items = ContractItem.objects.filter(contract_id__in=contract_ids, is_deleted=False)
        for item in items:
            contract_items_by_contract.setdefault(item.contract_id, []).append(item)
            if item.activity_id is not None:
                activity_ids.add(item.activity_id)

    latest_progresses_by_activity = {}
    if activity_ids:
        latest_progresses = (
            ActivityProgress.objects.filter(activity_id__in=activity_ids)
            .order_by('activity_id', '-report_date')
            .distinct('activity_id')
        )
        for prog in latest_progresses:
            latest_progresses_by_activity[prog.activity_id] = prog

    risk_map = {}
    for sub in subs:
        risk_map[sub.id] = _compute_risk_flag_with_data(sub, latest_progresses_by_activity, contract_items_by_contract)

    return risk_map


def compute_risk_flag(sub: Subcontractor) -> tuple[bool, list[str]]:
    if hasattr(sub, '_risk_cache'):
        return sub._risk_cache
    return precalculate_risk_flags([sub]).get(sub.id, (False, []))


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

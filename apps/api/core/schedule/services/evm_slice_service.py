"""Phase (WBS) and CBS EVM slice aggregation."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Sum

from cost_control.models import (
    ActualCost,
    Budget,
    BudgetLineLevel,
    CostBreakdownNode,
)
from projects.models import Activity, WBS
from schedule.services.evm_baseline import resolve_evm_baseline_validity
from schedule.services.evm_service import _build_indices, compute_evm
from schedule.services.evm_status import MEASURE_REGISTERED, MEASURE_UNREGISTERED, measure
from schedule.services.progress_service import get_approved_progress_for_activities


def _weighted_progress(activities: list[Activity], progress_map: dict) -> tuple[float | None, bool]:
    if not activities:
        return None, False
    total_weight = sum(float(a.weight or 0) for a in activities if a.weight is not None)
    if total_weight == 0:
        return None, False
    if not progress_map:
        return None, False
    weighted = 0.0
    for a in activities:
        if a.weight is None:
            continue
        weighted += float(a.weight) * float(progress_map.get(a.id, 0.0))
    return weighted / total_weight, True


def _planned_for_activities(activities: list[Activity], as_of: date) -> float:
    from schedule.models import ActivityProgress

    ids = [a.id for a in activities]
    if not ids:
        return 0.0
    total_weight = sum(float(a.weight or 0) for a in activities if a.weight is not None)
    if total_weight == 0:
        return 0.0
    progresses = (
        ActivityProgress.objects.filter(
            activity_id__in=ids,
            report_date__lte=as_of,
            planned_progress__isnull=False,
        )
        .order_by('activity_id', '-report_date')
        .distinct('activity_id')
    )
    pmap = {p.activity_id: float(p.planned_progress) for p in progresses}
    weighted = 0.0
    for a in activities:
        if a.weight is None:
            continue
        weighted += float(a.weight) * float(pmap.get(a.id, 0.0))
    return weighted / total_weight


def _slice_payload(
    *,
    bac: float,
    activities: list[Activity],
    as_of: date,
    ac_amount: float | None,
    ac_registered: bool,
    currency: str | None,
    currencies: set[str],
) -> dict[str, Any]:
    warnings: list[str] = []
    if len(currencies) > 1:
        warnings.append('mixed_currency')
        return {
            'bac': bac,
            'pv': measure(None, MEASURE_UNREGISTERED, currency=currency),
            'ev': measure(None, MEASURE_UNREGISTERED, currency=currency),
            'ac': measure(None, MEASURE_UNREGISTERED, currency=currency),
            'spi': {'value': None, 'status': 'not_computable', 'reason': 'mixed_currency'},
            'cpi': {'value': None, 'status': 'not_computable', 'reason': 'mixed_currency'},
            'eac': {'value': None, 'status': 'not_computable', 'reason': 'mixed_currency'},
            'etc': {'value': None, 'status': 'not_computable', 'reason': 'mixed_currency'},
            'vac': {'value': None, 'status': 'not_computable', 'reason': 'mixed_currency'},
            'aggregation': 'blocked',
            'warnings': warnings,
        }

    planned = _planned_for_activities(activities, as_of)
    if activities:
        pv_m = measure(bac * planned, MEASURE_REGISTERED, currency=currency)
    else:
        pv_m = measure(None, MEASURE_UNREGISTERED, currency=currency)

    ids = [a.id for a in activities]
    pmap, has_approved = get_approved_progress_for_activities(ids, as_of)
    ratio, ok = _weighted_progress(activities, pmap)
    if ok and has_approved and ratio is not None:
        ev_m = measure(bac * ratio, MEASURE_REGISTERED, currency=currency)
    else:
        ev_m = measure(None, MEASURE_UNREGISTERED, currency=currency)

    if ac_registered and ac_amount is not None:
        ac_m = measure(float(ac_amount), MEASURE_REGISTERED, currency=currency)
    else:
        ac_m = measure(None, MEASURE_UNREGISTERED, currency=currency)

    indices = _build_indices(bac=bac, pv_m=pv_m, ev_m=ev_m, ac_m=ac_m)
    return {
        'bac': bac,
        'pv': pv_m,
        'ev': ev_m,
        'ac': ac_m,
        'spi': indices['spi'],
        'cpi': indices['cpi'],
        'eac': indices['eac'],
        'etc': indices['etc'],
        'vac': indices['vac'],
        'sv': indices['sv'],
        'cv': indices['cv'],
        'warnings': warnings,
    }


def build_evm_by_phase(project_id, as_of: date) -> dict[str, Any]:
    baseline = resolve_evm_baseline_validity(project_id)
    budget_version = baseline.pop('budget_version', None)
    currency = baseline['budget_baseline'].get('currency')
    project_totals = compute_evm(project_id, as_of)

    # Phase candidates: WBS with phase-level budget lines, else top-level WBS children of roots
    phase_wbs_ids = set()
    budget_qs = Budget.objects.filter(project_id=project_id, is_deleted=False)
    if budget_version:
        budget_qs = budget_qs.filter(version_id=budget_version.id)
    for wbs_id in budget_qs.filter(level=BudgetLineLevel.PHASE, wbs_id__isnull=False).values_list(
        'wbs_id', flat=True
    ):
        phase_wbs_ids.add(wbs_id)

    if not phase_wbs_ids:
        roots = list(WBS.get_root_nodes().filter(project_id=project_id, is_deleted=False))
        for root in roots:
            children = list(root.get_children().filter(is_deleted=False))
            if children:
                phase_wbs_ids.update(c.id for c in children)
            else:
                phase_wbs_ids.add(root.id)

    phases = []
    for wbs in WBS.objects.filter(id__in=phase_wbs_ids, project_id=project_id, is_deleted=False):
        descendant_ids = [n.id for n in wbs.get_descendants() if not getattr(n, 'is_deleted', False)]
        descendant_ids.append(wbs.id)
        activities = list(
            Activity.objects.filter(
                project_id=project_id,
                wbs_id__in=descendant_ids,
                is_deleted=False,
                weight__isnull=False,
            )
        )
        bac_qs = budget_qs.filter(wbs_id__in=descendant_ids) | budget_qs.filter(
            activity__wbs_id__in=descendant_ids
        )
        bac = float(bac_qs.distinct().aggregate(total=Sum('budget_amount'))['total'] or 0)
        # Prefer explicit phase-level line amount when present
        phase_line = budget_qs.filter(level=BudgetLineLevel.PHASE, wbs_id=wbs.id).aggregate(
            total=Sum('budget_amount')
        )['total']
        if phase_line is not None:
            bac = float(phase_line)

        currencies = set()
        for c in bac_qs.values_list('currency', flat=True):
            if c:
                currencies.add(str(c).upper())
        if currency:
            currencies.add(str(currency).upper())

        ac_qs = ActualCost.objects.filter(
            project_id=project_id,
            cost_date__lte=as_of,
            is_deleted=False,
            wbs_id__in=descendant_ids,
        )
        ac_exists = ac_qs.exists()
        ac_amount = float(ac_qs.aggregate(total=Sum('amount'))['total'] or 0) if ac_exists else None

        slice_data = _slice_payload(
            bac=bac,
            activities=activities,
            as_of=as_of,
            ac_amount=ac_amount,
            ac_registered=ac_exists,
            currency=currency,
            currencies=currencies if bac or ac_exists else set(),
        )
        phases.append(
            {
                'wbs_id': str(wbs.id),
                'wbs_code': wbs.wbs_code,
                'wbs_name': wbs.wbs_name,
                **slice_data,
            }
        )

    control_bac = float(project_totals.get('bac') or 0)
    phase_bac_sum = sum(float(p.get('bac') or 0) for p in phases)
    roll_up = 'included' if abs(phase_bac_sum - control_bac) <= 0.01 else 'partial'
    for phase in phases:
        phase['roll_up'] = roll_up

    return {
        'as_of_date': as_of.strftime('%Y-%m-%d'),
        'validity': project_totals.get('validity'),
        'warnings': project_totals.get('warnings', []),
        'phases': phases,
        'project_totals': {
            'bac': project_totals.get('bac'),
            'pv': project_totals.get('pv'),
            'ev': project_totals.get('ev'),
            'ac': project_totals.get('ac'),
            'spi': project_totals.get('spi'),
            'cpi': project_totals.get('cpi'),
            'eac': project_totals.get('eac'),
            'etc': project_totals.get('etc'),
            'vac': project_totals.get('vac'),
        },
        'meta': {
            'phase_basis': 'wbs_phase_budget_or_subtree',
            'ac_allocation': 'direct_only',
        },
    }


def build_evm_by_cbs(project_id, as_of: date, root_id=None) -> dict[str, Any]:
    baseline = resolve_evm_baseline_validity(project_id)
    budget_version = baseline.pop('budget_version', None)
    currency = baseline['budget_baseline'].get('currency')
    project_totals = compute_evm(project_id, as_of)

    if root_id:
        root = CostBreakdownNode.objects.filter(
            pk=root_id, project_id=project_id, is_deleted=False
        ).first()
        if root:
            node_list = [root] + [
                n for n in root.get_descendants() if not getattr(n, 'is_deleted', False)
            ]
        else:
            node_list = []
    else:
        node_list = list(
            CostBreakdownNode.objects.filter(project_id=project_id, is_deleted=False).order_by('path')
        )

    budget_qs = Budget.objects.filter(project_id=project_id, is_deleted=False)
    if budget_version:
        budget_qs = budget_qs.filter(version_id=budget_version.id)

    nodes_out = []
    for node in node_list:
        desc = [n.id for n in node.get_descendants() if not getattr(n, 'is_deleted', False)]
        desc.append(node.id)
        bac = float(
            budget_qs.filter(cbs_id__in=desc).aggregate(total=Sum('budget_amount'))['total'] or 0
        )
        # Activities linked via budget lines on this CBS
        activity_ids = list(
            budget_qs.filter(cbs_id__in=desc, activity_id__isnull=False).values_list(
                'activity_id', flat=True
            )
        )
        activities = list(
            Activity.objects.filter(id__in=activity_ids, is_deleted=False, weight__isnull=False)
        )

        currencies = set()
        for c in budget_qs.filter(cbs_id__in=desc).values_list('currency', flat=True):
            if c:
                currencies.add(str(c).upper())

        ac_qs = ActualCost.objects.filter(
            project_id=project_id,
            cost_date__lte=as_of,
            is_deleted=False,
            cbs_id__in=desc,
        )
        ac_exists = ac_qs.exists()
        ac_amount = float(ac_qs.aggregate(total=Sum('amount'))['total'] or 0) if ac_exists else None
        for c in ac_qs.exclude(currency__isnull=True).values_list('currency', flat=True) if False else []:
            pass

        slice_data = _slice_payload(
            bac=bac,
            activities=activities,
            as_of=as_of,
            ac_amount=ac_amount,
            ac_registered=ac_exists,
            currency=currency,
            currencies=currencies if (bac or ac_exists) else set(),
        )
        depth = getattr(node, 'depth', 1) or 1
        nodes_out.append(
            {
                'cbs_id': str(node.id),
                'cbs_code': node.cbs_code,
                'cbs_name': node.cbs_name,
                'depth': depth,
                **slice_data,
                'children_roll_up': True,
            }
        )

    return {
        'as_of_date': as_of.strftime('%Y-%m-%d'),
        'validity': project_totals.get('validity'),
        'warnings': project_totals.get('warnings', []),
        'nodes': nodes_out,
        'project_totals': {
            'bac': project_totals.get('bac'),
            'pv': project_totals.get('pv'),
            'ev': project_totals.get('ev'),
            'ac': project_totals.get('ac'),
            'spi': project_totals.get('spi'),
            'cpi': project_totals.get('cpi'),
            'eac': project_totals.get('eac'),
            'etc': project_totals.get('etc'),
            'vac': project_totals.get('vac'),
        },
        'meta': {
            'ev_mapping': 'activities_via_cbs_budget_lines',
            'ac_mapping': 'actual_cost.cbs',
            'ac_allocation': 'direct_only',
        },
    }

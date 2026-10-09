"""Earned Value Management calculations."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Sum

from cost_control.models import ActualCost, Budget
from schedule.services.evm_baseline import resolve_evm_baseline_validity
from schedule.services.evm_status import (
    INDEX_COMPUTABLE,
    INDEX_NOT_COMPUTABLE,
    MEASURE_REGISTERED,
    MEASURE_UNREGISTERED,
    index,
    measure,
    not_computable,
)
from schedule.services.progress_service import (
    get_approved_progress_on_date,
    get_planned_progress_on_date,
    get_project_progress_on_date,
)

_INDEX_KEYS = frozenset({'sv', 'cv', 'spi', 'cpi', 'eac', 'etc', 'vac'})
_MEASURE_KEYS = frozenset({'pv', 'ev', 'ac'})


def evm_number(evm: dict, key: str) -> float | None:
    """Read legacy numeric or structured amount/value from an EVM payload."""
    legacy_key = f'{key}_legacy'
    if legacy_key in evm:
        return evm[legacy_key]
    value = evm.get(key)
    if isinstance(value, dict):
        if key in _INDEX_KEYS:
            return value.get('value')
        return value.get('amount')
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _bac_for_project(project_id, budget_version) -> tuple[float, str]:
    qs = Budget.objects.filter(project_id=project_id, is_deleted=False)
    if budget_version is not None:
        qs = qs.filter(version_id=budget_version.id)
        source = 'control_budget_version'
    else:
        source = 'project_budgets_fallback'
    total = qs.aggregate(total=Sum('budget_amount'))['total'] or 0
    return float(total), source


def _currencies_for_budgets(project_id, budget_version) -> set[str]:
    qs = Budget.objects.filter(project_id=project_id, is_deleted=False)
    if budget_version is not None:
        qs = qs.filter(version_id=budget_version.id)
    currencies = set()
    for row in qs.values_list('currency', 'version__currency'):
        c = (row[0] or row[1] or '').strip().upper()
        if c:
            currencies.add(c)
    return currencies


def _build_indices(
    *,
    bac: float,
    pv_m: dict,
    ev_m: dict,
    ac_m: dict,
) -> dict[str, Any]:
    pv_ok = pv_m['status'] == MEASURE_REGISTERED and pv_m['amount'] is not None
    ev_ok = ev_m['status'] == MEASURE_REGISTERED and ev_m['amount'] is not None
    ac_ok = ac_m['status'] == MEASURE_REGISTERED and ac_m['amount'] is not None

    if ev_ok and pv_ok:
        sv = index(float(ev_m['amount']) - float(pv_m['amount']), INDEX_COMPUTABLE, round_digits=None)
    else:
        reason = 'ev_unregistered' if not ev_ok else 'pv_unregistered'
        sv = not_computable(reason)

    if ev_ok and ac_ok:
        cv = index(float(ev_m['amount']) - float(ac_m['amount']), INDEX_COMPUTABLE, round_digits=None)
    else:
        reason = 'ev_unregistered' if not ev_ok else 'ac_unregistered'
        cv = not_computable(reason)

    if ev_ok and pv_ok and float(pv_m['amount']) != 0:
        spi = index(float(ev_m['amount']) / float(pv_m['amount']), INDEX_COMPUTABLE)
    else:
        if not ev_ok:
            reason = 'ev_unregistered'
        elif not pv_ok:
            reason = 'pv_unregistered'
        else:
            reason = 'pv_zero'
        spi = not_computable(reason)

    if ev_ok and ac_ok and float(ac_m['amount']) != 0:
        cpi = index(float(ev_m['amount']) / float(ac_m['amount']), INDEX_COMPUTABLE)
    else:
        if not ev_ok:
            reason = 'ev_unregistered'
        elif not ac_ok:
            reason = 'ac_unregistered'
        else:
            reason = 'ac_zero'
        cpi = not_computable(reason)

    if cpi['status'] == INDEX_COMPUTABLE and cpi['value'] and bac:
        eac_val = bac / float(cpi['value'])
        eac = index(eac_val, INDEX_COMPUTABLE, round_digits=None)
        etc = index(eac_val - float(ac_m['amount']), INDEX_COMPUTABLE, round_digits=None)
        vac = index(bac - eac_val, INDEX_COMPUTABLE, round_digits=None)
    else:
        eac = not_computable('cpi_not_computable')
        etc = not_computable('cpi_not_computable')
        vac = not_computable('cpi_not_computable')

    return {
        'sv': sv,
        'cv': cv,
        'spi': spi,
        'cpi': cpi,
        'eac': eac,
        'etc': etc,
        'vac': vac,
    }


def compute_evm(project_id, as_of_date: date) -> dict:
    baseline = resolve_evm_baseline_validity(project_id)
    budget_version = baseline.pop('budget_version', None)
    bac, bac_source = _bac_for_project(project_id, budget_version)
    currency = baseline['budget_baseline'].get('currency')

    currencies = _currencies_for_budgets(project_id, budget_version)
    warnings = list(baseline['warnings'])
    validity = baseline['validity']
    if len(currencies) > 1:
        warnings.append('mixed_currency')
        validity = 'invalid'

    planned_progress = get_planned_progress_on_date(project_id, as_of_date)
    actual_progress = get_project_progress_on_date(project_id, as_of_date)
    approved_ratio, has_approved = get_approved_progress_on_date(project_id, as_of_date)

    # PV: registered when there is planned work context (activities with weight);
    # amount may be 0.
    if bac == 0 and planned_progress == 0:
        # Distinguish: no budget and no plan → unregistered PV for ratios
        from projects.models import Activity

        has_weighted = Activity.objects.filter(
            project_id=project_id, is_deleted=False, weight__isnull=False
        ).exists()
        if has_weighted:
            pv_m = measure(float(bac) * planned_progress, MEASURE_REGISTERED, currency=currency)
        else:
            pv_m = measure(None, MEASURE_UNREGISTERED, currency=currency)
    else:
        pv_m = measure(float(bac) * planned_progress, MEASURE_REGISTERED, currency=currency)

    if has_approved and approved_ratio is not None:
        ev_m = measure(float(bac) * approved_ratio, MEASURE_REGISTERED, currency=currency)
        approved_progress_pct = round(approved_ratio * 100, 2)
    else:
        ev_m = measure(None, MEASURE_UNREGISTERED, currency=currency)
        approved_progress_pct = None

    ac_qs = ActualCost.objects.filter(
        project_id=project_id,
        cost_date__lte=as_of_date,
        is_deleted=False,
    )
    if not ac_qs.exists():
        ac_m = measure(None, MEASURE_UNREGISTERED, currency=currency)
        ac_legacy = 0.0
    else:
        ac_total = float(ac_qs.aggregate(total=Sum('amount'))['total'] or 0)
        ac_m = measure(ac_total, MEASURE_REGISTERED, currency=currency)
        ac_legacy = ac_total

    if len(currencies) > 1:
        # Block aggregated money measures
        for m in (pv_m, ev_m, ac_m):
            if m['status'] == MEASURE_REGISTERED:
                m['amount'] = None
                m['status'] = MEASURE_UNREGISTERED
        warnings = list(dict.fromkeys(warnings + ['mixed_currency']))

    indices = _build_indices(bac=bac, pv_m=pv_m, ev_m=ev_m, ac_m=ac_m)

    ev_legacy = float(ev_m['amount']) if ev_m['amount'] is not None else 0.0
    pv_legacy = float(pv_m['amount']) if pv_m['amount'] is not None else 0.0

    return {
        'as_of_date': as_of_date.strftime('%Y-%m-%d'),
        'scope_type': 'project',
        'validity': validity,
        'warnings': warnings,
        'schedule_baseline': baseline['schedule_baseline'],
        'budget_baseline': baseline['budget_baseline'],
        'bac': bac,
        'pv': pv_m,
        'ev': ev_m,
        'ac': ac_m,
        'sv': indices['sv'],
        'cv': indices['cv'],
        'spi': indices['spi'],
        'cpi': indices['cpi'],
        'eac': indices['eac'],
        'etc': indices['etc'],
        'vac': indices['vac'],
        'ev_legacy': ev_legacy,
        'pv_legacy': pv_legacy,
        'ac_legacy': ac_legacy,
        'spi_legacy': indices['spi']['value'],
        'cpi_legacy': indices['cpi']['value'],
        'eac_legacy': indices['eac']['value'],
        'etc_legacy': indices['etc']['value'],
        'vac_legacy': indices['vac']['value'],
        'sv_legacy': indices['sv']['value'],
        'cv_legacy': indices['cv']['value'],
        'actual_progress_pct': round(actual_progress * 100, 2),
        'planned_progress_pct': round(planned_progress * 100, 2),
        'approved_progress_pct': approved_progress_pct,
        'schedule_variance_pct': round((actual_progress - planned_progress) * 100, 2),
        'budget_consumption_pct': round(ac_legacy / float(bac) * 100, 2) if bac else None,
        'meta': {
            'eac_method': 'bac_over_cpi',
            'ev_basis': 'approved_progress',
            'bac_source': bac_source,
        },
    }

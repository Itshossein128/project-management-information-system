"""Monte Carlo profit simulation."""

from __future__ import annotations

from datetime import date

import numpy as np
from django.db.models import Sum

from contracts.models import Contract, ContractType
from cost_control.models import ActualCost
from economic.models import SimulationResult
from economic.services.snapshot_service import generate_snapshot
from schedule.services.evm_service import compute_evm

DEFAULT_PARAMS = {
    'inflation_rate_mean': 0.30,
    'inflation_rate_std': 0.10,
    'payment_delay_mean': 45,
    'payment_delay_std': 20,
    'productivity_factor_mean': 1.0,
    'productivity_factor_std': 0.15,
    'cost_overrun_mean': 1.05,
    'cost_overrun_std': 0.10,
}


def run_monte_carlo(project_id, iterations=5000, scenario_params=None) -> dict:
    params = {**DEFAULT_PARAMS, **(scenario_params or {})}
    generate_snapshot(project_id)

    base_cost = float(
        ActualCost.objects.filter(project_id=project_id, is_deleted=False).aggregate(t=Sum('amount'))['t'] or 0
    )
    evm = compute_evm(project_id, date.today())
    eac = float(evm.get('eac') or base_cost * 1.1)

    main_contract = Contract.objects.filter(
        project_id=project_id, contract_type=ContractType.MAIN, is_deleted=False
    ).first()
    revenue = float(main_contract.adjusted_amount or main_contract.original_amount or 0) if main_contract else eac

    n = int(iterations)
    rng = np.random.default_rng()

    inflation = rng.normal(params['inflation_rate_mean'], params['inflation_rate_std'], n).clip(0, None)
    delay = rng.normal(params['payment_delay_mean'], params['payment_delay_std'], n).clip(0, None)
    overrun = rng.normal(params['cost_overrun_mean'], params['cost_overrun_std'], n).clip(0.5, 2.0)
    productivity = rng.normal(
        params['productivity_factor_mean'], params['productivity_factor_std'], n
    ).clip(0.3, 2.0)

    adjusted_cost = eac * overrun * (1 + inflation) / productivity
    financing = revenue * 0.28 * delay / 365
    profit = revenue - adjusted_cost - financing

    payment_ratio = np.clip(1.0 - delay / 365.0, 0.05, 1.0)
    working_capital = np.maximum(adjusted_cost - revenue * payment_ratio, 0.0)
    max_wc_p90 = float(np.percentile(working_capital, 90))

    p10 = float(np.percentile(profit, 10))
    p50 = float(np.percentile(profit, 50))
    p90 = float(np.percentile(profit, 90))
    prob_loss = float(np.mean(profit < 0))

    sensitivity = []
    base_profit = (
        revenue
        - eac * params['cost_overrun_mean'] * (1 + params['inflation_rate_mean']) / params['productivity_factor_mean']
        - revenue * 0.28 * params['payment_delay_mean'] / 365
    )

    def quick_profit(p):
        prod = max(float(p['productivity_factor_mean']), 0.3)
        c = eac * p['cost_overrun_mean'] * (1 + p['inflation_rate_mean']) / prod
        f = revenue * 0.28 * p['payment_delay_mean'] / 365
        return revenue - c - f

    for var_name, mean_key, std_key in [
        ('تورم', 'inflation_rate_mean', 'inflation_rate_std'),
        ('تأخیر پرداخت', 'payment_delay_mean', 'payment_delay_std'),
        ('اضافه هزینه', 'cost_overrun_mean', 'cost_overrun_std'),
        ('بهره‌وری', 'productivity_factor_mean', 'productivity_factor_std'),
    ]:
        low_param = {**params, mean_key: params[mean_key] - params[std_key]}
        high_param = {**params, mean_key: params[mean_key] + params[std_key]}
        sensitivity.append({
            'variable': var_name,
            'low_profit': quick_profit(low_param),
            'high_profit': quick_profit(high_param),
            'impact': abs(quick_profit(high_param) - quick_profit(low_param)),
        })
    sensitivity.sort(key=lambda x: x['impact'], reverse=True)

    SimulationResult.objects.create(
        project_id=project_id,
        iterations=n,
        p10_profit=p10,
        p50_profit=p50,
        p90_profit=p90,
        prob_of_loss=prob_loss,
        max_working_capital=max_wc_p90,
        sensitivity_json=sensitivity,
        scenario_params_json=params,
    )

    return {
        'p10': p10,
        'p50': p50,
        'p90': p90,
        'prob_of_loss': prob_loss,
        'max_working_capital': max_wc_p90,
        'sensitivity': sensitivity,
        'iterations': n,
        'base_profit': base_profit,
    }

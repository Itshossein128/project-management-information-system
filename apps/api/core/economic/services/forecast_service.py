"""Inflation-adjusted EAC forecast."""

from __future__ import annotations

from datetime import date

from economic.services.inflation_service import compute_total_inflation_adjusted_cost
from schedule.services.evm_service import compute_evm


def compute_economic_forecast(project_id, as_of_date=None) -> dict:
    as_of = as_of_date or date.today()
    evm = compute_evm(project_id, as_of)

    actual_cost = float(evm.get('ac') or 0)
    inflation_adj_cost = compute_total_inflation_adjusted_cost(project_id, as_of)
    inflation_factor = inflation_adj_cost / actual_cost if actual_cost > 0 else 1.0

    etc = evm.get('etc')
    eac_nominal = evm.get('eac')
    if etc is not None and actual_cost > 0:
        eac_inflation_adjusted = actual_cost + float(etc) * inflation_factor
    elif eac_nominal is not None:
        eac_inflation_adjusted = float(eac_nominal) * inflation_factor
    else:
        eac_inflation_adjusted = inflation_adj_cost

    return {
        'as_of_date': evm.get('as_of_date'),
        'bac': evm.get('bac'),
        'ev': evm.get('ev'),
        'pv': evm.get('pv'),
        'ac': actual_cost,
        'sv': evm.get('sv'),
        'cv': evm.get('cv'),
        'spi': evm.get('spi'),
        'cpi': evm.get('cpi'),
        'eac_nominal': eac_nominal,
        'eac_inflation_adjusted': round(eac_inflation_adjusted, 2) if eac_inflation_adjusted else None,
        'etc_to_complete': etc,
        'vac': evm.get('vac'),
        'inflation_factor': round(inflation_factor, 4),
        'actual_progress_pct': evm.get('actual_progress_pct'),
        'planned_progress_pct': evm.get('planned_progress_pct'),
    }

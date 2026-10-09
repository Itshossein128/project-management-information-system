"""Inflation-adjusted EAC forecast."""

from __future__ import annotations

from datetime import date

from economic.services.inflation_service import compute_total_inflation_adjusted_cost
from schedule.services.evm_service import compute_evm, evm_number


def compute_economic_forecast(project_id, as_of_date=None) -> dict:
    as_of = as_of_date or date.today()
    evm = compute_evm(project_id, as_of)

    actual_cost = float(evm_number(evm, 'ac') or 0)
    inflation_adj_cost = compute_total_inflation_adjusted_cost(project_id, as_of)
    inflation_factor = inflation_adj_cost / actual_cost if actual_cost > 0 else 1.0

    etc = evm_number(evm, 'etc')
    eac_nominal = evm_number(evm, 'eac')
    if etc is not None and actual_cost > 0:
        eac_inflation_adjusted = actual_cost + float(etc) * inflation_factor
    elif eac_nominal is not None:
        eac_inflation_adjusted = float(eac_nominal) * inflation_factor
    else:
        eac_inflation_adjusted = inflation_adj_cost

    return {
        'as_of_date': evm.get('as_of_date'),
        'bac': evm.get('bac'),
        'ev': evm_number(evm, 'ev'),
        'pv': evm_number(evm, 'pv'),
        'ac': actual_cost,
        'sv': evm_number(evm, 'sv'),
        'cv': evm_number(evm, 'cv'),
        'spi': evm_number(evm, 'spi'),
        'cpi': evm_number(evm, 'cpi'),
        'eac_nominal': eac_nominal,
        'eac_inflation_adjusted': round(eac_inflation_adjusted, 2) if eac_inflation_adjusted else None,
        'etc_to_complete': etc,
        'vac': evm_number(evm, 'vac'),
        'inflation_factor': round(inflation_factor, 4),
        'actual_progress_pct': evm.get('actual_progress_pct'),
        'planned_progress_pct': evm.get('planned_progress_pct'),
    }

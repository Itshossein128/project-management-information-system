"""Pure AHP criteria weighting service (doc 05).

Computes criteria weights from pairwise comparisons using the geometric mean method
and calculates Saaty's consistency ratio (CR). Pure Python — no Django/DB/view math.
"""

from __future__ import annotations

import math
from typing import Any

from decision_support.services.validators import validate_ahp_inputs

# Standard Saaty Random Index table for n in [1, 10]
SAATY_RI: dict[int, float] = {
    1: 0.0,
    2: 0.0,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}


def compute_ahp(
    criteria: list[Any],
    ahp_matrix: list[Any],
) -> dict[str, Any]:
    """Calculate normalized weights and consistency ratio from pairwise comparisons (AC17, AC18)."""
    cleaned = validate_ahp_inputs(criteria, ahp_matrix)
    crit: list[str] = cleaned['criteria']
    matrix: list[list[float]] = cleaned['ahp_matrix']
    n = len(crit)

    if n == 1:
        return {
            'weights': [
                {
                    'criterion': crit[0],
                    'weight': 1.0,
                    'rank': 1,
                },
            ],
            'lambda_max': 1.0,
            'ci': 0.0,
            'cr': 0.0,
            'is_consistent': True,
        }

    # 1. Row geometric mean: g_j = (product_k a_{j,k}) ** (1 / n)
    geom_means: list[float] = []
    for row in matrix:
        prod = 1.0
        for val in row:
            prod *= val
        geom_means.append(prod ** (1.0 / n))

    sum_geom = sum(geom_means)
    # Normalized weights
    raw_weights = [g / sum_geom for g in geom_means]

    # 2. Principal eigenvalue estimation: lambda_max = (1/n) * sum_j ((A * w)_j / w_j)
    weighted_sums: list[float] = []
    for j in range(n):
        row_sum = sum(matrix[j][k] * raw_weights[k] for k in range(n))
        weighted_sums.append(row_sum)

    ratios = [weighted_sums[j] / raw_weights[j] for j in range(n)]
    lambda_max = sum(ratios) / n

    # 3. Consistency Index (CI) and Consistency Ratio (CR)
    ci = max(0.0, (lambda_max - n) / (n - 1.0))
    ri = SAATY_RI.get(n, 1.49)
    if ri == 0.0:
        cr = 0.0
    else:
        cr = ci / ri

    is_consistent = cr <= 0.10

    # 4. Form ordinal ranked weights output (stable sort by weight descending, input order tie-breaker)
    indexed = [(raw_weights[j], j, crit[j]) for j in range(n)]
    indexed.sort(key=lambda item: (-item[0], item[1]))

    weights_output = [
        {
            'criterion': name,
            'weight': w,
            'rank': rank,
        }
        for rank, (w, _, name) in enumerate(indexed, start=1)
    ]

    return {
        'weights': weights_output,
        'lambda_max': lambda_max,
        'ci': ci,
        'cr': cr,
        'is_consistent': is_consistent,
    }

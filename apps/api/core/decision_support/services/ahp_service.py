"""Pure AHP criteria weighting service (doc 05).

Computes criteria weights from pairwise comparisons using the geometric mean method
and calculates Saaty's consistency ratio (CR). Pure Python — no Django/DB/view math.
"""

from __future__ import annotations

import math
from typing import Any

from decision_support.services.validators import validate_ahp_inputs, raise_issues, _issue

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

    # Log-domain geometric means avoid overflowing representable row products.
    log_means = [math.fsum(math.log(value) for value in row) / n for row in matrix]
    offset = max(log_means)
    geom_means = [math.exp(value - offset) for value in log_means]
    sum_geom = math.fsum(geom_means)
    raw_weights = [value / sum_geom for value in geom_means]

    if any(not math.isfinite(weight) or weight <= 0 for weight in raw_weights):
        raise_issues([_issue('non_finite', 'ahp_matrix', 'AHP calculation must be finite.')])

    # 2. Principal eigenvalue estimation: lambda_max = (1/n) * sum_j ((A * w)_j / w_j)
    weighted_sums: list[float] = []
    for j in range(n):
        row_sum = sum(matrix[j][k] * raw_weights[k] for k in range(n))
        weighted_sums.append(row_sum)

    ratios = [weighted_sums[j] / raw_weights[j] for j in range(n)]
    # Scale before summation. A ratio may overflow even when its mean contribution
    # is representable; in that case divide the numerator before the weight.
    mean_terms = [
        ratio / n if math.isfinite(ratio) else (weighted_sums[j] / n) / raw_weights[j]
        for j, ratio in enumerate(ratios)
    ]
    try:
        lambda_max = math.fsum(mean_terms)
    except OverflowError:
        raise_issues([_issue('non_finite', 'ahp_matrix', 'AHP calculation must be finite.')])

    # 3. Consistency Index (CI) and Consistency Ratio (CR)
    ci = max(0.0, (lambda_max - n) / (n - 1.0))
    ri = SAATY_RI[n]
    if ri == 0.0:
        cr = 0.0
    else:
        cr = ci / ri

    if any(not math.isfinite(value) for value in (lambda_max, ci, cr)):
        raise_issues([_issue('non_finite', 'ahp_matrix', 'AHP calculation must be finite.')])
    is_consistent = cr <= 0.10

    # Store named rows in input order; rank is an independent ordinal.
    ordered = sorted(range(n), key=lambda index: (-raw_weights[index], index))
    ranks = {index: rank for rank, index in enumerate(ordered, start=1)}
    weights_output = [
        {'criterion': name, 'weight': raw_weights[index], 'rank': ranks[index]}
        for index, name in enumerate(crit)
    ]

    return {
        'weights': weights_output,
        'lambda_max': lambda_max,
        'ci': ci,
        'cr': cr,
        'is_consistent': is_consistent,
    }

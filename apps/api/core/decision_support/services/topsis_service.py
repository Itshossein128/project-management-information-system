"""Pure TOPSIS ranking engine (doc 04 / sample TOPSIS path). No HTTP; ranking-only."""

from __future__ import annotations

from math import sqrt
from typing import Any

from config.exceptions import CodedValidationError
from decision_support.services.validators import _issue, raise_issues, validate_ranking_inputs
from decision_support.services.weights import normalize_weights


def _check_topsis_denominators(x: list[list[float]], n: int, m: int) -> list[dict[str, str]]:
    """Guard: vector-normalization denom = sqrt(Σ x[i,j]²) must be > 0 for every column."""
    issues: list[dict[str, str]] = []
    for j in range(n):
        col_sq_sum = sum(x[i][j] ** 2 for i in range(m))
        if col_sq_sum == 0.0:
            issues.append(
                _issue(
                    'topsis_denom_zero',
                    f'criteria.{j}',
                    'TOPSIS normalization denominator is zero: all values in this column are zero.',
                ),
            )
    return issues


def compute_topsis(
    criteria: list[Any],
    alternatives: list[Any],
    weights: list[Any],
    types: list[Any],
    matrix: list[Any],
) -> dict[str, Any]:
    """
    Independent TOPSIS calculation.

    Returns:
      {
        "ranking": [
          {
            "option": str,
            "d_best": float,
            "d_worst": float,
            "closeness": float,
            "score": float,
            "rank": int,
          },
          ...
        ],
        "weights_normalized": [float, ...],
      }
    """
    try:
        validated = validate_ranking_inputs(criteria, alternatives, weights, types, matrix)
    except CodedValidationError as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        issues = detail.get('issues', [])
        mapped: list[dict[str, str]] = []
        for iss in issues:
            code = iss.get('code')
            if str(code) == 'benefit_column_all_zero':
                mapped.append(
                    _issue(
                        'topsis_denom_zero',
                        str(iss.get('path', '')),
                        'TOPSIS normalization denominator is zero: all values in this column are zero.',
                    )
                )
            else:
                mapped.append(iss)
        raise_issues(mapped)

    crit = validated['criteria']
    alts = validated['alternatives']
    raw_weights = validated['weights']
    type_list = validated['types']
    x = validated['performance_matrix']

    m = len(alts)
    n = len(crit)

    # Engine guard: vector-normalization denominator cannot be zero (FR-004)
    denom_issues = _check_topsis_denominators(x, n, m)
    raise_issues(denom_issues)

    w = normalize_weights(raw_weights)

    # Vector normalization and weighting: v[i][j] = w[j] * x[i][j] / sqrt(sum_i(x[i][j]^2))
    v = [[0.0] * n for _ in range(m)]
    for j in range(n):
        denom = sqrt(sum(x[i][j] ** 2 for i in range(m)))
        for i in range(m):
            v[i][j] = (x[i][j] / denom) * w[j]

    # Identify ideal best and ideal worst solutions
    ideal_best = [0.0] * n
    ideal_worst = [0.0] * n
    for j in range(n):
        col_values = [v[i][j] for i in range(m)]
        if type_list[j] == 'benefit':
            ideal_best[j] = max(col_values)
            ideal_worst[j] = min(col_values)
        else:
            ideal_best[j] = min(col_values)
            ideal_worst[j] = max(col_values)

    # Euclidean distances to ideal best and worst
    d_best = [0.0] * m
    d_worst = [0.0] * m
    closeness = [0.0] * m
    for i in range(m):
        d_best[i] = sqrt(sum((v[i][j] - ideal_best[j]) ** 2 for j in range(n)))
        d_worst[i] = sqrt(sum((v[i][j] - ideal_worst[j]) ** 2 for j in range(n)))
        total_dist = d_best[i] + d_worst[i]
        closeness[i] = d_worst[i] / total_dist if total_dist > 0.0 else 0.5

    # Stable sort: closeness descending, preserve input alternative order on ties
    indexed = list(enumerate(closeness))
    indexed.sort(key=lambda pair: (-pair[1], pair[0]))

    ranking = []
    for rank_pos, (orig_i, score_val) in enumerate(indexed, start=1):
        ranking.append(
            {
                'option': alts[orig_i],
                'd_best': d_best[orig_i],
                'd_worst': d_worst[orig_i],
                'closeness': score_val,
                'score': score_val,
                'rank': rank_pos,
            },
        )

    return {
        'ranking': ranking,
        'weights_normalized': w,
    }

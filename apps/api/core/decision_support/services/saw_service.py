"""Pure SAW ranking engine (doc 03 / sample SAW path). No HTTP; ranking-only."""

from __future__ import annotations

from typing import Any

from decision_support.services.validators import _issue, raise_issues, validate_ranking_inputs
from decision_support.services.weights import normalize_weights


def compute_saw(
    criteria: list[Any],
    alternatives: list[Any],
    weights: list[Any],
    types: list[Any],
    matrix: list[Any],
) -> dict[str, Any]:
    """
    Independent SAW calculation.

    Returns:
      {
        "ranking": [{"option": str, "score": float, "rank": int}, ...],  # score-desc, stable ties, ordinal rank
        "weights_normalized": [float, ...],
      }
    """
    validated = validate_ranking_inputs(criteria, alternatives, weights, types, matrix)
    crit = validated['criteria']
    alts = validated['alternatives']
    raw_weights = validated['weights']
    type_list = validated['types']
    x = validated['performance_matrix']

    m = len(alts)
    n = len(crit)

    # Engine guards (AC09/AC10/AC13) — validate_ranking_inputs already covers most;
    # re-check cost zeros and benefit columns for defense in depth.
    issues: list[dict[str, str]] = []
    for j in range(n):
        if type_list[j] == 'cost':
            for i in range(m):
                if x[i][j] <= 0:
                    issues.append(
                        _issue(
                            'cost_zero',
                            f'performance_matrix.{i}.{j}',
                            'Cost criterion cell must be greater than zero.',
                        ),
                    )
        else:
            col = [x[i][j] for i in range(m)]
            if all(v == 0 for v in col):
                issues.append(
                    _issue(
                        'benefit_column_all_zero',
                        f'criteria.{j}',
                        'Benefit criterion column cannot be all zeros.',
                    ),
                )
    if any(w < 0 for w in raw_weights):
        for j, w in enumerate(raw_weights):
            if w < 0:
                issues.append(
                    _issue('weight_negative', f'weights.{j}', 'Weight cannot be negative.'),
                )
    if sum(raw_weights) <= 0:
        issues.append(_issue('weights_all_zero', 'weights', 'Weight sum must be positive.'))
    raise_issues(issues)

    w = normalize_weights(raw_weights)
    scores = [0.0] * m
    for j in range(n):
        col = [x[i][j] for i in range(m)]
        if type_list[j] == 'benefit':
            largest = max(col)
            normalized = [v / largest for v in col]
        else:
            smallest = min(col)
            normalized = [smallest / v for v in col]
        for i in range(m):
            scores[i] += w[j] * normalized[i]

    # Stable sort: score descending, preserve input order on ties
    indexed = list(enumerate(scores))
    indexed.sort(key=lambda pair: (-pair[1], pair[0]))

    ranking = []
    for rank_pos, (orig_i, score) in enumerate(indexed, start=1):
        ranking.append(
            {
                'option': alts[orig_i],
                'score': score,
                'rank': rank_pos,
            },
        )

    return {
        'ranking': ranking,
        'weights_normalized': w,
    }

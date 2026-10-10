"""Shared decision-input contract validators (doc 02). Pure — no HTTP."""

from __future__ import annotations

import math
from typing import Any

from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError

from decision_support.models import METHOD_IDS

MAX_DIM = 10
VALID_TYPES = frozenset({'benefit', 'cost'})


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {'code': code, 'path': path, 'message': _(message)}


def raise_issues(issues: list[dict[str, str]]) -> None:
    if not issues:
        return
    raise CodedValidationError(
        detail={'issues': issues},
        code='decision_input_invalid',
    )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_non_finite(value: float) -> bool:
    return math.isnan(value) or math.isinf(value)


def validate_method_ids(methods: list[Any]) -> list[str]:
    issues: list[dict[str, str]] = []
    cleaned: list[str] = []
    seen: set[str] = set()
    if not isinstance(methods, list):
        raise_issues([_issue('invalid_type', 'selected_methods', 'Must be a list of method ids.')])
    for i, raw in enumerate(methods):
        mid = str(raw).strip() if raw is not None else ''
        if mid not in METHOD_IDS:
            issues.append(
                _issue('invalid_method', f'selected_methods.{i}', f'Unknown method id: {raw!r}.'),
            )
            continue
        if mid not in seen:
            seen.add(mid)
            cleaned.append(mid)
    raise_issues(issues)
    return cleaned


def validate_names(names: list[Any], field: str, *, require_non_empty: bool = False) -> list[str]:
    """Trim, reject empty, exact uniqueness, max 10 (O04 interim)."""
    issues: list[dict[str, str]] = []
    if not isinstance(names, list):
        raise_issues([_issue('invalid_type', field, f'{field} must be a list of names.')])

    if len(names) > MAX_DIM:
        issues.append(
            _issue('dimension_invalid', field, f'{field} must have at most {MAX_DIM} names.'),
        )

    cleaned: list[str] = []
    seen: dict[str, int] = {}
    for i, raw in enumerate(names):
        if raw is None:
            text = ''
        else:
            text = str(raw).strip()
        path = f'{field}.{i}'
        if not text:
            issues.append(_issue('name_empty', path, 'Name cannot be empty.'))
            continue
        if text in seen:
            issues.append(_issue('name_duplicate', path, 'Name must be unique within the list.'))
            continue
        seen[text] = i
        cleaned.append(text)

    if require_non_empty and len(cleaned) < 1 and not any(i['code'] == 'dimension_invalid' for i in issues):
        issues.append(_issue('dimension_invalid', field, f'{field} must have at least 1 name.'))

    raise_issues(issues)
    return cleaned


def validate_criteria_only(criteria: list[Any]) -> list[str]:
    return validate_names(criteria, 'criteria', require_non_empty=True)


def validate_ranking_inputs(
    criteria: list[Any],
    alternatives: list[Any],
    weights: list[Any],
    types: list[Any],
    matrix: list[Any],
) -> dict[str, Any]:
    """Full ranking contract (AC05–AC12). Raises CodedValidationError with issues."""
    issues: list[dict[str, str]] = []

    # Names first (collect without raising until end where possible)
    try:
        crit = validate_names(criteria, 'criteria', require_non_empty=True)
    except CodedValidationError as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        issues.extend(detail.get('issues', []))
        crit = []

    try:
        alts = validate_names(alternatives, 'alternatives', require_non_empty=True)
    except CodedValidationError as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        issues.extend(detail.get('issues', []))
        alts = []

    n = len(crit)
    m = len(alts)

    if n > MAX_DIM:
        issues.append(_issue('dimension_invalid', 'criteria', f'n must be <= {MAX_DIM}.'))
    if m > MAX_DIM:
        issues.append(_issue('dimension_invalid', 'alternatives', f'm must be <= {MAX_DIM}.'))
    if n == 0:
        issues.append(_issue('dimension_invalid', 'criteria', 'n must be >= 1 for ranking.'))
    if m == 0:
        issues.append(_issue('dimension_invalid', 'alternatives', 'm must be >= 1 for ranking.'))

    if not isinstance(weights, list):
        issues.append(_issue('length_mismatch', 'weights', 'weights must be a list.'))
        weights = []
    if not isinstance(types, list):
        issues.append(_issue('length_mismatch', 'types', 'types must be a list.'))
        types = []
    if not isinstance(matrix, list):
        issues.append(_issue('matrix_shape', 'performance_matrix', 'matrix must be a list of rows.'))
        matrix = []

    if n > 0 and len(weights) != n:
        issues.append(
            _issue('length_mismatch', 'weights', f'weights length must equal n={n}.'),
        )
    if n > 0 and len(types) != n:
        issues.append(
            _issue('length_mismatch', 'types', f'types length must equal n={n}.'),
        )

    cleaned_types: list[str] = []
    for j, t in enumerate(types):
        ts = str(t).strip() if t is not None else ''
        if ts not in VALID_TYPES:
            issues.append(
                _issue('invalid_type', f'types.{j}', 'Type must be benefit or cost.'),
            )
            cleaned_types.append(ts)
        else:
            cleaned_types.append(ts)

    cleaned_weights: list[float] = []
    for j, w in enumerate(weights):
        path = f'weights.{j}'
        if w is None or (isinstance(w, str) and not str(w).strip()):
            issues.append(_issue('non_numeric', path, 'Weight cannot be empty.'))
            continue
        try:
            wf = float(w)
        except (TypeError, ValueError):
            issues.append(_issue('non_numeric', path, 'Weight must be a finite number.'))
            continue
        if _is_non_finite(wf):
            issues.append(_issue('non_finite', path, 'Weight must be finite.'))
            continue
        if wf < 0:
            issues.append(_issue('weight_negative', path, 'Weight cannot be negative.'))
            continue
        cleaned_weights.append(wf)

    if cleaned_weights and all(w == 0 for w in cleaned_weights) and len(cleaned_weights) == len(weights):
        issues.append(_issue('weights_all_zero', 'weights', 'Weight sum must be positive.'))

    if m > 0 and n > 0:
        if len(matrix) != m:
            issues.append(
                _issue(
                    'matrix_shape',
                    'performance_matrix',
                    f'matrix must have exactly m={m} rows.',
                ),
            )

    cleaned_matrix: list[list[float]] = []
    for i, row in enumerate(matrix):
        row_path = f'performance_matrix.{i}'
        if not isinstance(row, list):
            issues.append(_issue('matrix_shape', row_path, 'Row must be a list.'))
            continue
        if n > 0 and len(row) != n:
            issues.append(
                _issue('length_mismatch', row_path, f'Row must have exactly n={n} cells.'),
            )
        cleaned_row: list[float] = []
        for j, cell in enumerate(row):
            cell_path = f'performance_matrix.{i}.{j}'
            if cell is None or (isinstance(cell, str) and not str(cell).strip()):
                issues.append(_issue('empty_cell', cell_path, 'Cell cannot be empty.'))
                continue
            if isinstance(cell, str):
                try:
                    cf = float(cell)
                except ValueError:
                    issues.append(_issue('non_numeric', cell_path, 'Cell must be numeric.'))
                    continue
            elif _is_number(cell):
                cf = float(cell)
            else:
                issues.append(_issue('non_numeric', cell_path, 'Cell must be numeric.'))
                continue
            if _is_non_finite(cf):
                issues.append(_issue('non_finite', cell_path, 'Cell must be finite.'))
                continue
            if cf < 0:
                issues.append(_issue('negative_value', cell_path, 'Cell cannot be negative.'))
                continue
            if j < len(cleaned_types) and cleaned_types[j] == 'cost' and cf == 0:
                issues.append(_issue('cost_zero', cell_path, 'Cost criterion cell cannot be zero.'))
                continue
            cleaned_row.append(cf)
        cleaned_matrix.append(cleaned_row)

    raise_issues(issues)
    return {
        'criteria': crit,
        'alternatives': alts,
        'weights': cleaned_weights,
        'types': cleaned_types,
        'performance_matrix': cleaned_matrix,
    }

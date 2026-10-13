"""Shared decision-input contract validators (doc 02). Pure — no HTTP."""

from __future__ import annotations

import math
from typing import Any

from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError

from decision_support.models import METHOD_IDS

MAX_DIM = 10
VALID_TYPES = frozenset({'benefit', 'cost'})


def validate_ism_inputs(criteria: Any, matrix: Any) -> dict[str, Any]:
    """Strict binary execution boundary, independent of ranking and other methods."""
    issues = []
    try:
        if isinstance(criteria, list):
            raise_issues([
                _issue('invalid_type', f'criteria.{i}', 'Criterion must be a string.')
                for i, name in enumerate(criteria) if not isinstance(name, str)
            ])
        names = validate_names(criteria, 'criteria', require_non_empty=True)
    except CodedValidationError as error:
        issues.extend(error.detail.get('issues', []))
        names = []
    n = len(names)
    if not isinstance(matrix, list):
        issues.append(_issue('dimension_invalid', 'ism_matrix', 'Matrix must be a list of rows.'))
        raise_issues(issues)
    if len(matrix) != n:
        issues.append(_issue('dimension_invalid', 'ism_matrix', 'Matrix dimensions must match criteria.'))
    cleaned = []
    for i, row in enumerate(matrix):
        path = f'ism_matrix.{i}'
        if not isinstance(row, list):
            issues.append(_issue('dimension_invalid', path, 'Row must be a list.'))
            continue
        if len(row) != n:
            issues.append(_issue('dimension_invalid', path, 'Row dimensions must match criteria.'))
        output = []
        for j, value in enumerate(row):
            cell_path = f'{path}.{j}'
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append(_issue('cell_empty', cell_path, 'Cell cannot be empty.'))
                continue
            if not _is_number(value):
                issues.append(_issue('non_numeric', cell_path, 'Cell must be numeric.'))
                continue
            try:
                finite = math.isfinite(float(value))
            except OverflowError:
                finite = False
            if not finite:
                issues.append(_issue('non_finite', cell_path, 'Cell must be finite.'))
                continue
            if value not in (0, 1):
                issues.append(_issue('ism_relation_invalid', cell_path, 'Relation must be exactly zero or one.'))
                continue
            output.append(int(value))
        cleaned.append(output)
    raise_issues(issues)
    return {'criteria': names, 'ism_matrix': cleaned}


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
                _issue('invalid_method', f'selected_methods.{i}', _('Unknown method id: %(method)s.') % {'method': repr(raw)}),
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
        raise_issues([_issue('invalid_type', field, _('%(field)s must be a list of names.') % {'field': _(field)})])

    if len(names) > MAX_DIM:
        issues.append(
            _issue('dimension_invalid', field, _('%(field)s must have at most %(maximum)s names.') % {'field': _(field), 'maximum': MAX_DIM}),
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
        issues.append(_issue('dimension_invalid', field, _('%(field)s must have at least 1 name.') % {'field': _(field)}))

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
        issues.append(_issue('dimension_invalid', 'criteria', _('n must be <= %(maximum)s.') % {'maximum': MAX_DIM}))
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

    # AC13: all-zero benefit column (even if that criterion's weight is 0)
    if (
        not issues
        and cleaned_matrix
        and cleaned_types
        and all(len(row) == len(cleaned_types) for row in cleaned_matrix)
    ):
        for j, t in enumerate(cleaned_types):
            if t != 'benefit':
                continue
            col = [row[j] for row in cleaned_matrix]
            if col and all(v == 0 for v in col):
                issues.append(
                    _issue(
                        'benefit_column_all_zero',
                        f'criteria.{j}',
                        'Benefit criterion column cannot be all zeros.',
                    ),
                )

    raise_issues(issues)
    return {
        'criteria': crit,
        'alternatives': alts,
        'weights': cleaned_weights,
        'types': cleaned_types,
        'performance_matrix': cleaned_matrix,
    }


def validate_ahp_draft_numbers(value: Any, *, field: str = 'ahp_matrix') -> None:
    """Keep incomplete drafts, but reject unrepresentable numbers before JSON storage."""
    issues = []

    def visit(cell: Any, path: str) -> None:
        if isinstance(cell, list):
            for index, child in enumerate(cell):
                visit(child, f'{path}.{index}')
        elif isinstance(cell, dict):
            for key, child in cell.items():
                visit(child, f'{path}.{key}')
        elif _is_number(cell):
            try:
                finite = math.isfinite(float(cell))
            except OverflowError:
                finite = False
            if not finite:
                issues.append(_issue('non_finite', path, 'Cell must be finite.'))

    visit(value, field)
    raise_issues(issues)


def validate_ism_draft_numbers(value: Any) -> None:
    # Root JSON null and null cells are retained drafts; execution validates shape.
    validate_ahp_draft_numbers(value, field='ism_matrix')


def validate_ahp_inputs(criteria: list[Any], matrix: list[Any]) -> dict[str, Any]:
    """Validate AHP pairwise comparison matrix and criteria (doc 05, AC02, AC08, AC17, AC18, AC26)."""
    issues: list[dict[str, str]] = []

    try:
        if isinstance(criteria, list):
            raise_issues([
                _issue('invalid_type', f'criteria.{index}', 'Criterion must be a string.')
                for index, value in enumerate(criteria) if not isinstance(value, str)
            ])
        crit = validate_names(criteria, 'criteria', require_non_empty=True)
    except CodedValidationError as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        issues.extend(detail.get('issues', []))
        crit = []

    n = len(crit)
    if n > MAX_DIM:
        issues.append(_issue('dimension_invalid', 'criteria', _('n must be <= %(maximum)s.') % {'maximum': MAX_DIM}))
    if n == 0:
        issues.append(_issue('dimension_invalid', 'criteria', 'n must be >= 1 for AHP.'))

    if not isinstance(matrix, list):
        issues.append(_issue('dimension_invalid', 'ahp_matrix', 'ahp_matrix must be a list of rows.'))
        raise_issues(issues)

    if n > 0 and (
        len(matrix) != n
        or any(not isinstance(row, list) or len(row) != n for row in matrix)
    ):
        issues.append(
            _issue(
                'dimension_invalid',
                'ahp_matrix',
                _('AHP matrix must have %(n)s rows and %(n)s cells per row.') % {'n': n},
            ),
        )

    cleaned_matrix: list[list[float]] = []
    for j, row in enumerate(matrix):
        row_path = f'ahp_matrix.{j}'
        if not isinstance(row, list):
            issues.append(_issue('dimension_invalid', row_path, 'Row must be a list.'))
            continue
        if n > 0 and len(row) != n:
            issues.append(
                _issue(
                    'dimension_invalid',
                    row_path,
                    _('Row must have exactly %(n)s cells.') % {'n': n},
                ),
            )
        cleaned_row: list[float] = []
        for k, cell in enumerate(row):
            cell_path = f'ahp_matrix.{j}.{k}'
            if cell is None or (isinstance(cell, str) and not cell.strip()):
                issues.append(_issue('cell_empty', cell_path, 'Cell cannot be empty.'))
                continue
            if not _is_number(cell):
                issues.append(_issue('non_numeric', cell_path, 'Cell must be numeric.'))
                continue
            try:
                cf = float(cell)
            except OverflowError:
                issues.append(_issue('non_finite', cell_path, 'Cell must be finite.'))
                continue

            if _is_non_finite(cf):
                issues.append(_issue('non_finite', cell_path, 'Cell must be finite.'))
                continue
            if cf <= 0:
                issues.append(_issue('cell_non_positive', cell_path, 'Cell must be strictly positive.'))
                continue
            cleaned_row.append(cf)
        cleaned_matrix.append(cleaned_row)

    # Reciprocal and diagonal checks only if matrix structure is complete
    if (
        not issues
        and n > 0
        and len(cleaned_matrix) == n
        and all(len(row) == n for row in cleaned_matrix)
    ):
        for j in range(n):
            if cleaned_matrix[j][j] != 1.0:
                issues.append(
                    _issue(
                        'ahp_diagonal_invalid',
                        f'ahp_matrix.{j}.{j}',
                        'Diagonal element must be 1.0.',
                    ),
                )
        for j in range(n):
            for k in range(j + 1, n):
                val_jk = cleaned_matrix[j][k]
                val_kj = cleaned_matrix[k][j]
                if abs(val_jk * val_kj - 1.0) >= 1e-4:
                    issues.append(
                        _issue(
                            'ahp_reciprocal_mismatch',
                            f'ahp_matrix.{k}.{j}',
                            'Pairwise cells must be reciprocals (a[k,j] = 1 / a[j,k]).',
                        ),
                    )

    raise_issues(issues)
    return {
        'criteria': crit,
        'ahp_matrix': cleaned_matrix,
    }


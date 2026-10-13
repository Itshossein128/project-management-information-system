"""Pure AHP engine tests (AC02, AC17, AC18, Saaty RI, geometric mean, consistency ratio, guards)."""

from __future__ import annotations

import inspect
import pytest

from config.exceptions import CodedValidationError
from decision_support.services import ahp_service
from decision_support.services.ahp_service import compute_ahp


def _issues(exc: CodedValidationError) -> list[dict]:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return detail.get('issues', [])


def test_ac17_consistent_matrix_geometric_mean_weights():
    # 3 criteria where C1 = 2*C2, C2 = 3*C3, hence C1 = 6*C3
    matrix = [
        [1.0, 2.0, 6.0],
        [0.5, 1.0, 3.0],
        [1.0 / 6.0, 1.0 / 3.0, 1.0],
    ]
    out = compute_ahp(['تجربه', 'قیمت', 'زمان'], matrix)

    weights = out['weights']
    assert len(weights) == 3

    # Ranking order: C1 > C2 > C3
    assert weights[0]['criterion'] == 'تجربه'
    assert weights[0]['weight'] == pytest.approx(0.60, abs=1e-2)
    assert weights[0]['rank'] == 1

    assert weights[1]['criterion'] == 'قیمت'
    assert weights[1]['weight'] == pytest.approx(0.30, abs=1e-2)
    assert weights[1]['rank'] == 2

    assert weights[2]['criterion'] == 'زمان'
    assert weights[2]['weight'] == pytest.approx(0.10, abs=1e-2)
    assert weights[2]['rank'] == 3

    assert sum(w['weight'] for w in weights) == pytest.approx(1.0)
    assert out['lambda_max'] == pytest.approx(3.0, abs=1e-2)
    assert out['ci'] == pytest.approx(0.0, abs=1e-2)
    assert out['cr'] == pytest.approx(0.0, abs=1e-2)
    assert out['is_consistent'] is True


def test_ahp_n1_single_criterion():
    out = compute_ahp(['تنها_معیار'], [[1.0]])
    assert len(out['weights']) == 1
    assert out['weights'][0]['criterion'] == 'تنها_معیار'
    assert out['weights'][0]['weight'] == pytest.approx(1.0)
    assert out['weights'][0]['rank'] == 1
    assert out['lambda_max'] == pytest.approx(1.0)
    assert out['ci'] == pytest.approx(0.0)
    assert out['cr'] == pytest.approx(0.0)
    assert out['is_consistent'] is True


def test_ahp_n2_two_criteria():
    matrix = [
        [1.0, 3.0],
        [1.0 / 3.0, 1.0],
    ]
    out = compute_ahp(['C1', 'C2'], matrix)
    assert len(out['weights']) == 2
    assert out['weights'][0]['weight'] == pytest.approx(0.75)
    assert out['weights'][1]['weight'] == pytest.approx(0.25)
    assert out['cr'] == pytest.approx(0.0)
    assert out['is_consistent'] is True


def test_ac18_inconsistent_matrix():
    # Intransitive circular preferences: A > B, B > C, C > A
    matrix = [
        [1.0, 5.0, 0.2],
        [0.2, 1.0, 5.0],
        [5.0, 0.2, 1.0],
    ]
    out = compute_ahp(['A', 'B', 'C'], matrix)
    assert sum(w['weight'] for w in out['weights']) == pytest.approx(1.0)
    assert out['cr'] > 0.10
    assert out['is_consistent'] is False


def test_ahp_validation_diagonal_invalid():
    matrix = [
        [2.0, 3.0],
        [1.0 / 3.0, 1.0],
    ]
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B'], matrix)
    codes = [i['code'] for i in _issues(exc.value)]
    assert 'ahp_diagonal_invalid' in codes
    paths = [i['path'] for i in _issues(exc.value)]
    assert 'ahp_matrix.0.0' in paths


def test_ahp_validation_reciprocal_mismatch():
    matrix = [
        [1.0, 4.0],
        [0.5, 1.0],  # Reciprocal of 4 is 0.25, not 0.5
    ]
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B'], matrix)
    codes = [i['code'] for i in _issues(exc.value)]
    assert 'ahp_reciprocal_mismatch' in codes
    paths = [i['path'] for i in _issues(exc.value)]
    assert 'ahp_matrix.1.0' in paths


def test_ahp_validation_non_positive_and_empty():
    matrix = [
        [1.0, -1.0],
        [-1.0, 1.0],
    ]
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B'], matrix)
    codes = [i['code'] for i in _issues(exc.value)]
    assert 'cell_non_positive' in codes


def test_ac02_no_saw_or_topsis_in_module():
    src = inspect.getsource(ahp_service)
    assert 'saw_service' not in src
    assert 'topsis_service' not in src
    assert 'alternatives' not in src

@pytest.mark.parametrize('values', [[1], [1, 3], [1, 3, 6], [1] * 10])
def test_input_order_ordinal_ranks_finite_and_unchanged(values):
    import copy
    import math
    criteria = [f'C{i}' for i in range(len(values))]
    matrix = [[a / b for b in values] for a in values]
    before = copy.deepcopy((criteria, matrix))
    out = compute_ahp(criteria, matrix)
    assert (criteria, matrix) == before
    assert [w['criterion'] for w in out['weights']] == criteria
    assert [w['weight'] for w in out['weights']] == pytest.approx(
        [v / sum(values) for v in values], abs=1e-12)
    expected = sorted(range(len(values)), key=lambda i: (-values[i], i))
    ranks = {i: rank for rank, i in enumerate(expected, 1)}
    assert [w['rank'] for w in out['weights']] == [ranks[i] for i in range(len(values))]
    assert sum(w['weight'] for w in out['weights']) == pytest.approx(1, abs=1e-6)
    assert all(math.isfinite(w['weight']) and w['weight'] > 0 for w in out['weights'])
    assert all(math.isfinite(out[k]) for k in ['lambda_max', 'ci', 'cr'])


def test_log_geometric_mean_avoids_intermediate_product_overflow():
    # Row products overflow although each comparison and final result is representable.
    values = [1e200, 1, 1, 1, 1, 1]
    matrix = [[a / b for b in values] for a in values]
    out = compute_ahp([f'C{i}' for i in range(6)], matrix)
    assert out['weights'][0]['weight'] == pytest.approx(1)
    assert out['weights'][1]['weight'] == pytest.approx(1e-200, rel=1e-10)
    assert out['lambda_max'] == pytest.approx(6)


def test_ri_table_and_circular_consistency_exact_metrics(monkeypatch):
    assert list(ahp_service.SAATY_RI.values()) == [0, 0, .58, .90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
    matrix = [[1, 5, .2], [.2, 1, 5], [5, .2, 1]]
    out = compute_ahp(['A', 'B', 'C'], matrix)
    assert out['lambda_max'] == pytest.approx(6.2, abs=1e-12)
    assert out['ci'] == pytest.approx(1.6, abs=1e-12)
    assert out['cr'] == pytest.approx(1.6/.58, abs=1e-12)
    assert out['is_consistent'] is False
    monkeypatch.setitem(ahp_service.SAATY_RI, 3, out['ci'] / .1)
    boundary = compute_ahp(['A', 'B', 'C'], matrix)
    assert boundary['cr'] == .1
    assert boundary['is_consistent'] is True
    monkeypatch.setitem(ahp_service.SAATY_RI, 3, out['ci'] / .10001)
    assert compute_ahp(['A', 'B', 'C'], matrix)['is_consistent'] is False


@pytest.mark.parametrize('n', range(1, 11))
def test_equal_comparisons_ci_clamped_and_consistent(n):
    out = compute_ahp([str(i) for i in range(n)], [[1]*n for _ in range(n)])
    assert out['ci'] == 0
    assert out['cr'] == 0
    assert out['is_consistent'] is True

@pytest.mark.parametrize('value,code', [
    ('2', 'non_numeric'), (True, 'non_numeric'), (None, 'cell_empty'),
    (' ', 'cell_empty'), (0, 'cell_non_positive'), (-1, 'cell_non_positive'),
    (float('inf'), 'non_finite'), (float('nan'), 'non_finite'), (10**400, 'non_finite'),
])
def test_strict_cell_type_and_path(value, code):
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B'], [[1, value], [.5, 1]])
    assert any(i['code'] == code and i['path'] == 'ahp_matrix.0.1' for i in _issues(exc.value))


@pytest.mark.parametrize('criteria,code,path', [
    ([1], 'invalid_type', 'criteria.0'), ([True], 'invalid_type', 'criteria.0'),
    ([None], 'invalid_type', 'criteria.0'), (['  '], 'name_empty', 'criteria.0'),
    (['A', ' A '], 'name_duplicate', 'criteria.1'), ([], 'dimension_invalid', 'criteria'),
    ([str(i) for i in range(11)], 'dimension_invalid', 'criteria'),
])
def test_strict_criterion_type_and_dimension(criteria, code, path):
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(criteria, [[1]*len(criteria) for _ in criteria])
    assert any(i['code'] == code and i['path'] == path for i in _issues(exc.value))


def test_diagonal_is_exact_not_epsilon():
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A'], [[1.00005]])
    assert _issues(exc.value)[0]['code'] == 'ahp_diagonal_invalid'
    assert _issues(exc.value)[0]['path'] == 'ahp_matrix.0.0'


@pytest.mark.parametrize('a,b,valid', [
    (9, (1 + .000099)/9, True), (9, (1 + .000101)/9, False),
    (1/9, 9*(1 - .000099), True), (1/9, 9*(1 - .000101), False),
])
def test_product_residual_not_inverse_difference(a, b, valid):
    if valid:
        assert compute_ahp(['A', 'B'], [[1, a], [b, 1]])['cr'] == 0
    else:
        with pytest.raises(CodedValidationError) as exc:
            compute_ahp(['A', 'B'], [[1, a], [b, 1]])
        assert any(i['code'] == 'ahp_reciprocal_mismatch' and i['path'] == 'ahp_matrix.1.0'
                   for i in _issues(exc.value))


@pytest.mark.parametrize('matrix', [[], [[1]], [[1, 2], [.5]], [1, [1, 1]]])
def test_ragged_matrix_is_coded_not_index_error(matrix):
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B'], matrix)
    assert any(i['code'] == 'dimension_invalid' for i in _issues(exc.value))


def test_unrepresentable_calculation_is_coded():
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A', 'B', 'C'],
                    [[1, 1e308, 1e308], [1e-308, 1, 1e308], [1e-308, 1e-308, 1]])
    assert any(i['code'] == 'non_finite' and i['path'] == 'ahp_matrix' for i in _issues(exc.value))


@pytest.mark.parametrize('criteria,matrix', [
    ([], []), ([str(i) for i in range(11)], []),
    ({'A': 1}, [[1]]), (['A'], {'row': [1]}), (['A'], [1]),
])
def test_convergence_ahp_structural_errors_fully_localized(criteria, matrix):
    from django.utils.translation import override
    observed = []
    for lang in ['en', 'fa']:
        with override(lang), pytest.raises(CodedValidationError) as exc:
            compute_ahp(criteria, matrix)
        observed.append(_issues(exc.value))
    assert [(i['code'], i['path']) for i in observed[0]] == [(i['code'], i['path']) for i in observed[1]]
    assert all(en['message'] != fa['message'] for en, fa in zip(*observed))


@pytest.mark.parametrize('value', [1e307, 1e308])
def test_representable_extreme_cyclic_metrics(value):
    import math
    matrix = [[1, value, 1/value], [1/value, 1, value], [value, 1/value, 1]]
    result = compute_ahp(['A', 'B', 'C'], matrix)
    assert [row['weight'] for row in result['weights']] == pytest.approx([1/3]*3)
    assert result['lambda_max'] == pytest.approx(value, rel=1e-12)
    assert result['ci'] == pytest.approx(value/2, rel=1e-12)
    assert result['cr'] == pytest.approx((value/2)/.58, rel=1e-12)
    assert result['is_consistent'] is False
    assert all(math.isfinite(result[key]) for key in ['lambda_max', 'ci', 'cr'])


def test_representable_average_with_overflowing_individual_ratio():
    import math
    matrix = [[1,1e308,1e-2,1], [1e-308,1,1e308,1e308],
              [1e2,1e-308,1,1e-308], [1,1e-308,1e308,1]]
    result = compute_ahp(['A', 'B', 'C', 'D'], matrix)
    # Dominant ratio is 10**308.5; its contribution to the mean is representable.
    expected = (1e308/4)*math.sqrt(10)
    assert result['lambda_max'] == pytest.approx(expected, rel=1e-12)
    assert result['cr'] == pytest.approx((expected/3)/.9, rel=1e-12)
    assert result['is_consistent'] is False
    assert all(math.isfinite(row['weight']) and row['weight'] > 0 for row in result['weights'])
    assert sum(row['weight'] for row in result['weights']) == pytest.approx(1, abs=1e-6)



def test_unrepresentable_average_is_coded():
    matrix = [[1 if i == j else 1e308 if (j-i)%5 in (1,2) else 1e-308
               for j in range(5)] for i in range(5)]
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp([str(i) for i in range(5)], matrix)
    assert any(i['code'] == 'non_finite' and i['path'] == 'ahp_matrix' for i in _issues(exc.value))


@pytest.mark.parametrize('matrix', [[], [[1]], [[1,2],[.5]], [1,[.5,1]], {'row':[1]}, [[1,2,3],[.5,1]]])
def test_convergence_shape_has_root_and_row_diagnostics(matrix):
    with pytest.raises(CodedValidationError) as exc:
        compute_ahp(['A','B'], matrix)
    issues = _issues(exc.value)
    assert any(i['code'] == 'dimension_invalid' and i['path'] == 'ahp_matrix' for i in issues)
    if isinstance(matrix, list) and len(matrix) == 2:
        assert any(i['code'] == 'dimension_invalid' and i['path'].startswith('ahp_matrix.') for i in issues)

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

"""Pure SAW engine tests (AC14, AC11, AC09, AC13, AC01 independence)."""

from __future__ import annotations

import inspect

import pytest

from config.exceptions import CodedValidationError
from decision_support.services import saw_service
from decision_support.services.saw_service import compute_saw


def _issues(exc: CodedValidationError):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return detail.get('issues', [])


def test_ac14_acceptance_sample():
    out = compute_saw(
        ['تجربه', 'قیمت'],
        ['پیمانکار الف', 'پیمانکار ب'],
        [1, 1],
        ['benefit', 'cost'],
        [[10, 100], [5, 200]],
    )
    ranking = out['ranking']
    assert len(ranking) == 2
    assert ranking[0]['option'] == 'پیمانکار الف'
    assert ranking[0]['score'] == pytest.approx(1.0)
    assert ranking[0]['rank'] == 1
    assert ranking[1]['option'] == 'پیمانکار ب'
    assert ranking[1]['score'] == pytest.approx(0.5)
    assert ranking[1]['rank'] == 2
    assert out['weights_normalized'] == pytest.approx([0.5, 0.5])


def test_ac11_scaled_weights_same_scores():
    base = dict(
        criteria=['c1', 'c2'],
        alternatives=['a1', 'a2'],
        types=['benefit', 'cost'],
        matrix=[[10, 100], [5, 200]],
    )
    a = compute_saw(**base, weights=[2, 3])
    b = compute_saw(**base, weights=[20, 30])
    assert [r['score'] for r in a['ranking']] == pytest.approx([r['score'] for r in b['ranking']])
    assert [r['option'] for r in a['ranking']] == [r['option'] for r in b['ranking']]


def test_ac01_no_topsis_in_output_or_module():
    out = compute_saw(['c'], ['a'], [1], ['benefit'], [[1]])
    assert 'TOPSIS' not in out
    assert 'topsis' not in out
    src = inspect.getsource(saw_service)
    # No ideal-solution / distance machinery from the combined sample
    assert 'ideal_best' not in src
    assert 'd_best' not in src
    assert 'from math import' not in src and 'import math' not in src


def test_ac13_engine_benefit_all_zero():
    with pytest.raises(CodedValidationError) as ei:
        compute_saw(
            ['b', 'c'],
            ['a1', 'a2'],
            [0, 1],
            ['benefit', 'cost'],
            [[0, 100], [0, 200]],
        )
    assert any(i['code'] == 'benefit_column_all_zero' and i['path'] == 'criteria.0' for i in _issues(ei.value))


def test_ac09_engine_cost_zero():
    with pytest.raises(CodedValidationError) as ei:
        compute_saw(['c'], ['a'], [1], ['cost'], [[0]])
    assert any(i['code'] == 'cost_zero' for i in _issues(ei.value))


def test_equal_scores_stable_order_and_ordinal_ranks():
    """Equal scores: preserve input alternative order; interim ranks are 1,2,… (not tied)."""
    out = compute_saw(
        ['c1'],
        ['first', 'second', 'third'],
        [1],
        ['benefit'],
        [[5], [5], [5]],
    )
    ranking = out['ranking']
    assert [r['option'] for r in ranking] == ['first', 'second', 'third']
    assert [r['score'] for r in ranking] == pytest.approx([1.0, 1.0, 1.0])
    assert [r['rank'] for r in ranking] == [1, 2, 3]

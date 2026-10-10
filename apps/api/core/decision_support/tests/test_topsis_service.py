"""Pure TOPSIS engine tests (AC15, AC16, AC11, AC01 independence, zero denominator)."""

from __future__ import annotations

import inspect

import pytest

from config.exceptions import CodedValidationError
from decision_support.services import topsis_service
from decision_support.services.topsis_service import compute_topsis


def _issues(exc: CodedValidationError):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return detail.get('issues', [])


def test_ac15_acceptance_sample():
    out = compute_topsis(
        ['تجربه', 'قیمت'],
        ['پیمانکار الف', 'پیمانکار ب'],
        [1, 1],
        ['benefit', 'cost'],
        [[10, 100], [5, 200]],
    )
    ranking = out['ranking']
    assert len(ranking) == 2
    assert ranking[0]['option'] == 'پیمانکار الف'
    assert ranking[0]['closeness'] == pytest.approx(1.0)
    assert ranking[0]['score'] == pytest.approx(1.0)
    assert ranking[0]['rank'] == 1
    assert ranking[0]['d_best'] == pytest.approx(0.0)
    assert ranking[0]['d_worst'] > 0.0

    assert ranking[1]['option'] == 'پیمانکار ب'
    assert ranking[1]['closeness'] == pytest.approx(0.0)
    assert ranking[1]['score'] == pytest.approx(0.0)
    assert ranking[1]['rank'] == 2
    assert ranking[1]['d_best'] > 0.0
    assert ranking[1]['d_worst'] == pytest.approx(0.0)

    assert out['weights_normalized'] == pytest.approx([0.5, 0.5])


def test_ac11_scaled_weights_same_scores():
    base = dict(
        criteria=['c1', 'c2'],
        alternatives=['a1', 'a2'],
        types=['benefit', 'cost'],
        matrix=[[10, 100], [5, 200]],
    )
    a = compute_topsis(**base, weights=[2, 3])
    b = compute_topsis(**base, weights=[20, 30])
    assert [r['closeness'] for r in a['ranking']] == pytest.approx([r['closeness'] for r in b['ranking']])
    assert [r['option'] for r in a['ranking']] == [r['option'] for r in b['ranking']]


def test_ac01_no_saw_in_output_or_module():
    out = compute_topsis(
        ['تجربه', 'قیمت'],
        ['پیمانکار الف', 'پیمانکار ب'],
        [1, 1],
        ['benefit', 'cost'],
        [[10, 100], [5, 200]],
    )
    assert 'SAW' not in out
    assert 'saw' not in out
    src = inspect.getsource(topsis_service)
    assert 'compute_saw' not in src


def test_ac16_zero_total_distance():
    """Single alternative or identical rows where d_best + d_worst == 0 -> closeness is 0.5."""
    out = compute_topsis(
        ['c1'],
        ['a1'],
        [1],
        ['benefit'],
        [[5]],
    )
    ranking = out['ranking']
    assert len(ranking) == 1
    assert ranking[0]['closeness'] == pytest.approx(0.5)
    assert ranking[0]['score'] == pytest.approx(0.5)
    assert ranking[0]['rank'] == 1


def test_topsis_denom_zero_rejected():
    """All-zero column vector-normalization denominator is 0 -> raises topsis_denom_zero."""
    with pytest.raises(CodedValidationError) as ei:
        compute_topsis(
            ['c1', 'c2'],
            ['a1', 'a2'],
            [1, 1],
            ['benefit', 'cost'],
            [[0, 10], [0, 20]],
        )
    issues = _issues(ei.value)
    assert any(i['code'] == 'topsis_denom_zero' and i['path'] == 'criteria.0' for i in issues)


def test_equal_scores_stable_order_and_ordinal_ranks():
    """Equal closeness scores: preserve input alternative order; ordinal ranks are 1, 2, ..."""
    out = compute_topsis(
        ['c1'],
        ['first', 'second', 'third'],
        [1],
        ['benefit'],
        [[5], [5], [5]],
    )
    ranking = out['ranking']
    assert [r['option'] for r in ranking] == ['first', 'second', 'third']
    assert [r['closeness'] for r in ranking] == pytest.approx([0.5, 0.5, 0.5])
    assert [r['rank'] for r in ranking] == [1, 2, 3]

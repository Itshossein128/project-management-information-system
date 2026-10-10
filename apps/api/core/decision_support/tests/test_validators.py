import math

import pytest
from rest_framework import status

from config.exceptions import CodedValidationError
from decision_support.services.validators import validate_ranking_inputs
from decision_support.services.weights import normalize_weights

BASE = '/api/v1/projects/{project_id}/decision-cases/'


def _valid_ranking(**overrides):
    data = {
        'criteria': ['c1', 'c2'],
        'alternatives': ['a1', 'a2'],
        'weights': [1, 1],
        'types': ['benefit', 'cost'],
        'matrix': [[10, 100], [5, 200]],
    }
    data.update(overrides)
    return data


def _issues(exc: CodedValidationError):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return detail.get('issues', [])


def test_ac11_normalize_weights_proportional():
    assert normalize_weights([2, 3]) == normalize_weights([20, 30])


def test_ac05_valid_dimensions():
    validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [[1]])
    validate_ranking_inputs(
        [f'c{i}' for i in range(10)],
        [f'a{i}' for i in range(10)],
        [1] * 10,
        ['benefit'] * 10,
        [[1] * 10 for _ in range(10)],
    )
    validate_ranking_inputs(
        ['c1', 'c2', 'c3'],
        ['a1', 'a2'],
        [1, 1, 1],
        ['benefit', 'benefit', 'cost'],
        [[1, 2, 3], [4, 5, 6]],
    )


def test_ac06_zero_or_over_ten():
    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs([], ['a'], [], [], [])
    assert any(i['path'].startswith('criteria') or i['path'] == 'criteria' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], [], [1], ['benefit'], [])
    assert any(i['path'].startswith('alternatives') or i['path'] == 'alternatives' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError):
        validate_ranking_inputs([f'c{i}' for i in range(11)], ['a'], [1] * 11, ['benefit'] * 11, [[1] * 11])


def test_ac07_length_mismatch():
    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c1', 'c2'], ['a1'], [1], ['benefit', 'cost'], [[1, 2]])
    codes = {i['code'] for i in _issues(ei.value)}
    assert 'length_mismatch' in codes

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c1'], ['a1', 'a2'], [1], ['benefit'], [[1], [1, 2]])
    assert any(i['code'] == 'length_mismatch' for i in _issues(ei.value))


def test_ac08_empty_and_non_finite():
    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [[None]])
    issues = _issues(ei.value)
    assert any(i['code'] == 'empty_cell' and i['path'] == 'performance_matrix.0.0' for i in issues)

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [['x']])
    assert any(i['code'] == 'non_numeric' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [[-1]])
    assert any(i['code'] == 'negative_value' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [[math.nan]])
    assert any(i['code'] == 'non_finite' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['benefit'], [[math.inf]])
    assert any(i['code'] == 'non_finite' for i in _issues(ei.value))


def test_ac09_ac10_ac12():
    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['cost'], [[0]])
    assert any(i['code'] == 'cost_zero' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [-1], ['benefit'], [[1]])
    assert any(i['code'] == 'weight_negative' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c1', 'c2'], ['a'], [0, 0], ['benefit', 'benefit'], [[1, 1]])
    assert any(i['code'] == 'weights_all_zero' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['', 'c'], ['a'], [1, 1], ['benefit', 'benefit'], [[1, 1]])
    assert any(i['code'] == 'name_empty' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c', 'c'], ['a'], [1, 1], ['benefit', 'benefit'], [[1, 1]])
    assert any(i['code'] == 'name_duplicate' for i in _issues(ei.value))

    with pytest.raises(CodedValidationError) as ei:
        validate_ranking_inputs(['c'], ['a'], [1], ['maybe'], [[1]])
    assert any(i['code'] == 'invalid_type' for i in _issues(ei.value))


@pytest.mark.django_db
def test_ac26_api_empty_cell_path(auth_client, project):
    url = BASE.format(project_id=project.id)
    create = auth_client.post(
        url,
        {
            'title': 'Case',
            'selected_methods': ['saw'],
            'criteria': ['c1', 'c2'],
            'alternatives': ['a1'],
            'weights': [1, 1],
            'types': ['benefit', 'cost'],
            'performance_matrix': [[10, None]],
        },
        format='json',
    )
    assert create.status_code == status.HTTP_400_BAD_REQUEST, create.data
    assert create.data['error']['code'] == 'decision_input_invalid'
    issues = create.data['error']['details'].get('issues', [])
    assert any(i.get('path') == 'performance_matrix.0.1' for i in issues)

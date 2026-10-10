"""API tests for AHP-only runs (AC02, AC04, AC17, AC18, AC23–AC26)."""

from __future__ import annotations

import pytest
from rest_framework import status

from decision_support.models import DecisionRun

CASES = '/api/v1/projects/{project_id}/decision-cases/'


def _ahp_payload(**overrides):
    data = {
        'title': 'AHP criteria weighting sample',
        'selected_methods': ['ahp'],
        'criteria': ['تجربه', 'قیمت', 'زمان'],
        'alternatives': [],
        'weights': [],
        'types': [],
        'performance_matrix': [],
        'ahp_matrix': [
            [1.0, 2.0, 6.0],
            [0.5, 1.0, 3.0],
            [1.0 / 6.0, 1.0 / 3.0, 1.0],
        ],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_ac02_ac17_ahp_only_run(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(), format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']

    run = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    assert run.data['method'] == 'ahp'
    assert run.data['result']['status'] == 'ok'
    assert run.data['result']['engine'] == 'ahp'

    weights = run.data['result']['weights']
    assert len(weights) == 3
    assert weights[0]['criterion'] == 'تجربه'
    assert weights[0]['weight'] == pytest.approx(0.60, abs=1e-2)
    assert weights[0]['rank'] == 1

    assert weights[1]['criterion'] == 'قیمت'
    assert weights[1]['weight'] == pytest.approx(0.30, abs=1e-2)
    assert weights[1]['rank'] == 2

    assert weights[2]['criterion'] == 'زمان'
    assert weights[2]['weight'] == pytest.approx(0.10, abs=1e-2)
    assert weights[2]['rank'] == 3

    assert run.data['result']['cr'] == pytest.approx(0.0, abs=1e-2)
    assert run.data['result']['is_consistent'] is True
    assert str(run.data['extracted_by']) == str(user.id)

    # Ensure zero ranking runs were generated
    assert DecisionRun.objects.filter(case_id=case_id).count() == 1


@pytest.mark.django_db
def test_ac18_inconsistent_run_persisted_with_alert(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    inconsistent_payload = _ahp_payload(
        criteria=['A', 'B', 'C'],
        ahp_matrix=[
            [1.0, 5.0, 0.2],
            [0.2, 1.0, 5.0],
            [5.0, 0.2, 1.0],
        ],
    )
    case = auth_client.post(base, inconsistent_payload, format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']

    run = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    assert run.data['result']['status'] == 'ok'
    assert run.data['result']['cr'] > 0.10
    assert run.data['result']['is_consistent'] is False


@pytest.mark.django_db
def test_ahp_validation_error_paths(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    bad_payload = _ahp_payload(
        ahp_matrix=[
            [2.0, 2.0, 6.0],  # Diagonal is 2.0 instead of 1.0
            [0.5, 1.0, 3.0],
            [1.0 / 6.0, 1.0 / 3.0, 1.0],
        ],
    )
    case = auth_client.post(base, bad_payload, format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']

    run = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run.status_code == status.HTTP_400_BAD_REQUEST
    error_details = run.data.get('error', {}).get('details', {}) if isinstance(run.data, dict) else {}
    issues = error_details.get('issues', run.data.get('issues', []))
    codes = [i['code'] for i in issues]
    assert 'ahp_diagonal_invalid' in codes
    paths = [i['path'] for i in issues]
    assert 'ahp_matrix.0.0' in paths
    assert DecisionRun.objects.filter(case_id=case_id).count() == 0


@pytest.mark.django_db
def test_ac04_ahp_does_not_mutate_case_ranking_inputs(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    payload = _ahp_payload(
        selected_methods=['ahp', 'saw'],
        alternatives=['پیمانکار ۱', 'پیمانکار ۲'],
        weights=[10, 20, 30],
        types=['benefit', 'cost', 'benefit'],
        performance_matrix=[[10, 100, 5], [20, 200, 10]],
    )
    case = auth_client.post(base, payload, format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']

    # Execute AHP
    run = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data

    # Fetch case again
    refetched = auth_client.get(f"{base}{case_id}/")
    assert refetched.status_code == status.HTTP_200_OK
    assert refetched.data['weights'] == [10, 20, 30]
    assert refetched.data['alternatives'] == ['پیمانکار ۱', 'پیمانکار ۲']
    assert refetched.data['performance_matrix'] == [[10, 100, 5], [20, 200, 10]]


@pytest.mark.django_db
def test_ac23_ac24_immutable_history(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(), format='json')
    case_id = case.data['id']

    run1 = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run1.status_code == status.HTTP_201_CREATED
    r1_weights = run1.data['result']['weights']

    # Update case with different comparisons
    new_matrix = [
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
    ]
    auth_client.patch(f"{base}{case_id}/", {'ahp_matrix': new_matrix}, format='json')

    # Run AHP again
    run2 = auth_client.post(f"{base}{case_id}/runs/", {'method': 'ahp'}, format='json')
    assert run2.status_code == status.HTTP_201_CREATED
    r2_weights = run2.data['result']['weights']

    assert r1_weights != r2_weights
    # Refetch run1 and verify its snapshot is unchanged
    run1_refetched = auth_client.get(f"{base}{case_id}/runs/{run1.data['id']}/")
    assert run1_refetched.data['result']['weights'] == r1_weights

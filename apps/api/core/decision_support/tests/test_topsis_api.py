"""API tests for TOPSIS-only runs (AC01, AC15, AC16, AC03, AC23–AC26)."""

from __future__ import annotations

import copy

import pytest
from rest_framework import status

from decision_support.models import DecisionRun

CASES = '/api/v1/projects/{project_id}/decision-cases/'


def _topsis_payload(**overrides):
    data = {
        'title': 'TOPSIS sample',
        'selected_methods': ['topsis'],
        'criteria': ['تجربه', 'قیمت'],
        'alternatives': ['پیمانکار الف', 'پیمانکار ب'],
        'weights': [1, 1],
        'types': ['benefit', 'cost'],
        'performance_matrix': [[10, 100], [5, 200]],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_ac01_ac15_topsis_only_run(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _topsis_payload(), format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']

    run = auth_client.post(f"{base}{case_id}/runs/", {'method': 'topsis'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    assert run.data['method'] == 'topsis'
    assert run.data['result']['status'] == 'ok'
    assert run.data['result']['engine'] == 'topsis'

    ranking = run.data['result']['ranking']
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

    assert 'SAW' not in run.data['result']
    assert 'saw' not in run.data['result']
    assert 'weights_normalized' in run.data['input_snapshot']
    assert str(run.data['extracted_by']) == str(user.id)

    # Prove AC01: zero SAW runs created
    assert DecisionRun.objects.filter(case_id=case_id, method='saw').count() == 0
    assert DecisionRun.objects.filter(case_id=case_id).count() == 1


@pytest.mark.django_db
def test_ac16_api_zero_distance(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        {
            'title': 'AC16 single alt',
            'selected_methods': ['topsis'],
            'criteria': ['c1'],
            'alternatives': ['a1'],
            'weights': [1],
            'types': ['benefit'],
            'performance_matrix': [[5]],
        },
        format='json',
    )
    assert case.status_code == status.HTTP_201_CREATED, case.data
    run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'topsis'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    ranking = run.data['result']['ranking']
    assert len(ranking) == 1
    assert ranking[0]['closeness'] == pytest.approx(0.5)
    assert ranking[0]['score'] == pytest.approx(0.5)


@pytest.mark.django_db
def test_topsis_denom_zero_rejected_no_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        _topsis_payload(
            title='zero column',
            weights=[0, 1],
            types=['benefit', 'cost'],
            performance_matrix=[[0, 100], [0, 200]],
        ),
        format='json',
    )
    if case.status_code == status.HTTP_201_CREATED:
        before = DecisionRun.objects.count()
        run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'topsis'}, format='json')
        assert run.status_code == status.HTTP_400_BAD_REQUEST
        issues = run.data['error']['details'].get('issues', [])
        assert any(i.get('code') in ('topsis_denom_zero', 'benefit_column_all_zero') for i in issues)
        assert DecisionRun.objects.count() == before
    else:
        assert case.status_code == status.HTTP_400_BAD_REQUEST
        issues = case.data['error']['details'].get('issues', [])
        assert any(i.get('code') in ('topsis_denom_zero', 'benefit_column_all_zero') for i in issues)


@pytest.mark.django_db
def test_ac03_ac25_saw_and_topsis_independent(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        _topsis_payload(title='Multi-method', selected_methods=['saw', 'topsis']),
        format='json',
    )
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']
    runs_url = f'{base}{case_id}/runs/'

    # Run SAW
    saw_run = auth_client.post(runs_url, {'method': 'saw'}, format='json')
    assert saw_run.status_code == status.HTTP_201_CREATED, saw_run.data
    assert saw_run.data['method'] == 'saw'

    # Run TOPSIS
    topsis_run = auth_client.post(runs_url, {'method': 'topsis'}, format='json')
    assert topsis_run.status_code == status.HTTP_201_CREATED, topsis_run.data
    assert topsis_run.data['method'] == 'topsis'

    # Two independent runs exist
    runs_list = auth_client.get(runs_url)
    assert runs_list.status_code == status.HTTP_200_OK
    assert runs_list.data['count'] == 2
    assert len(runs_list.data['results']) == 2

    # Verify SAW results only has SAW fields; TOPSIS only has TOPSIS fields
    saw_data = auth_client.get(f'{runs_url}{saw_run.data["id"]}/').data
    topsis_data = auth_client.get(f'{runs_url}{topsis_run.data["id"]}/').data

    assert saw_data['result']['engine'] == 'saw'
    assert 'd_best' not in saw_data['result']['ranking'][0]

    assert topsis_data['result']['engine'] == 'topsis'
    assert 'd_best' in topsis_data['result']['ranking'][0]
    assert 'closeness' in topsis_data['result']['ranking'][0]


@pytest.mark.django_db
def test_ac23_ac24_topsis_immutability(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _topsis_payload(), format='json')
    case_id = case.data['id']
    runs_url = f'{base}{case_id}/runs/'

    run_a = auth_client.post(runs_url, {'method': 'topsis'}, format='json')
    assert run_a.status_code == status.HTTP_201_CREATED, run_a.data
    snap_a = copy.deepcopy(run_a.data['input_snapshot'])
    result_a = copy.deepcopy(run_a.data['result'])

    # Mutate case inputs
    patch = auth_client.patch(
        f'{base}{case_id}/',
        {'weights': [2, 1], 'performance_matrix': [[10, 100], [5, 200]]},
        format='json',
    )
    assert patch.status_code == status.HTTP_200_OK, patch.data

    # Run again -> new run appended
    run_b = auth_client.post(runs_url, {'method': 'topsis'}, format='json')
    assert run_b.status_code == status.HTTP_201_CREATED, run_b.data
    assert run_b.data['id'] != run_a.data['id']

    # Prior run unchanged
    again = auth_client.get(f"{runs_url}{run_a.data['id']}/")
    assert again.data['input_snapshot'] == snap_a
    assert again.data['result'] == result_a

    # Immutability: patch/put/delete disallowed
    for method in ('patch', 'put', 'delete'):
        resp = getattr(auth_client, method)(
            f"{runs_url}{run_a.data['id']}/",
            {'result': {'x': 1}},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'run_immutable'

"""API tests for SAW-only runs (AC01, AC09–AC13, AC23–AC26)."""

from __future__ import annotations

import copy

import pytest
from rest_framework import status

from decision_support.models import DecisionRun

CASES = '/api/v1/projects/{project_id}/decision-cases/'


def _acceptance_payload(**overrides):
    data = {
        'title': 'SAW sample',
        'selected_methods': ['saw'],
        'criteria': ['تجربه', 'قیمت'],
        'alternatives': ['پیمانکار الف', 'پیمانکار ب'],
        'weights': [1, 1],
        'types': ['benefit', 'cost'],
        'performance_matrix': [[10, 100], [5, 200]],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_ac01_ac14_saw_only_run(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _acceptance_payload(), format='json')
    assert case.status_code == status.HTTP_201_CREATED, case.data
    run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'saw'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    assert run.data['method'] == 'saw'
    assert run.data['result']['status'] == 'ok'
    assert run.data['result']['engine'] == 'saw'
    ranking = run.data['result']['ranking']
    assert ranking[0]['option'] == 'پیمانکار الف'
    assert ranking[0]['score'] == pytest.approx(1.0)
    assert ranking[0]['rank'] == 1
    assert ranking[1]['option'] == 'پیمانکار ب'
    assert ranking[1]['score'] == pytest.approx(0.5)
    assert 'TOPSIS' not in run.data['result']
    assert 'topsis' not in run.data['result']
    assert 'weights_normalized' in run.data['input_snapshot']
    assert str(run.data['extracted_by']) == str(user.id)


@pytest.mark.django_db
def test_patch_ranking_fields_then_saw(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        {
            'title': 'Draft',
            'selected_methods': ['saw'],
            'criteria': ['c1', 'c2'],
            'alternatives': ['a1', 'a2'],
            'weights': [1, 1],
            'types': ['benefit', 'benefit'],
            'performance_matrix': [[1, 1], [1, 1]],
        },
        format='json',
    )
    assert case.status_code == status.HTTP_201_CREATED, case.data
    case_id = case.data['id']
    patch = auth_client.patch(
        f'{base}{case_id}/',
        {
            'weights': [1, 1],
            'types': ['benefit', 'cost'],
            'performance_matrix': [[10, 100], [5, 200]],
            'criteria': ['تجربه', 'قیمت'],
            'alternatives': ['پیمانکار الف', 'پیمانکار ب'],
        },
        format='json',
    )
    assert patch.status_code == status.HTTP_200_OK, patch.data
    run = auth_client.post(f'{base}{case_id}/runs/', {'method': 'saw'}, format='json')
    assert run.status_code == status.HTTP_201_CREATED, run.data
    assert run.data['result']['ranking'][0]['score'] == pytest.approx(1.0)


@pytest.mark.django_db
def test_ac09_cost_zero_no_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        _acceptance_payload(performance_matrix=[[10, 0], [5, 200]]),
        format='json',
    )
    # create may reject cost zero on case PATCH/POST if ranking validated
    if case.status_code == status.HTTP_201_CREATED:
        before = DecisionRun.objects.count()
        run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'saw'}, format='json')
        assert run.status_code == status.HTTP_400_BAD_REQUEST
        issues = run.data['error']['details'].get('issues', [])
        assert any(i.get('code') == 'cost_zero' for i in issues)
        assert DecisionRun.objects.count() == before
    else:
        assert case.status_code == status.HTTP_400_BAD_REQUEST
        issues = case.data['error']['details'].get('issues', [])
        assert any(i.get('code') == 'cost_zero' for i in issues)


@pytest.mark.django_db
def test_ac10_bad_weights_no_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    for weights in ([-1, 1], [0, 0]):
        case = auth_client.post(
            base,
            _acceptance_payload(title=f'w{weights}', weights=weights),
            format='json',
        )
        assert case.status_code == status.HTTP_400_BAD_REQUEST
        codes = {i.get('code') for i in case.data['error']['details'].get('issues', [])}
        assert codes & {'weight_negative', 'weights_all_zero'}


@pytest.mark.django_db
def test_ac13_benefit_all_zero_no_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        _acceptance_payload(
            title='zero benefit',
            weights=[0, 1],
            types=['benefit', 'cost'],
            performance_matrix=[[0, 100], [0, 200]],
        ),
        format='json',
    )
    if case.status_code == status.HTTP_201_CREATED:
        before = DecisionRun.objects.count()
        run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'saw'}, format='json')
        assert run.status_code == status.HTTP_400_BAD_REQUEST
        issues = run.data['error']['details'].get('issues', [])
        assert any(
            i.get('code') == 'benefit_column_all_zero' and i.get('path') == 'criteria.0' for i in issues
        )
        assert DecisionRun.objects.count() == before
    else:
        assert case.status_code == status.HTTP_400_BAD_REQUEST
        issues = case.data['error']['details'].get('issues', [])
        assert any(i.get('code') == 'benefit_column_all_zero' for i in issues)


@pytest.mark.django_db
def test_ac08_empty_cell_no_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(
        base,
        {
            'title': 'Incomplete matrix',
            'selected_methods': ['saw'],
            'criteria': ['c1'],
            'alternatives': ['a1'],
            'weights': [1],
            'types': ['benefit'],
            'performance_matrix': [],
        },
        format='json',
    )
    assert case.status_code == status.HTTP_201_CREATED
    before = DecisionRun.objects.count()
    run = auth_client.post(f"{base}{case.data['id']}/runs/", {'method': 'saw'}, format='json')
    assert run.status_code == status.HTTP_400_BAD_REQUEST
    assert run.data['error']['code'] == 'decision_input_invalid'
    assert DecisionRun.objects.count() == before


@pytest.mark.django_db
def test_ac23_ac24_saw_immutability(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _acceptance_payload(), format='json')
    case_id = case.data['id']
    runs_url = f'{base}{case_id}/runs/'
    run_a = auth_client.post(runs_url, {'method': 'saw'}, format='json')
    assert run_a.status_code == status.HTTP_201_CREATED, run_a.data
    snap_a = copy.deepcopy(run_a.data['input_snapshot'])
    result_a = copy.deepcopy(run_a.data['result'])

    patch = auth_client.patch(
        f'{base}{case_id}/',
        {'weights': [2, 1], 'performance_matrix': [[10, 100], [5, 200]]},
        format='json',
    )
    assert patch.status_code == status.HTTP_200_OK, patch.data
    run_b = auth_client.post(runs_url, {'method': 'saw'}, format='json')
    assert run_b.status_code == status.HTTP_201_CREATED, run_b.data
    assert run_b.data['id'] != run_a.data['id']

    again = auth_client.get(f"{runs_url}{run_a.data['id']}/")
    assert again.data['input_snapshot'] == snap_a
    assert again.data['result'] == result_a

    for method in ('patch', 'put', 'delete'):
        resp = getattr(auth_client, method)(
            f"{runs_url}{run_a.data['id']}/",
            {'result': {'x': 1}},
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data['error']['code'] == 'run_immutable'

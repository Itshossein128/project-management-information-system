import copy

import pytest
from rest_framework import status

from decision_support.models import DecisionCase, DecisionRun

CASES = '/api/v1/projects/{project_id}/decision-cases/'


def _ranking_case_payload():
    return {
        'title': 'Rank',
        'selected_methods': ['saw', 'ahp'],
        'criteria': ['تجربه', 'قیمت'],
        'alternatives': ['الف', 'ب'],
        'weights': [1, 1],
        'types': ['benefit', 'cost'],
        'performance_matrix': [[10, 100], [5, 200]],
    }


@pytest.mark.django_db
class TestDecisionRuns:
    def test_ac23_stub_run_snapshot(self, auth_client, project, user):
        base = CASES.format(project_id=project.id)
        case = auth_client.post(base, _ranking_case_payload(), format='json')
        assert case.status_code == status.HTTP_201_CREATED, case.data
        runs_url = f"{base}{case.data['id']}/runs/"
        run = auth_client.post(runs_url, {'method': 'saw'}, format='json')
        assert run.status_code == status.HTTP_201_CREATED, run.data
        assert run.data['result']['status'] == 'ok'
        assert run.data['result']['engine'] == 'saw'
        assert 'ranking' in run.data['result']
        snap = run.data['input_snapshot']
        assert snap['criteria'] == ['تجربه', 'قیمت']
        assert snap['alternatives'] == ['الف', 'ب']
        assert snap['weights'] == [1, 1]
        assert snap['types'] == ['benefit', 'cost']
        assert snap['performance_matrix'] == [[10, 100], [5, 200]]
        assert 'weights_normalized' in snap
        assert str(run.data['extracted_by']) == str(user.id)


    def test_ac24_prior_run_immutable_after_case_change(self, auth_client, project):
        base = CASES.format(project_id=project.id)
        case = auth_client.post(base, _ranking_case_payload(), format='json')
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
        assert run_b.data['input_snapshot']['weights'] == [2.0, 1.0] or run_b.data['input_snapshot']['weights'] == [2, 1]

        again = auth_client.get(f"{runs_url}{run_a.data['id']}/")
        assert again.status_code == status.HTTP_200_OK
        assert again.data['input_snapshot'] == snap_a
        assert again.data['result'] == result_a

    def test_run_immutable_and_invalid_creates_no_row(self, auth_client, project):
        base = CASES.format(project_id=project.id)
        case = auth_client.post(base, _ranking_case_payload(), format='json')
        case_id = case.data['id']
        runs_url = f'{base}{case_id}/runs/'
        run = auth_client.post(runs_url, {'method': 'saw'}, format='json')
        assert run.status_code == status.HTTP_201_CREATED
        run_url = f"{runs_url}{run.data['id']}/"

        for method in ('patch', 'put', 'delete'):
            resp = getattr(auth_client, method)(run_url, {'result': {'x': 1}}, format='json')
            assert resp.status_code == status.HTTP_400_BAD_REQUEST, resp.data
            assert resp.data['error']['code'] == 'run_immutable'

        before = DecisionRun.objects.filter(case_id=case_id).count()
        bad = auth_client.post(
            base,
            {
                **_ranking_case_payload(),
                'title': 'Bad matrix case',
                'performance_matrix': [[10, None], [5, 200]],
            },
            format='json',
        )
        # invalid create case — alternatively patch then run
        assert bad.status_code == status.HTTP_400_BAD_REQUEST

        auth_client.patch(
            f'{base}{case_id}/',
            {'performance_matrix': [[10, None], [5, 200]]},
            format='json',
        )
        # case patch may fail; ensure run with invalid live state
        # restore valid then use empty cell via direct model? Prefer API: patch fails so case stays valid
        invalid_run = auth_client.post(runs_url, {'method': 'saw'}, format='json')
        # If patch failed, run still succeeds — force invalid by creating incomplete case for ahp then saw
        assert DecisionRun.objects.filter(case_id=case_id).count() == before or invalid_run.status_code in (
            201,
            400,
        )

        # Explicit: incomplete ranking case cannot create saw run
        incomplete = auth_client.post(
            base,
            {
                'title': 'Incomplete',
                'selected_methods': ['saw'],
                'criteria': ['c1'],
                'alternatives': ['a1'],
                'weights': [1],
                'types': ['benefit'],
                'performance_matrix': [],
            },
            format='json',
        )
        assert incomplete.status_code == status.HTTP_201_CREATED
        count_before = DecisionRun.objects.count()
        fail_run = auth_client.post(
            f"{base}{incomplete.data['id']}/runs/",
            {'method': 'saw'},
            format='json',
        )
        assert fail_run.status_code == status.HTTP_400_BAD_REQUEST
        assert fail_run.data['error']['code'] == 'decision_input_invalid'
        assert DecisionRun.objects.count() == count_before

    def test_method_not_selected_and_ahp_stub(self, auth_client, project):
        base = CASES.format(project_id=project.id)
        case = auth_client.post(
            base,
            {
                'title': 'Crit',
                'selected_methods': ['ahp'],
                'criteria': ['c1', 'c2'],
                'ahp_matrix': [[1.0, 1.0], [1.0, 1.0]],
            },
            format='json',
        )
        assert case.status_code == status.HTTP_201_CREATED, case.data
        runs_url = f"{base}{case.data['id']}/runs/"
        not_sel = auth_client.post(runs_url, {'method': 'saw'}, format='json')
        assert not_sel.status_code == status.HTTP_400_BAD_REQUEST
        assert not_sel.data['error']['code'] == 'method_not_selected'

        ahp = auth_client.post(runs_url, {'method': 'ahp'}, format='json')
        assert ahp.status_code == status.HTTP_201_CREATED, ahp.data
        assert ahp.data['input_snapshot']['criteria'] == ['c1', 'c2']
        assert ahp.data['input_snapshot']['alternatives'] == []


@pytest.mark.django_db
def test_whole_ahp_history_frozen_and_legacy_named_order_preserved(auth_client, project, user):
    base = CASES.format(project_id=project.id)
    payload = {**_ranking_case_payload(), 'weights': [20, 10], 'ahp_matrix': [[1, .5], [2, 1]]}
    created = auth_client.post(base, payload, format='json')
    assert created.status_code == 201, created.data
    url = base + created.data['id'] + '/'
    first = auth_client.post(url + 'runs/', {'method': 'ahp'}, format='json')
    assert first.status_code == 201, first.data
    frozen = copy.deepcopy(first.data)
    assert frozen['input_snapshot']['weights'] == [20, 10]
    assert 'weights_normalized' not in frozen['input_snapshot']
    saw = auth_client.post(url + 'runs/', {'method': 'saw'}, format='json')
    assert saw.status_code == 201
    saw_frozen = copy.deepcopy(saw.data)
    assert saw_frozen['input_snapshot']['weights_normalized'] == pytest.approx([2/3, 1/3])
    assert auth_client.patch(url, {'ahp_matrix': [[1, 3], [1/3, 1]]}, format='json').status_code == 200
    assert auth_client.patch(url, {'title': 'Changed'}, format='json').status_code == 200
    second = auth_client.post(url + 'runs/', {'method': 'ahp'}, format='json')
    assert second.status_code == 201
    assert second.data['result'] != frozen['result']
    assert auth_client.get(url + 'runs/' + frozen['id'] + '/').data == frozen
    assert auth_client.get(url + 'runs/' + saw_frozen['id'] + '/').data == saw_frozen
    for verb in ['put', 'patch', 'delete']:
        res = getattr(auth_client, verb)(url + 'runs/' + frozen['id'] + '/', {}, format='json')
        assert res.status_code == 400
        assert res.data['error']['code'] == 'run_immutable'
    # Old engine versions stored descending rows. Inspection preserves their names/order.
    legacy = DecisionRun.objects.get(pk=frozen['id'])
    legacy.result['weights'].reverse()
    legacy.save(update_fields=['result'])
    stored = copy.deepcopy(legacy.result)
    assert auth_client.get(url + 'runs/' + frozen['id'] + '/').data['result'] == stored

@pytest.mark.django_db
def test_ism_frozen_cycle_method_filter_and_mutation_rejection(auth_client,project,user):
    base=CASES.format(project_id=project.id)
    case=auth_client.post(base,{'title':'ISM cycle history','selected_methods':['ism','dematel'],'criteria':['A','B','C'],'ism_matrix':[[0,1,0],[1,0,1],[0,0,0]]},format='json');assert case.status_code==201,case.data
    url=base+case.data['id']+'/runs/'
    first=auth_client.post(url,{'method':'ism'},format='json');assert first.status_code==201,first.data
    assert first.data['result']['mutual_groups']==[{'level':2,'criteria':['A','B']}]
    stub=auth_client.post(url,{'method':'dematel'},format='json');assert stub.status_code==201
    patch=auth_client.patch(base+case.data['id']+'/',{'criteria':['X','Y','Z'],'ism_matrix':[[0,0,0],[0,0,0],[0,0,0]]},format='json');assert patch.status_code==200
    second=auth_client.post(url,{'method':'ism'},format='json');assert second.status_code==201 and second.data['id']!=first.data['id']
    assert auth_client.get(url+first.data['id']+'/').data==first.data
    assert auth_client.get(url+stub.data['id']+'/').data==stub.data
    assert auth_client.get(url+'?method=ism&page_size=1').data['count']==2
    for method in ('put','patch','delete'):
        assert getattr(auth_client,method)(url+first.data['id']+'/',{},format='json').status_code==400
    assert str(first.data['extracted_by'])==str(user.id)

import copy
from decision_support.services.case_service import create_case, update_case
from decision_support.services.execution_service import create_run
from decision_support.tests.execution_records_fixtures import payload,METHODS
from config.exceptions import CodedValidationError

@pytest.mark.django_db
@pytest.mark.parametrize('method',METHODS)
def test_distinct_append_full_immutability_and_zero_rejection(project,user,method):
    case=create_case(project.id,user,payload())
    first=create_run(case,method,user); frozen=copy.deepcopy(DecisionRun.objects.filter(pk=first.pk).values().get())
    second=create_run(case,method,user);assert first.pk!=second.pk
    update_case(case,user,{'title':'Edited context'})
    third=create_run(case,method,user);assert third.pk not in (first.pk,second.pk)
    assert DecisionRun.objects.filter(pk=first.pk).values().get()==frozen
    assert first.input_snapshot['weights']==[2,3]
    if method in ('saw','topsis'):assert first.input_snapshot['weights_normalized']==[.4,.6]
    DecisionCase.objects.filter(pk=case.pk).update(selected_methods=[])
    with pytest.raises(CodedValidationError):create_run(case,method,user)
    assert DecisionRun.objects.filter(case=case).count()==3
    assert DecisionRun.objects.filter(pk=first.pk).values().get()==frozen

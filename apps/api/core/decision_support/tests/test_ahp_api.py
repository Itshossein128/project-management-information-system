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
    assert DecisionRun.objects.filter(case_id=case_id).count() == 1
    assert run.data['result']['lambda_max'] == pytest.approx(6.2)
    assert run.data['result']['ci'] == pytest.approx(1.6)
    assert run.data['result']['cr'] == pytest.approx(1.6/.58)
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

@pytest.fixture
def ahp_access(project, user, other_user, viewer_role):
    from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
    from projects.services import create_project_with_creator
    from rest_framework.test import APIClient
    reader = APIClient()
    reader.force_authenticate(other_user)
    member = ProjectMember.objects.create(project=project, user=other_user, status=MemberStatus.ACTIVE)
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    foreign = create_project_with_creator(
        creator=user, project_code='AHP-OTHER', project_name='Other AHP',
        employer='Test', start_date='2026-01-01')
    return reader, foreign


@pytest.mark.django_db
def test_ahp_snapshot_actor_and_view_edit_permissions(auth_client, project, user, ahp_access):
    reader, foreign = ahp_access
    base = CASES.format(project_id=project.id)
    payload = _ahp_payload()
    case = auth_client.post(base, payload, format='json')
    assert case.status_code == 201, case.data
    url = f"{base}{case.data['id']}/"
    assert reader.get(url).status_code == 200
    assert reader.post(url + 'runs/', {'method': 'ahp'}, format='json').status_code == 403
    assert auth_client.get(CASES.format(project_id=foreign.id) + case.data['id'] + '/').status_code == 404
    run = auth_client.post(url + 'runs/', {'method': 'ahp'}, format='json')
    assert run.status_code == 201, run.data
    assert str(run.data['extracted_by']) == str(user.id)
    assert run.data['extracted_at']
    for key in ('criteria', 'ahp_matrix', 'alternatives', 'weights', 'types', 'performance_matrix'):
        assert run.data['input_snapshot'][key] == payload[key]
    before = run.data['input_snapshot']
    auth_client.patch(url, {'title': 'Edited'}, format='json')
    fetched = auth_client.get(url + f"runs/{run.data['id']}/")
    assert fetched.data['input_snapshot'] == before

@pytest.mark.django_db
@pytest.mark.parametrize('matrix,code,path', [
    ([[1.00005]], 'ahp_diagonal_invalid', 'ahp_matrix.0.0'),
    ([['1']], 'non_numeric', 'ahp_matrix.0.0'),
    ([[True]], 'non_numeric', 'ahp_matrix.0.0'),
    ([[None]], 'cell_empty', 'ahp_matrix.0.0'),
    ([[0]], 'cell_non_positive', 'ahp_matrix.0.0'),
    ([], 'dimension_invalid', 'ahp_matrix'),
])
def test_strict_http_error_envelope_no_run(auth_client, project, matrix, code, path):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(criteria=['A'], ahp_matrix=matrix), format='json')
    assert case.status_code == 201, case.data
    url = base + case.data['id'] + '/runs/'
    messages = []
    for lang in ['en', 'fa']:
        run = auth_client.post(url, {'method': 'ahp'}, format='json', HTTP_ACCEPT_LANGUAGE=lang)
        assert run.status_code == 400, run.data
        assert run.data['error']['code'] == 'decision_input_invalid'
        issues = run.data['error']['details']['issues']
        assert any(i['code'] == code and i['path'] == path and i['message'] for i in issues)
        messages.append(next(i['message'] for i in issues if i['code'] == code))
    assert messages[0] != messages[1]
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()


@pytest.mark.django_db
def test_run_nonmember_foreign_ids_and_invalid_method(auth_client, project, other_user, ahp_access):
    from rest_framework.test import APIClient
    reader, foreign = ahp_access
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(), format='json')
    runs = base + case.data['id'] + '/runs/'
    invalid = auth_client.post(runs, {'method': 'unknown'}, format='json')
    assert invalid.status_code == 400
    assert invalid.data['error']['details']['issues'][0]['code'] == 'invalid_method'
    reader.get(CASES.format(project_id=foreign.id))  # viewer is a nonmember there
    for verb in ['get', 'post']:
        resp = getattr(reader, verb)(CASES.format(project_id=foreign.id) + case.data['id'] + '/runs/')
        assert resp.status_code == 403
    anonymous = APIClient()
    assert anonymous.get(runs).status_code in (401, 403)
    assert auth_client.post(CASES.format(project_id=foreign.id) + case.data['id'] + '/runs/',
                            {'method': 'ahp'}, format='json').status_code == 404
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()


@pytest.mark.django_db
def test_nonfinite_json_is_parser_rejection(auth_client, project):
    response = auth_client.post(CASES.format(project_id=project.id),
        '{"title":"bad","criteria":["A"],"ahp_matrix":[[NaN]]}', content_type='application/json')
    assert response.status_code == 400
    assert response.data['error']['code'] == 'parse_error'


@pytest.mark.django_db
@pytest.mark.parametrize('incomplete', [False, True])
def test_matrix_only_patch_preserves_raw_ranking_drafts(auth_client, project, incomplete):
    import copy
    from decision_support.models import DecisionCase
    base = CASES.format(project_id=project.id)
    created = auth_client.post(base, _ahp_payload(), format='json')
    case = DecisionCase.objects.get(pk=created.data['id'])
    raw = {'selected_methods': ['saw', 'ahp'], 'alternatives': ['X', 'Y'],
           'weights': ['10', '20', '30'], 'types': ['benefit', 'cost', 'benefit'],
           'performance_matrix': [[2, None if incomplete else 3, 4], [4, 5, 6]],
           'dematel_matrix': [[4]], 'ism_matrix': [[9]]}
    DecisionCase.objects.filter(pk=case.pk).update(**copy.deepcopy(raw))
    new_matrix = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    changed = auth_client.patch(base + str(case.pk) + '/', {'ahp_matrix': new_matrix}, format='json')
    assert changed.status_code == 200, changed.data
    case.refresh_from_db()
    assert {key: getattr(case, key) for key in raw} == raw
    run = auth_client.post(base + str(case.pk) + '/runs/', {'method': 'ahp'}, format='json')
    assert run.status_code == 201, run.data
    assert {key: run.data['input_snapshot'][key] for key in raw} == raw
    assert 'weights_normalized' not in run.data['input_snapshot']
    # A real shared criteria change must still validate existing ranking dimensions.
    invalid = auth_client.patch(base + str(case.pk) + '/', {'criteria': ['A', 'B']}, format='json')
    assert invalid.status_code == 400
    case.refresh_from_db()
    assert case.criteria == _ahp_payload()['criteria']


@pytest.mark.django_db
def test_targeted_save_does_not_overwrite_unrelated_stale_fields(project, user):
    from decision_support.models import DecisionCase
    from decision_support.services.case_service import update_case
    case = DecisionCase.objects.create(project=project, created_by=user, updated_by=user, **_ahp_payload())
    DecisionCase.objects.filter(pk=case.pk).update(title='Newer title', weights=[42])
    update_case(case, user, {'ahp_matrix': [[1]]})
    case.refresh_from_db()
    assert case.title == 'Newer title'
    assert case.weights == [42]


@pytest.mark.django_db
def test_method_filter_before_pagination_and_scoped_run_ids(auth_client, project, user, ahp_access):
    from django.utils import timezone
    reader, foreign = ahp_access
    base = CASES.format(project_id=project.id)
    created = auth_client.post(base, _ahp_payload(selected_methods=['ahp', 'dematel']), format='json')
    case_id = created.data['id']
    url = base + case_id + '/runs/'
    run = auth_client.post(url, {'method': 'ahp'}, format='json')
    assert run.status_code == 201
    first = run.data['id']
    auth_client.post(url, {'method': 'dematel'}, format='json')
    auth_client.post(url, {'method': 'ahp'}, format='json')
    filtered = auth_client.get(url + '?method=ahp&page_size=1')
    assert filtered.status_code == 200
    assert filtered.data['count'] == 2
    assert filtered.data['next']
    assert [row['method'] for row in filtered.data['results']] == ['ahp']
    second = auth_client.get(url + '?method=ahp&page_size=1&page=2')
    assert second.data['results'][0]['id'] == first
    assert auth_client.get(url).data['count'] == 3
    for method in ['', 'unknown']:
        bad = auth_client.get(url + '?method=' + method + '&page=999')
        assert bad.status_code == 400
        assert bad.data['error']['code'] == 'decision_input_invalid'
        assert bad.data['error']['details']['issues'][0]['path'] == 'method'
    assert reader.get(url + '?method=ahp').status_code == 200
    # Defensive double scope: inconsistent case/project relation must not leak.
    corrupt = DecisionRun.objects.create(case_id=case_id, project=foreign, method='ahp',
        input_snapshot={}, result={}, extracted_at=timezone.now(), extracted_by=user)
    assert auth_client.get(url).data['count'] == 3
    assert auth_client.get(url + str(corrupt.pk) + '/').status_code == 404
    foreign_url = CASES.format(project_id=foreign.id) + case_id + '/runs/' + first + '/'
    for verb in ['get', 'patch', 'put', 'delete']:
        response = getattr(auth_client, verb)(foreign_url)
        assert response.status_code == 404


@pytest.mark.django_db
def test_json_numeric_exponent_overflow_is_coded_before_draft_storage(auth_client, project):
    response = auth_client.post(CASES.format(project_id=project.id),
        '{"title":"range","selected_methods":["ahp"],"criteria":["A"],"ahp_matrix":[[1e400]]}',
        content_type='application/json')
    assert response.status_code == 400, response.data
    assert response.data['error']['code'] == 'decision_input_invalid'
    assert response.data['error']['details']['issues'][0]['code'] == 'non_finite'
    assert response.data['error']['details']['issues'][0]['path'] == 'ahp_matrix.0.0'


@pytest.mark.django_db
def test_representable_extreme_calculation_persists_frozen_run(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(criteria=['A', 'B', 'C'], ahp_matrix=[
        [1, 1e308, 1e-308], [1e-308, 1, 1e308], [1e308, 1e-308, 1]]), format='json')
    assert case.status_code == 201, case.data
    run = auth_client.post(base + case.data['id'] + '/runs/', {'method': 'ahp'}, format='json')
    assert run.status_code == 201, run.data
    assert run.data['result']['lambda_max'] == pytest.approx(1e308, rel=1e-12)
    assert run.data['result']['ci'] == pytest.approx(5e307, rel=1e-12)
    assert run.data['result']['cr'] == pytest.approx(5e307/.58, rel=1e-12)
    assert run.data['result']['is_consistent'] is False
    assert DecisionRun.objects.filter(case_id=case.data['id']).count() == 1
    # Compare persisted JSONB before/after; large numeric notation is canonicalized.
    frozen = auth_client.get(base + case.data['id'] + '/runs/' + run.data['id'] + '/').data
    assert float(frozen['result']['lambda_max']) == pytest.approx(1e308, rel=1e-12)
    assert auth_client.patch(base + case.data['id'] + '/', {'ahp_matrix': [[1]*3 for _ in range(3)]}, format='json').status_code == 200
    assert auth_client.get(base + case.data['id'] + '/runs/' + run.data['id'] + '/').data == frozen


@pytest.mark.django_db
@pytest.mark.parametrize('criteria,matrix', [
    ([], []), ([str(i) for i in range(11)], []),
    ({'A': 1}, [[1]]), (['A'], {'row': [1]}), (['A'], [1]),
])
def test_convergence_api_structural_errors_fully_localized(auth_client, project, criteria, matrix):
    from decision_support.models import DecisionCase
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(), format='json')
    DecisionCase.objects.filter(pk=case.data['id']).update(criteria=criteria, ahp_matrix=matrix)
    observed = []
    for lang in ['en', 'fa']:
        response = auth_client.post(base + case.data['id'] + '/runs/', {'method': 'ahp'},
                                    format='json', HTTP_ACCEPT_LANGUAGE=lang)
        assert response.status_code == 400
        observed.append(response.data['error']['details']['issues'])
    assert [(i['code'], i['path']) for i in observed[0]] == [(i['code'], i['path']) for i in observed[1]]
    assert all(en['message'] != fa['message'] for en, fa in zip(*observed))
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('action', ['execute', 'history', 'selected_methods'])
def test_convergence_unknown_methods_localized(auth_client, project, action):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(), format='json')
    url = base + case.data['id'] + '/'
    observed = []
    for lang in ['en', 'fa']:
        if action == 'execute':
            response = auth_client.post(url + 'runs/', {'method': 'unknown'}, format='json', HTTP_ACCEPT_LANGUAGE=lang)
        elif action == 'history':
            response = auth_client.get(url + 'runs/?method=unknown', HTTP_ACCEPT_LANGUAGE=lang)
        else:
            response = auth_client.patch(url, {'selected_methods': ['unknown']}, format='json', HTTP_ACCEPT_LANGUAGE=lang)
        assert response.status_code == 400
        observed.append(response.data['error']['details']['issues'])
    assert [(i['code'], i['path']) for i in observed[0]] == [(i['code'], i['path']) for i in observed[1]]
    assert all(en['message'] != fa['message'] for en, fa in zip(*observed))
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()


@pytest.mark.django_db
def test_unrepresentable_weights_http_error_no_record(auth_client, project):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(criteria=['A','B','C'], ahp_matrix=[
        [1,1e308,1e308], [1e-308,1,1e308], [1e-308,1e-308,1]]), format='json')
    assert case.status_code == 201
    run = auth_client.post(base + case.data['id'] + '/runs/', {'method':'ahp'}, format='json')
    assert run.status_code == 400
    assert run.data['error']['details']['issues'][0]['code'] == 'non_finite'
    assert run.data['error']['details']['issues'][0]['path'] == 'ahp_matrix'
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('matrix', [[], [[1]], [[1,2],[.5]], [1,[.5,1]], {'row':[1]}, [[1,2,3],[.5,1]]])
def test_convergence_shape_api_root_localized_no_run(auth_client, project, matrix):
    base = CASES.format(project_id=project.id)
    case = auth_client.post(base, _ahp_payload(criteria=['A','B'], ahp_matrix=matrix), format='json')
    assert case.status_code == 201
    messages = []
    for lang in ['en', 'fa']:
        response = auth_client.post(base + case.data['id'] + '/runs/', {'method':'ahp'}, format='json', HTTP_ACCEPT_LANGUAGE=lang)
        assert response.status_code == 400
        issues = response.data['error']['details']['issues']
        root = next((i for i in issues if i['code'] == 'dimension_invalid' and i['path'] == 'ahp_matrix'), None)
        assert root is not None
        messages.append(root['message'])
    assert messages[0] != messages[1]
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()

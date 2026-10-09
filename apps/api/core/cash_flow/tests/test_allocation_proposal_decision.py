from datetime import date
from decimal import Decimal

import pytest

from cost_control.models import Commitment, CommitmentStatus


def _score(client, project_id, urgency, return_score, recovery, risk):
    return client.put(
        f'/api/v1/projects/{project_id}/cash-flow/priority-score/',
        {
            'urgency': urgency,
            'return_score': return_score,
            'recovery_speed': recovery,
            'risk': risk,
        },
        format='json',
    )


@pytest.mark.django_db
def test_priority_score_composite(auth_client, project, user):
    # (80+60+70+(100-40))/4 = 67.5
    resp = _score(auth_client, project.id, 80, 60, 70, 40)
    assert resp.status_code == 200
    assert resp.data['composite'] == 67.5

    get_resp = auth_client.get(f'/api/v1/projects/{project.id}/cash-flow/priority-score/')
    assert get_resp.status_code == 200
    assert get_resp.data['urgency'] == 80.0


@pytest.mark.django_db
def test_score_out_of_range_rejected(auth_client, project):
    resp = _score(auth_client, project.id, 101, 50, 50, 50)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_propose_ranks_by_composite_and_respects_pool(
    auth_client, project, second_project, user, wbs, approved_ipc, approved_commitment
):
    # Project A (project): higher composite, need from fixtures = -400k → no positive need
    # Create positive need on second_project: commitment only
    Commitment.objects.create(
        project=second_project,
        commitment_number='CF-CM-B',
        amount=Decimal('2000000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 15),
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    # Positive need on project: add larger commitment
    Commitment.objects.create(
        project=project,
        commitment_number='CF-CM-EXTRA',
        amount=Decimal('3000000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 18),
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )

    _score(auth_client, project.id, 90, 90, 90, 10)  # composite high
    _score(auth_client, second_project.id, 50, 50, 50, 50)  # lower

    cycle = auth_client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': '2026-Q4',
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'available_liquidity': '5000000',
            'currency': 'IRR',
        },
        format='json',
    )
    assert cycle.status_code == 201, cycle.content
    cid = cycle.data['id']

    propose = auth_client.post(f'/api/v1/cash-flow/portfolio/cycles/{cid}/propose/')
    assert propose.status_code == 200, propose.content
    lines = propose.data['lines']
    assert len(lines) >= 1
    assert lines[0]['rank'] == 1
    # Higher composite project first among those with positive need
    assert lines[0]['project_id'] == str(project.id)
    total = sum(l['suggested_amount'] for l in lines)
    assert total <= 5000000.0


@pytest.mark.django_db
def test_incomplete_scores_in_warnings(auth_client, project, second_project, user, wbs):
    Commitment.objects.create(
        project=project,
        commitment_number='CF-CM-W',
        amount=Decimal('1000000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 15),
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    _score(auth_client, project.id, 80, 60, 70, 40)
    # second_project has no score

    cycle = auth_client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': 'warn-cycle',
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'available_liquidity': '1000000',
        },
        format='json',
    )
    propose = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cycle.data["id"]}/propose/'
    )
    assert propose.status_code == 200
    assert str(second_project.id) in propose.data['warnings']['incomplete_score_projects']


@pytest.mark.django_db
def test_zero_liquidity_empty_proposal(auth_client, project):
    _score(auth_client, project.id, 80, 60, 70, 40)
    cycle = auth_client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': 'zero',
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'available_liquidity': '0',
        },
        format='json',
    )
    propose = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cycle.data["id"]}/propose/'
    )
    assert propose.status_code == 200
    assert propose.data['lines'] == []
    assert propose.data['message'] == 'no_available_liquidity'


@pytest.mark.django_db
def test_decision_requires_owner_and_rationale(auth_client, project, user):
    cycle = auth_client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': 'dec',
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'available_liquidity': '1000',
        },
        format='json',
    )
    cid = cycle.data['id']
    bad = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        {'owner_id': str(user.id), 'rationale': '', 'lines': []},
        format='json',
    )
    assert bad.status_code == 400

    no_owner = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        {'rationale': 'Because we must', 'lines': []},
        format='json',
    )
    assert no_owner.status_code == 400

    ok = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        {
            'owner_id': str(user.id),
            'rationale': 'Prioritize concrete pour',
            'lines': [
                {
                    'project_id': str(project.id),
                    'amount': 500,
                    'period_start': '2026-10-01',
                    'period_end': '2026-10-31',
                    'schedule_impact': 'Keeps path',
                    'cost_impact': 'Avoids idle',
                }
            ],
        },
        format='json',
    )
    assert ok.status_code == 201, ok.content
    assert ok.data['rationale'] == 'Prioritize concrete pour'
    assert ok.data['owner_id'] == str(user.id)

from datetime import date
from decimal import Decimal

import pytest

from cost_control.models import Commitment, CommitmentStatus


def _create_cycle(client, liquidity='5000000'):
    return client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': 'overlap-cycle',
            'period_start': '2026-10-01',
            'period_end': '2026-12-31',
            'available_liquidity': liquidity,
        },
        format='json',
    )


def _decision_body(user_id, project_id, acknowledge=False):
    return {
        'owner_id': str(user_id),
        'rationale': 'First allocation decision with clear rationale text',
        'acknowledge_overlap': acknowledge,
        'lines': [
            {
                'project_id': str(project_id),
                'amount': 1000000,
                'period_start': '2026-10-01',
                'period_end': '2026-10-31',
                'schedule_impact': 'path',
                'cost_impact': 'crew',
            }
        ],
    }


@pytest.mark.django_db
def test_overlap_without_ack_rejected(auth_client, project, user):
    cycle = _create_cycle(auth_client)
    cid = cycle.data['id']
    first = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        _decision_body(user.id, project.id),
        format='json',
    )
    assert first.status_code == 201, first.content

    second = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        _decision_body(user.id, project.id, acknowledge=False),
        format='json',
    )
    assert second.status_code == 400
    body = second.json()
    assert 'overlapping_allocation' in str(body)


@pytest.mark.django_db
def test_overlap_with_ack_accepted(auth_client, project, user):
    cycle = _create_cycle(auth_client)
    cid = cycle.data['id']
    first = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        _decision_body(user.id, project.id),
        format='json',
    )
    assert first.status_code == 201

    second = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        _decision_body(user.id, project.id, acknowledge=True),
        format='json',
    )
    assert second.status_code == 201, second.content
    assert second.data['acknowledge_overlap'] is True


@pytest.mark.django_db
def test_simulation_compare_diffs(auth_client, project, user, wbs):
    Commitment.objects.create(
        project=project,
        commitment_number='SIM-CM',
        amount=Decimal('2000000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 15),
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    auth_client.put(
        f'/api/v1/projects/{project.id}/cash-flow/priority-score/',
        {'urgency': 80, 'return_score': 60, 'recovery_speed': 70, 'risk': 40},
        format='json',
    )
    cycle = _create_cycle(auth_client)
    cid = cycle.data['id']
    propose = auth_client.post(f'/api/v1/cash-flow/portfolio/cycles/{cid}/propose/')
    assert propose.status_code == 200

    sim = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/simulations/',
        {
            'name': 'alt',
            'lines': [{'project_id': str(project.id), 'amount': 500000}],
        },
        format='json',
    )
    assert sim.status_code == 201, sim.content
    sid = sim.data['id']

    compare = auth_client.get(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/simulations/{sid}/compare/'
    )
    assert compare.status_code == 200
    assert 'diffs' in compare.data
    assert any(d['project_id'] == str(project.id) for d in compare.data['diffs'])

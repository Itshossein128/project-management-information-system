from datetime import date
from decimal import Decimal

import pytest

from cost_control.models import Commitment, CommitmentStatus
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole


@pytest.mark.django_db
def test_portfolio_report_membership_and_projection(
    auth_client, project, second_project, user, outsider_user, approved_ipc, approved_commitment, wbs
):
    Commitment.objects.create(
        project=second_project,
        commitment_number='REP-CM',
        amount=Decimal('500000'),
        commitment_date=date(2026, 10, 1),
        due_date=date(2026, 10, 10),
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

    cycle = auth_client.post(
        '/api/v1/cash-flow/portfolio/cycles/',
        {
            'name': 'report-cycle',
            'period_start': '2026-10-01',
            'period_end': '2026-10-31',
            'available_liquidity': '3000000',
        },
        format='json',
    )
    cid = cycle.data['id']
    decision = auth_client.post(
        f'/api/v1/cash-flow/portfolio/cycles/{cid}/decisions/',
        {
            'owner_id': str(user.id),
            'rationale': 'Allocate to Acme for October liquidity gap',
            'lines': [
                {
                    'project_id': str(project.id),
                    'amount': 2000000,
                    'period_start': '2026-10-01',
                    'period_end': '2026-10-31',
                }
            ],
        },
        format='json',
    )
    assert decision.status_code == 201, decision.content

    report = auth_client.get(
        '/api/v1/cash-flow/portfolio/report/?from=2026-10&to=2026-10'
        f'&cycle_id={cid}'
    )
    assert report.status_code == 200
    pids = {p['project_id'] for p in report.data['projects']}
    assert str(project.id) in pids
    assert str(second_project.id) in pids
    assert any(a['decision_id'] == str(decision.data['id']) for a in report.data['allocations'])

    # outsider with no membership sees empty
    auth_client.force_authenticate(user=outsider_user)
    empty = auth_client.get('/api/v1/cash-flow/portfolio/report/?from=2026-10&to=2026-10')
    assert empty.status_code == 200
    assert empty.data['projects'] == []


@pytest.mark.django_db
def test_report_excludes_non_member_project(
    auth_client, project, second_project, outsider_user, project_manager_role, approved_ipc
):
    m = ProjectMember.objects.create(
        project=project,
        user=outsider_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=m, role=project_manager_role)
    auth_client.force_authenticate(user=outsider_user)
    report = auth_client.get('/api/v1/cash-flow/portfolio/report/?from=2026-10&to=2026-10')
    assert report.status_code == 200
    pids = {p['project_id'] for p in report.data['projects']}
    assert str(project.id) in pids
    assert str(second_project.id) not in pids

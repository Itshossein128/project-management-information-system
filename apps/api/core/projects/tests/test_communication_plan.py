"""FR-COL US4: communication plan CRUD and stakeholder matrix."""

import pytest

from projects.models import Stakeholder


@pytest.mark.django_db
def test_communication_plan_create_and_list(auth_client, project, user):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/communication-plans/',
        {
            'audience': 'Employer team',
            'message': 'Monthly KPI pack',
            'channel_type': 'report',
            'frequency': 'monthly',
            'owner': str(user.id),
            'status': 'active',
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    plan_id = create.json()['id']

    listing = auth_client.get(f'/api/v1/projects/{project.id}/communication-plans/')
    assert listing.status_code == 200
    rows = listing.json()
    if isinstance(rows, dict):
        rows = rows.get('results', rows)
    assert any(r['id'] == plan_id for r in rows)
    row = next(r for r in rows if r['id'] == plan_id)
    assert row['audience'] == 'Employer team'
    assert row['message'] == 'Monthly KPI pack'
    assert row['frequency'] == 'monthly'


@pytest.mark.django_db
def test_stakeholder_influence_interest_matrix(auth_client, project, user):
    s1 = Stakeholder.objects.create(
        project=project,
        name='High Power',
        influence=5,
        interest=4,
        created_by=user,
        updated_by=user,
    )
    Stakeholder.objects.create(
        project=project,
        name='Low Power',
        influence=2,
        interest=2,
        created_by=user,
        updated_by=user,
    )

    resp = auth_client.get(f'/api/v1/projects/{project.id}/stakeholders/matrix/')
    assert resp.status_code == 200
    cells = resp.json()['cells']
    assert isinstance(cells, list)
    cell_5_4 = next(
        (c for c in cells if c.get('influence') == 5 and c.get('interest') == 4),
        None,
    )
    assert cell_5_4 is not None
    names = {s['name'] for s in cell_5_4['stakeholders']}
    assert 'High Power' in names
    ids = {s['id'] for s in cell_5_4['stakeholders']}
    assert str(s1.id) in ids

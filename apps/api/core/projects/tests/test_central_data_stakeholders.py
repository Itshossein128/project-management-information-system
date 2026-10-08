import pytest

from projects.models import Stakeholder


@pytest.mark.django_db
def test_stakeholder_crud(auth_client, project):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {
            'name': 'Ali',
            'organization_name': 'Employer',
            'role': 'Owner',
            'influence': 4,
            'interest': 5,
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    sid = create.json()['id']
    listing = auth_client.get(f'/api/v1/projects/{project.id}/stakeholders/')
    assert listing.status_code == 200
    rows = listing.json()
    if isinstance(rows, dict):
        rows = rows.get('results', rows)
    assert any(r['id'] == sid for r in rows)
    assert Stakeholder.objects.filter(pk=sid, is_deleted=False).exists()


@pytest.mark.django_db
def test_stakeholder_influence_validation(auth_client, project):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/stakeholders/',
        {'name': 'Bad', 'influence': 9},
        format='json',
    )
    assert resp.status_code == 400

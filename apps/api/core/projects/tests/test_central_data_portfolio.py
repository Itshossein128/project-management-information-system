import pytest

from projects.services import create_project_with_creator


@pytest.mark.django_db
def test_portfolio_summary_two_projects(auth_client, user, project_manager_role):
    create_project_with_creator(
        creator=user,
        project_code='PF-1',
        project_name='First',
        employer='E',
        start_date='2024-01-01',
    )
    create_project_with_creator(
        creator=user,
        project_code='PF-2',
        project_name='Second',
        employer='E',
        start_date='2024-01-01',
    )
    resp = auth_client.get('/api/v1/portfolio/summary/')
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data['totals']['project_count'] >= 2
    assert len(data['projects']) >= 2

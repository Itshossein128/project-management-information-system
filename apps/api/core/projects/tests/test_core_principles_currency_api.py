"""US3: project currency field."""
import pytest

from projects.models import ProjectCurrency


@pytest.mark.django_db
def test_project_default_currency_irr(auth_client, project):
    resp = auth_client.get(f'/api/v1/projects/{project.id}/')
    assert resp.status_code == 200
    assert resp.json().get('currency') == ProjectCurrency.IRR


@pytest.mark.django_db
def test_project_accepts_irt_currency(auth_client, project):
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/',
        {'currency': 'IRT'},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()['currency'] == 'IRT'


@pytest.mark.django_db
def test_create_project_with_currency(auth_client, user):
    resp = auth_client.post(
        '/api/v1/projects/',
        {
            'project_code': 'CUR-1',
            'project_name': 'Currency Proj',
            'employer': 'Emp',
            'start_date': '2024-01-01',
            'currency': 'IRT',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    # create response may be nested — fetch detail
    pid = body.get('id') or body.get('project_id')
    detail = auth_client.get(f'/api/v1/projects/{pid}/')
    assert detail.json()['currency'] == 'IRT'

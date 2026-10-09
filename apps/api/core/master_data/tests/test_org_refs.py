import pytest

from master_data.models import OrganizationUnit


@pytest.mark.django_db
def test_create_organization_unit(auth_client, user):
    resp = auth_client.post(
        '/api/v1/organization-units/',
        {'code': 'OPS', 'name': 'Operations'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert OrganizationUnit.objects.filter(code='OPS').exists()


@pytest.mark.django_db
def test_organization_unit_code_unique(auth_client):
    auth_client.post(
        '/api/v1/organization-units/',
        {'code': 'DUP', 'name': 'One'},
        format='json',
    )
    resp = auth_client.post(
        '/api/v1/organization-units/',
        {'code': 'DUP', 'name': 'Two'},
        format='json',
    )
    assert resp.status_code == 400

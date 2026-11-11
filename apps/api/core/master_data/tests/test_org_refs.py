import pytest

from master_data.models import OrganizationUnit


@pytest.mark.django_db
def test_create_organization_unit(hr_client):
    resp = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'OPS', 'name': 'Operations'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert OrganizationUnit.objects.filter(code='OPS').exists()


@pytest.mark.django_db
def test_create_organization_unit_as_business_setup(business_setup_client):
    resp = business_setup_client.post(
        '/api/v1/organization-units/',
        {'code': 'BSU', 'name': 'Business setup unit'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert OrganizationUnit.objects.filter(code='BSU').exists()


@pytest.mark.django_db
def test_create_organization_unit_as_staff(staff_client):
    resp = staff_client.post(
        '/api/v1/organization-units/',
        {'code': 'STF', 'name': 'Staff unit'},
        format='json',
    )
    assert resp.status_code == 403, resp.content
    assert not OrganizationUnit.objects.filter(code='STF').exists()


@pytest.mark.django_db
def test_list_organization_units_authenticated(auth_client, user):
    OrganizationUnit.objects.create(code='OPS', name='Operations', created_by=user, updated_by=user)
    resp = auth_client.get('/api/v1/organization-units/')
    assert resp.status_code == 200, resp.content
    codes = {row['code'] for row in resp.json()}
    assert 'OPS' in codes


@pytest.mark.django_db
def test_create_organization_unit_forbidden(auth_client):
    resp = auth_client.post(
        '/api/v1/organization-units/',
        {'code': 'OPS2', 'name': 'Operations2'},
        format='json',
    )
    assert resp.status_code == 403, resp.content
    assert not OrganizationUnit.objects.filter(code='OPS2').exists()


@pytest.mark.django_db
def test_patch_organization_unit(hr_client, user):
    unit = OrganizationUnit.objects.create(code='OPS', name='Operations', created_by=user, updated_by=user)
    resp = hr_client.patch(
        f'/api/v1/organization-units/{unit.id}/',
        {'name': 'Renamed'},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    unit.refresh_from_db()
    assert unit.name == 'Renamed'


@pytest.mark.django_db
def test_patch_organization_unit_forbidden(auth_client, user):
    unit = OrganizationUnit.objects.create(code='OPS', name='Operations', created_by=user, updated_by=user)
    resp = auth_client.patch(
        f'/api/v1/organization-units/{unit.id}/',
        {'name': 'Renamed'},
        format='json',
    )
    assert resp.status_code == 403, resp.content
    unit.refresh_from_db()
    assert unit.name == 'Operations'


@pytest.mark.django_db
def test_organization_unit_code_unique(hr_client):
    hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'DUP', 'name': 'One'},
        format='json',
    )
    resp = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'DUP', 'name': 'Two'},
        format='json',
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_organization_unit_accepts_a_different_parent(hr_client):
    parent = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'PAR', 'name': 'Parent'},
        format='json',
    )
    assert parent.status_code == 201, parent.content
    child = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'CHD', 'name': 'Child', 'parent': parent.json()['id']},
        format='json',
    )
    assert child.status_code == 201, child.content
    assert str(OrganizationUnit.objects.get(code='CHD').parent_id) == parent.json()['id']


@pytest.mark.django_db
def test_organization_unit_cannot_be_its_own_parent(hr_client):
    created = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'SELF', 'name': 'Self'},
        format='json',
    )
    assert created.status_code == 201, created.content
    unit_id = created.json()['id']
    resp = hr_client.patch(
        f'/api/v1/organization-units/{unit_id}/',
        {'parent': unit_id},
        format='json',
    )
    assert resp.status_code == 400, resp.content
    assert OrganizationUnit.objects.get(pk=unit_id).parent_id is None

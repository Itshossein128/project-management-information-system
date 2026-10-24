import pytest

from master_data.models import ManagedContractType


@pytest.mark.django_db
def test_create_and_list_contract_types(hr_client):
    resp = hr_client.post(
        '/api/v1/contract-types/',
        {'code': 'main', 'name_fa': 'اصلی', 'name_en': 'Main'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    listing = hr_client.get('/api/v1/contract-types/')
    assert listing.status_code == 200
    codes = {row['code'] for row in listing.json()}
    assert 'main' in codes
    assert ManagedContractType.objects.filter(code='main').exists()


@pytest.mark.django_db
def test_create_contract_type_as_business_setup(business_setup_client):
    resp = business_setup_client.post(
        '/api/v1/contract-types/',
        {'code': 'bs', 'name_fa': 'راه‌اندازی', 'name_en': 'Setup'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert ManagedContractType.objects.filter(code='bs').exists()


@pytest.mark.django_db
def test_list_contract_types_authenticated(auth_client):
    ManagedContractType.objects.create(code='main', name_fa='اصلی', name_en='Main')
    resp = auth_client.get('/api/v1/contract-types/')
    assert resp.status_code == 200, resp.content
    codes = {row['code'] for row in resp.json()}
    assert 'main' in codes


@pytest.mark.django_db
def test_create_contract_types_forbidden(auth_client):
    resp = auth_client.post(
        '/api/v1/contract-types/',
        {'code': 'main', 'name_fa': 'اصلی', 'name_en': 'Main'},
        format='json',
    )
    assert resp.status_code == 403, resp.content
    assert not ManagedContractType.objects.filter(code='main').exists()

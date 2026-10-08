import pytest

from master_data.models import ManagedContractType


@pytest.mark.django_db
def test_create_and_list_contract_types(auth_client):
    resp = auth_client.post(
        '/api/v1/contract-types/',
        {'code': 'main', 'name_fa': 'اصلی', 'name_en': 'Main'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    listing = auth_client.get('/api/v1/contract-types/')
    assert listing.status_code == 200
    codes = {r['code'] for r in listing.json()}
    assert 'main' in codes
    assert ManagedContractType.objects.filter(code='main').exists()

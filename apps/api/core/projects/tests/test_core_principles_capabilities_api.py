"""US6: capabilities API."""
import pytest


@pytest.mark.django_db
def test_list_capabilities_seeds_catalog(auth_client, project):
    resp = auth_client.get(f'/api/v1/projects/{project.id}/capabilities/')
    assert resp.status_code == 200, resp.content
    keys = {row['capability_key'] for row in resp.json()}
    assert 'risk' in keys
    assert 'economic' in keys


@pytest.mark.django_db
def test_update_capability(auth_client, project):
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/capabilities/risk/',
        {'enabled': False, 'mode': 'disabled'},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()['enabled'] is False
    assert resp.json()['mode'] == 'disabled'

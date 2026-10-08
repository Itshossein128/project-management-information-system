"""US7: fiscal period lock API."""
import pytest


@pytest.mark.django_db
def test_create_fiscal_lock(auth_client, project):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/fiscal-period-locks/',
        {
            'period_start': '2024-01-01',
            'period_end': '2024-03-31',
            'reason': 'Q1 close',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()['is_active'] is True


@pytest.mark.django_db
def test_overlap_rejected(auth_client, project):
    auth_client.post(
        f'/api/v1/projects/{project.id}/fiscal-period-locks/',
        {
            'period_start': '2024-01-01',
            'period_end': '2024-03-31',
            'reason': 'Q1 close',
        },
        format='json',
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/fiscal-period-locks/',
        {
            'period_start': '2024-03-01',
            'period_end': '2024-06-30',
            'reason': 'overlap',
        },
        format='json',
    )
    assert resp.status_code == 400
    assert 'overlapping_fiscal_lock' in str(resp.json())

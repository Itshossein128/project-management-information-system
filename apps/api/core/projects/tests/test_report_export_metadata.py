"""FR-RPT US3: report export metadata and download envelope."""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_export_persists_metadata(auth_client, project):
    payload = {
        'filters': {
            'date_from': '2026-10-01',
            'date_to': '2026-10-07',
            'approved_only': True,
        },
        'format': 'json',
    }
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/reports/weekly_progress/export/',
        payload,
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data['report_type'] == 'weekly_progress'
    assert data['filters']['date_from'] == '2026-10-01'
    assert data['filters']['date_to'] == '2026-10-07'
    assert data['extracted_at']
    export_id = data['id']

    meta = auth_client.get(
        f'/api/v1/projects/{project.id}/reports/exports/{export_id}/'
    )
    assert meta.status_code == 200
    assert meta.json()['filters'] == data['filters']

    download = auth_client.get(
        f'/api/v1/projects/{project.id}/reports/exports/{export_id}/download/'
    )
    assert download.status_code == 200
    envelope = download.json()
    assert envelope['extracted_at'] == data['extracted_at']
    assert envelope['filters']['date_from'] == '2026-10-01'
    assert envelope['filters']['date_to'] == '2026-10-07'


@pytest.mark.django_db
def test_report_catalog(auth_client, project):
    resp = auth_client.get(f'/api/v1/projects/{project.id}/reports/catalog/')
    assert resp.status_code == 200
    types = {r['report_type'] for r in resp.json()['results']}
    assert 'weekly_progress' in types
    assert 'budget_variance' in types

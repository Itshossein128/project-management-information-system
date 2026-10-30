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


@pytest.mark.django_db
def test_run_query_filters_preserve_values_and_requested_approval_mode(auth_client, project, monkeypatch):
    from projects.services import report_export_service

    captured = {}

    def fake_kpis(project_id, as_of):
        captured['as_of'] = as_of.isoformat()
        return {
            'figures': [{'figure_key': 'draft', 'label_unapproved': True}],
            'physical_progress': {},
        }

    monkeypatch.setattr(report_export_service, 'get_project_kpis', fake_kpis)
    response = auth_client.get(
        f'/api/v1/projects/{project.id}/reports/weekly_progress/',
        {'date_to': '2026-10-07', 'approved_only': 'false'},
    )

    assert response.status_code == 200
    body = response.json()
    assert captured['as_of'] == '2026-10-07'
    assert body['filters']['date_to'] == '2026-10-07'
    assert body['filters']['approved_only'] is False
    assert [figure['figure_key'] for figure in body['figures']] == ['draft']


@pytest.mark.django_db
@pytest.mark.parametrize('scope', ['project', 'portfolio'])
def test_export_rejects_unsupported_format_without_creating_version(auth_client, project, scope):
    from projects.models import ReportExportVersion

    before = ReportExportVersion.objects.count()
    url = (
        f'/api/v1/projects/{project.id}/reports/weekly_progress/export/'
        if scope == 'project'
        else '/api/v1/portfolio/reports/portfolio_summary/export/'
    )
    response = auth_client.post(url, {'format': 'pdf'}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'format' in response.json()['error']['details']
    assert ReportExportVersion.objects.count() == before


@pytest.mark.django_db
def test_portfolio_export_download_is_owner_scoped_and_rechecks_membership(
    auth_client, api_client, project, user, other_user, member,
):
    from master_data.models import ProjectMember

    response = auth_client.post(
        '/api/v1/portfolio/reports/portfolio_summary/export/',
        {'format': 'json', 'filters': {'date_to': '2026-10-07'}},
        format='json',
    )
    assert response.status_code == 201
    meta = response.json()
    url = meta['download_url']
    download = auth_client.get(url)
    assert download.status_code == 200
    snapshot = download.json()
    assert snapshot['extracted_at'] == meta['extracted_at']
    assert snapshot['filters']['date_to'] == '2026-10-07'
    assert str(project.id) in {row['project_id'] for row in snapshot['data']['projects']}

    api_client.force_authenticate(other_user)
    assert api_client.get(url).status_code == 404

    api_client.force_authenticate(user)
    ProjectMember.objects.filter(project=project, user=user).update(status='inactive')
    assert auth_client.get(url).status_code == 404

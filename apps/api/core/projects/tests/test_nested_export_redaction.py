"""A6-P4 US5: nested wage/contact redaction on report export payloads."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from projects.services.report_export_service import _redact_wage_fields, create_export


@pytest.mark.django_db
def test_nested_export_redacts_wage_without_view_wage(project, user, monkeypatch):
    nested = {
        'report_type': 'monthly_project',
        'summary': {'title': 'Month', 'wage': 1500000, 'daily_rate': 500},
        'rows': [
            {'name': 'Crew A', 'wage': 900, 'email': 'a@example.com'},
            {'name': 'Crew B', 'contact_phone': '+98912'},
        ],
    }

    def fake_run_report(*args, **kwargs):
        return nested

    monkeypatch.setattr(
        'projects.services.report_export_service.run_report',
        fake_run_report,
    )

    version = create_export(
        report_type='monthly_project',
        user=user,
        project=project,
        filters={},
        fmt='json',
        user_permissions=set(),
    )
    data = version.payload_json['data']
    assert data['summary']['title'] == 'Month'
    assert data['summary']['wage'] is None
    assert data['summary'].get('wage_redacted') is True
    assert data['rows'][0]['wage'] is None
    assert data['rows'][0]['name'] == 'Crew A'
    assert data['rows'][0]['email'] is None
    assert data['rows'][1]['contact_phone'] is None


@pytest.mark.django_db
def test_nested_export_keeps_wage_with_view_wage(project, user, monkeypatch):
    nested = {'summary': {'wage': 42}, 'rows': []}

    monkeypatch.setattr(
        'projects.services.report_export_service.run_report',
        lambda *a, **k: nested,
    )

    version = create_export(
        report_type='monthly_project',
        user=user,
        project=project,
        fmt='json',
        user_permissions={'view_wage', 'view_person_contacts'},
    )
    data = version.payload_json['data']
    assert data['summary']['wage'] == 42


@pytest.mark.django_db
def test_nested_export_redacts_stakeholder_contact_keys(project, user, monkeypatch):
    nested = {
        'rows': [{'name': 'Stakeholder A', 'email': 's@example.com', 'phone': '+1000'}],
    }

    monkeypatch.setattr(
        'projects.services.report_export_service.run_report',
        lambda *a, **k: nested,
    )

    version = create_export(
        report_type='monthly_project',
        user=user,
        project=project,
        fmt='json',
        user_permissions=set(),
    )
    data = version.payload_json['data']
    assert data['rows'][0]['email'] is None
    assert data['rows'][0]['phone'] is None


@pytest.mark.django_db
def test_export_download_re_redacts_payload(user, project, monkeypatch):
    """Download applies current permissions to persisted envelope (A6-P4 T073)."""
    from django.utils import timezone

    from master_data.models import ProjectMember, ProjectMemberPermissionOverride
    from projects.models import ReportExportVersion

    membership = ProjectMember.objects.get(project=project, user=user)
    for codename in ('view_wage', 'view_person_contacts', 'view_sensitive_contacts'):
        ProjectMemberPermissionOverride.objects.update_or_create(
            member=membership,
            permission_codename=codename,
            defaults={'is_granted': False},
        )

    envelope = {
        'data': {
            'rows': [{'wage': 999, 'email': 'leak@example.com'}],
        },
    }
    version = ReportExportVersion.objects.create(
        report_type='monthly_project',
        project=project,
        filters={},
        extracted_at=timezone.now(),
        extracted_by=user,
        approved_only=True,
        payload_json=envelope,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse(
        'project-report-export-download',
        kwargs={'project_pk': project.id, 'export_id': version.id},
    )
    response = client.get(url)
    assert response.status_code == 200
    body = response.json()
    row = body['data']['rows'][0]
    assert row['wage'] is None
    assert row['email'] is None


def test_redact_helper_strips_nested_keys_directly():
    out = _redact_wage_fields(
        {'outer': {'inner': {'wage': 1, 'mobile': '2'}}},
        set(),
    )
    assert out['outer']['inner']['wage'] is None
    assert out['outer']['inner']['mobile'] is None

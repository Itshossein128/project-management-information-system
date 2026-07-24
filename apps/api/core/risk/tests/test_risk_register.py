"""Risk register API tests."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from documents.models import Correspondence, CorrType
from field_reports.models import DailyReport
from projects.models import Project
from risk.models import BarrierStatus, EventType, RiskEvent, Severity


BASE = '/api/v1/projects/{project_id}/risk-events/'


@pytest.mark.django_db
class TestRiskRegisterAPI:
    def test_create_and_list_risk_event(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(
            url,
            {
                'event_type': EventType.RISK,
                'description': 'Supply chain delay',
                'probability': '0.5',
                'severity': Severity.MEDIUM,
                'event_date': '2024-08-01',
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        listing = auth_client.get(url)
        assert listing.status_code == status.HTTP_200_OK
        assert listing.data['count'] >= 1

    def test_filter_by_event_type(self, auth_client, project, user):
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.CLAIM,
            description='Claim 1',
            status=BarrierStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.DELAY,
            description='Delay 1',
            status=BarrierStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        resp = auth_client.get(url, {'event_type': EventType.CLAIM})
        assert resp.status_code == status.HTTP_200_OK
        assert all(r['event_type'] == EventType.CLAIM for r in resp.data['results'])

    def test_risk_matrix_aggregation(self, auth_client, project, user):
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Open risk',
            probability=Decimal('0.5'),
            severity=Severity.MEDIUM,
            status=BarrierStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.DELAY,
            description='Resolved risk',
            probability=Decimal('0.5'),
            severity=Severity.MEDIUM,
            status=BarrierStatus.RESOLVED,
            resolved_date=date.today(),
            created_by=user,
            updated_by=user,
        )
        url = f"{BASE.format(project_id=project.id)}matrix/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['total_open'] == 1
        assert 'matrix' in resp.data

    def test_claim_linker_same_project(self, auth_client, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-01',
            created_by=user,
            updated_by=user,
        )
        corr = Correspondence.objects.create(
            project=project,
            corr_number='CORR-001',
            corr_type=CorrType.INCOMING,
            subject='Test letter',
            from_party='Employer',
            to_party='Contractor',
            corr_date='2024-01-15',
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.CLAIM,
                'description': 'Extension of time claim',
                'related_daily_report': str(report.id),
                'related_correspondence': str(corr.id),
                'severity': Severity.HIGH,
                'probability': '0.7',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert str(resp.data['related_daily_report']) == str(report.id)
        assert str(resp.data['related_correspondence']) == str(corr.id)

    def test_claim_linker_rejects_cross_project(self, auth_client, project, user):
        other = Project.objects.create(project_code='PRJ-002', project_name='Other Project')
        report = DailyReport.objects.create(
            project=other,
            report_date='2024-01-01',
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.CLAIM,
                'description': 'Bad link',
                'related_daily_report': str(report.id),
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_claim_linker_rejects_cross_project_correspondence(self, auth_client, project, user):
        other = Project.objects.create(project_code='PRJ-003', project_name='Third Project')
        corr = Correspondence.objects.create(
            project=other,
            corr_number='CORR-OTHER',
            corr_type=CorrType.INCOMING,
            subject='Bad corr link',
            from_party='A',
            to_party='B',
            corr_date='2024-01-01',
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'event_type': EventType.CLAIM,
                'description': 'Bad link',
                'related_correspondence': str(corr.id),
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_and_retrieve_risk_event(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.DELAY,
            description='Initial',
            status=BarrierStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        url = f"{BASE.format(project_id=project.id)}{event.id}/"
        patch = auth_client.patch(
            url,
            {'description': 'Updated delay', 'time_impact_days': 3, 'severity': Severity.HIGH},
            format='json',
        )
        assert patch.status_code == status.HTTP_200_OK
        assert patch.data['description'] == 'Updated delay'
        get = auth_client.get(url)
        assert get.status_code == status.HTTP_200_OK
        assert get.data['severity'] == Severity.HIGH

    def test_soft_delete_risk_event(self, auth_client, project, user):
        event = RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='To delete',
            created_by=user,
            updated_by=user,
        )
        url = f"{BASE.format(project_id=project.id)}{event.id}/"
        delete = auth_client.delete(url)
        assert delete.status_code == status.HTTP_204_NO_CONTENT
        assert not RiskEvent.objects.filter(id=event.id).exists()

    def test_filter_by_severity_and_search(self, auth_client, project, user):
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Steel supply shortage',
            responsible_party='Procurement',
            severity=Severity.HIGH,
            created_by=user,
            updated_by=user,
        )
        RiskEvent.objects.create(
            project=project,
            event_type=EventType.RISK,
            description='Minor paperwork',
            severity=Severity.LOW,
            created_by=user,
            updated_by=user,
        )
        url = BASE.format(project_id=project.id)
        by_sev = auth_client.get(url, {'severity': Severity.HIGH})
        assert all(r['severity'] == Severity.HIGH for r in by_sev.data['results'])
        by_search = auth_client.get(url, {'search': 'Steel'})
        assert any('Steel' in r['description'] for r in by_search.data['results'])

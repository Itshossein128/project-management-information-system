"""Workflow decisions must use current server-side authorization under lock."""
from datetime import date

import pytest

from master_data.models import MemberStatus, ProjectMember
from sub_reports.models import DisciplineSubReport, SubReportStatus
from sub_reports import unit_report_services as svc

pytestmark = pytest.mark.django_db


def test_submit_rechecks_permission_after_lock(auth_client, project, user, monkeypatch):
    report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 20), status=SubReportStatus.DRAFT, created_by=user)
    original_lock = svc.lock_current_version
    def revoke_after_read(*args, **kwargs):
        result = original_lock(*args, **kwargs)
        ProjectMember.objects.filter(project=project, user=user).update(status=MemberStatus.INACTIVE)
        return result
    monkeypatch.setattr(svc, 'lock_current_version', revoke_after_read)
    response = auth_client.post(f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{report.id}/submit/')
    assert response.status_code == 403, response.data
    report.refresh_from_db()
    assert report.status == SubReportStatus.DRAFT

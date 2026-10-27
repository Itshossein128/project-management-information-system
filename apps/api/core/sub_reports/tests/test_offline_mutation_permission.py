"""A cached/request-time grant cannot authorize a later unit mutation."""
from datetime import date

import pytest

from master_data.models import MemberStatus, ProjectMember
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus
from sub_reports import unit_report_services as svc

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('target', ['header', 'activity'])
def test_permission_revoked_before_locked_mutation_is_refused(auth_client, project, user, monkeypatch, target):
    report = DisciplineSubReport.objects.create(project=project, unit='buildings', discipline='civil',
        report_date=date(2026, 10, 20), status=SubReportStatus.DRAFT, created_by=user, form_code='original')
    row = DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1,
        shift='shift_1', activity_description='work', notes='original')
    original_lock = svc.lock_current_version
    def revoke_after_read(*args, **kwargs):
        result = original_lock(*args, **kwargs)
        ProjectMember.objects.filter(project=project, user=user).update(status=MemberStatus.INACTIVE)
        return result
    monkeypatch.setattr(svc, 'lock_current_version', revoke_after_read)
    base = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{report.id}/'
    response = (auth_client.patch(base, {'form_code': 'changed'}, format='json') if target == 'header'
                else auth_client.patch(base + f'activities/{row.id}/', {'notes': 'changed'}, format='json'))
    assert response.status_code == 403, response.data
    report.refresh_from_db(); row.refresh_from_db()
    assert report.form_code == 'original'
    assert row.notes == 'original'

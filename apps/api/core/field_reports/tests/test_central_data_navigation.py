import pytest

from field_reports.models import DailyReport, ReportShift


@pytest.mark.django_db
def test_daily_report_navigation(auth_client, project, user):
    report = DailyReport.objects.create(
        project=project,
        report_date='2024-06-01',
        shift=ReportShift.DAY,
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.get(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/navigation/'
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body['project']['id'] == str(project.id)
    assert body['report']['id'] == str(report.id)

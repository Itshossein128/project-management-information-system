import pytest

from field_reports.models import ReportStatus
from field_reports.services import approve_report, submit_report
from field_reports.services.daily_report_aggregation import (
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_approval_survives_rebuild(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    submit_report(report, user)
    approve_report(report, user)
    report.refresh_from_db()
    assert report.status == ReportStatus.APPROVED

    add_activity(sr, description='extra')
    rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.refresh_from_db()
    assert report.status == ReportStatus.APPROVED
    assert report.approved_by_id == user.id

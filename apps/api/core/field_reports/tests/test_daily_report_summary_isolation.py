import pytest

from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from projects.services import create_project_with_creator
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_rebuild_does_not_leak_other_project(project, user):
    other = create_project_with_creator(
        creator=user,
        project_code='PRJ-OTHER',
        project_name='Other',
        employer='E',
        start_date='2024-01-01',
    )
    sr = make_sub_report(other, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr, description='other-only')

    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    descs = list(
        report.activities.filter(is_deleted=False).values_list('activity_description', flat=True),
    )
    assert 'other-only' not in descs

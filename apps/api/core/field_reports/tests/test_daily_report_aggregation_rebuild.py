import pytest

from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus
from sub_reports.services import submit_sub_report


@pytest.mark.django_db
def test_rebuild_replaces_derived_activities(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.DRAFT)
    add_activity(sr, description='v1')
    submit_sub_report(sr, user)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert list(
        report.activities.filter(is_deleted=False).values_list('activity_description', flat=True),
    ) == ['v1']

    sr.activities.filter(is_deleted=False).update(is_deleted=True)
    add_activity(sr, description='v2')
    # already submitted — trigger rebuild via ensure
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    descs = list(
        report.activities.filter(is_deleted=False).values_list('activity_description', flat=True),
    )
    assert descs == ['v2']

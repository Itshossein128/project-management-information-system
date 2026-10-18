import pytest

from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    ensure_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_partial_meta(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=report)
    assert meta['contributing_disciplines'] == ['civil']
    assert 'electrical' in meta['missing_disciplines']
    assert 'mechanical' in meta['missing_disciplines']
    assert meta['is_partial'] is True

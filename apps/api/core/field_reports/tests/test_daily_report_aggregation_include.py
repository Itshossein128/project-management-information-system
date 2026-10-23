import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.services.daily_report_aggregation import (
    contributing_sub_reports,
    ensure_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import Discipline, SubReportStatus


@pytest.mark.django_db
def test_include_only_submitted_and_approved(project, user):
    draft = make_sub_report(project, user, status=SubReportStatus.DRAFT)
    add_activity(draft, description='draft-act')
    submitted = make_sub_report(
        project, user, discipline=Discipline.ELECTRICAL, status=SubReportStatus.SUBMITTED,
    )
    add_activity(submitted, description='sub-act')
    approved = make_sub_report(
        project, user, discipline=Discipline.MECHANICAL, status=SubReportStatus.APPROVED,
    )
    add_activity(approved, description='apr-act')
    rejected = make_sub_report(
        project, user, unit=SpecialtyUnit.MACHINERY, discipline=Discipline.MECHANICAL, status=SubReportStatus.REJECTED,
    )
    add_activity(rejected, description='rej-act')

    qs = contributing_sub_reports(project.id, SUMMARY_DATE)
    assert set(qs.values_list('unit', flat=True)) == {
        SpecialtyUnit.ELECTRICAL,
        SpecialtyUnit.MECHANICAL,
    }

    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    descs = list(
        report.activities.filter(is_deleted=False).values_list('activity_description', flat=True),
    )
    assert 'sub-act' in descs
    assert 'apr-act' in descs
    assert 'draft-act' not in descs
    assert 'rej-act' not in descs


@pytest.mark.django_db
def test_draft_invisible_until_submit(project, user):
    draft = make_sub_report(project, user, status=SubReportStatus.DRAFT)
    add_activity(draft, description='later')
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert report.activities.filter(is_deleted=False).count() == 0

    from sub_reports.services import submit_sub_report

    submit_sub_report(draft, user)
    report.refresh_from_db()
    descs = list(
        report.activities.filter(is_deleted=False).values_list('activity_description', flat=True),
    )
    assert 'later' in descs

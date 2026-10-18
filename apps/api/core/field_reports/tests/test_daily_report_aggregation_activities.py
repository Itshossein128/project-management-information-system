import pytest

from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import Discipline, SubReportStatus


@pytest.mark.django_db
def test_activity_union_with_provenance(project, user):
    civil = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(civil, description='civil-a', zone='C8')
    elec = make_sub_report(
        project, user, discipline=Discipline.ELECTRICAL, status=SubReportStatus.SUBMITTED,
    )
    add_activity(elec, description='elec-a', zone='E1')

    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    rows = list(report.activities.filter(is_deleted=False).order_by('activity_description'))
    assert len(rows) == 2
    assert all(r.is_derived for r in rows)
    by_desc = {r.activity_description: r for r in rows}
    assert by_desc['civil-a'].source_discipline == Discipline.CIVIL
    assert by_desc['civil-a'].source_sub_report_id == civil.id
    assert by_desc['civil-a'].zone == 'C8'
    civil.refresh_from_db()
    assert civil.linked_daily_report_id == report.id

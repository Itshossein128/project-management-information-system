from datetime import date
import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReportActivity
from field_reports.services.daily_report_aggregation import (
    contributing_sub_reports,
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
)
from projects.models import Project
from sub_reports.models import (
    DisciplineSubReport,
    MigrationDisposition,
    SubReportStatus,
    UnitReportMigrationQuarantine,
    UnitReportMigrationTrace,
)


def make_unit_report(
    project,
    user,
    *,
    unit=SpecialtyUnit.BUILDINGS,
    status=SubReportStatus.SUBMITTED,
    report_date=SUMMARY_DATE,
    is_current=True,
    is_deleted=False,
    version_number=1,
):
    sr = DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        unit=unit,
        legacy_discipline=unit,
        discipline='civil',
        status=status,
        is_current=is_current,
        is_deleted=is_deleted,
        version_number=version_number,
        created_by=user,
        updated_by=user,
        submitted_by=user if status in (SubReportStatus.SUBMITTED, SubReportStatus.APPROVED) else None,
        approved_by=user if status == SubReportStatus.APPROVED else None,
    )
    return sr


@pytest.mark.django_db
def test_submitted_and_approved_reports_contribute(project, user):
    r1 = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED)
    act1 = add_activity(r1, description='Buildings task')
    r2 = make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL, status=SubReportStatus.APPROVED)
    act2 = add_activity(r2, description='Electrical task')

    eligible = list(contributing_sub_reports(project.id, SUMMARY_DATE))
    assert r1 in eligible
    assert r2 in eligible

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    activities = summary.activities.filter(is_derived=True).values_list('activity_description', flat=True)
    assert 'Buildings task' in activities
    assert 'Electrical task' in activities


@pytest.mark.django_db
def test_draft_and_rejected_reports_contribute_nothing(project, user):
    r_draft = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.DRAFT)
    add_activity(r_draft, description='Draft task')
    r_rejected = make_unit_report(project, user, unit=SpecialtyUnit.MECHANICAL, status=SubReportStatus.REJECTED)
    add_activity(r_rejected, description='Rejected task')

    eligible = list(contributing_sub_reports(project.id, SUMMARY_DATE))
    assert r_draft not in eligible
    assert r_rejected not in eligible

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert summary.activities.filter(is_derived=True).count() == 0


@pytest.mark.django_db
def test_deleted_and_superseded_reports_contribute_nothing(project, user):
    r_deleted = make_unit_report(
        project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED, is_deleted=True,
    )
    add_activity(r_deleted, description='Deleted task')

    r_superseded = make_unit_report(
        project, user, unit=SpecialtyUnit.ELECTRICAL, status=SubReportStatus.SUBMITTED, is_current=False,
    )
    add_activity(r_superseded, description='Superseded task')

    eligible = list(contributing_sub_reports(project.id, SUMMARY_DATE))
    assert r_deleted not in eligible
    assert r_superseded not in eligible

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert summary.activities.filter(is_derived=True).count() == 0


@pytest.mark.django_db
def test_cross_project_and_cross_date_reports_contribute_nothing(project, user):
    other_project = Project.objects.create(project_name='Other Project', project_code='OTH-01')
    r_other_proj = make_unit_report(
        other_project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED,
    )
    add_activity(r_other_proj, description='Other project task')

    r_other_date = make_unit_report(
        project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED,
        report_date=date(2024, 6, 11),
    )
    add_activity(r_other_date, description='Other date task')

    eligible = list(contributing_sub_reports(project.id, SUMMARY_DATE))
    assert r_other_proj not in eligible
    assert r_other_date not in eligible

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert summary.activities.filter(is_derived=True).count() == 0


@pytest.mark.django_db
def test_quarantined_reports_contribute_nothing(project, user):
    r_quarantined = make_unit_report(
        project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED,
    )
    add_activity(r_quarantined, description='Quarantined task')

    trace = UnitReportMigrationTrace.objects.create(
        source_system='legacy',
        source_model='sub_report',
        source_id='legacy-123',
        target_report=r_quarantined,
        disposition=MigrationDisposition.QUARANTINED,
    )
    UnitReportMigrationQuarantine.objects.create(
        trace=trace,
        reason_code='unmapped_discipline',
    )

    eligible = list(contributing_sub_reports(project.id, SUMMARY_DATE))
    assert r_quarantined not in eligible

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert summary.activities.filter(is_derived=True).count() == 0

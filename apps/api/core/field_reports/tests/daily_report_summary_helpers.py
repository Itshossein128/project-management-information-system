"""Shared fixtures/helpers for auto daily-report summary tests."""
import uuid
from datetime import date

from common.reporting_units import SpecialtyUnit
from field_reports.models import LaborCategory
from sub_reports.models import (
    Discipline,
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportLabor,
    SubReportStatus,
)


SUMMARY_DATE = date(2024, 6, 10)

DISCIPLINE_TO_CANONICAL_UNIT = {
    'civil': SpecialtyUnit.BUILDINGS,
    'finishing': SpecialtyUnit.BUILDINGS,
    'electrical': SpecialtyUnit.ELECTRICAL,
    'mechanical': SpecialtyUnit.MECHANICAL,
    'plumbing': SpecialtyUnit.MECHANICAL,
    'hvac': SpecialtyUnit.MECHANICAL,
    'machinery': SpecialtyUnit.MACHINERY,
    'warehouse': SpecialtyUnit.WAREHOUSE,
    'security': SpecialtyUnit.SECURITY,
}


def make_sub_report(
    project,
    user,
    *,
    unit=None,
    discipline=Discipline.CIVIL,
    status=SubReportStatus.DRAFT,
    report_date=SUMMARY_DATE,
    weather_condition='clear',
    site_status='active',
    lineage_id=None,
    version_number=1,
    is_current=True,
):
    canonical_unit = unit or DISCIPLINE_TO_CANONICAL_UNIT.get(str(discipline), SpecialtyUnit.BUILDINGS)
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        unit=canonical_unit,
        discipline=discipline,
        weather_condition=weather_condition,
        site_status=site_status,
        status=status,
        lineage_id=lineage_id or uuid.uuid4(),
        version_number=version_number,
        is_current=is_current,
        created_by=user,
        updated_by=user,
        submitted_by=user if status != SubReportStatus.DRAFT else None,
    )


def add_activity(
    sub_report,
    *,
    description='Activity',
    shift='shift_1',
    workers=2,
    foreman=None,
    zone='Z1',
    parcel=None,
    notes='',
):
    return DisciplineSubReportActivity.objects.create(
        sub_report=sub_report,
        row_number=sub_report.activities.count() + 1,
        shift=shift,
        crew_name='Crew',
        foreman_count=foreman,
        worker_count=workers,
        zone=zone,
        parcel=parcel,
        block='B1',
        floor='1',
        activity_description=description,
        unit='m2',
        quantity=10,
        notes=notes,
    )


def add_labor(sub_report, *, title='کارگر ساده', category=LaborCategory.DIRECT, present=3, leave=1):
    return DisciplineSubReportLabor.objects.create(
        sub_report=sub_report,
        labor_category=category,
        job_title=title,
        present_count=present,
        leave_count=leave,
    )




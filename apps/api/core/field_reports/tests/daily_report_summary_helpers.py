"""Shared fixtures/helpers for auto daily-report summary tests."""
from datetime import date

from field_reports.models import LaborCategory
from sub_reports.models import (
    Discipline,
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportLabor,
    SubReportStatus,
)


SUMMARY_DATE = date(2024, 6, 10)


def make_sub_report(
    project,
    user,
    *,
    discipline=Discipline.CIVIL,
    status=SubReportStatus.DRAFT,
    report_date=SUMMARY_DATE,
    weather_condition='clear',
    site_status='active',
):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        discipline=discipline,
        weather_condition=weather_condition,
        site_status=site_status,
        status=status,
        created_by=user,
        updated_by=user,
        submitted_by=user if status != SubReportStatus.DRAFT else None,
    )


def add_activity(sub_report, *, description='Activity', shift='shift_1', workers=2, zone='Z1'):
    return DisciplineSubReportActivity.objects.create(
        sub_report=sub_report,
        row_number=sub_report.activities.count() + 1,
        shift=shift,
        crew_name='Crew',
        worker_count=workers,
        zone=zone,
        block='B1',
        floor='1',
        activity_description=description,
        unit='m2',
        quantity=10,
    )


def add_labor(sub_report, *, title='کارگر ساده', category=LaborCategory.DIRECT, present=3, leave=1):
    return DisciplineSubReportLabor.objects.create(
        sub_report=sub_report,
        labor_category=category,
        job_title=title,
        present_count=present,
        leave_count=leave,
    )

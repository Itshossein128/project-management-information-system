import pytest

from field_reports.models import LaborCategory
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_labor,
    make_sub_report,
)
from sub_reports.models import (
    Discipline,
    DisciplineSubReportConcrete,
    DisciplineSubReportMaterial,
    SubReportStatus,
)


@pytest.mark.django_db
def test_labor_sums_across_disciplines(project, user):
    civil = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_labor(civil, title='کارگر ساده', present=2, leave=1)
    elec = make_sub_report(
        project, user, discipline=Discipline.ELECTRICAL, status=SubReportStatus.SUBMITTED,
    )
    add_labor(elec, title='کارگر ساده', present=3, leave=0)

    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    row = report.labor_entries.filter(is_deleted=False, job_title='کارگر ساده').get()
    assert row.shift_1_count == 5
    assert row.absence_count == 1
    assert row.labor_category == LaborCategory.DIRECT
    assert row.is_derived is True


@pytest.mark.django_db
def test_materials_and_concrete_union(project, user):
    civil = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    DisciplineSubReportMaterial.objects.create(
        sub_report=civil,
        material_description='سیمان',
        quantity=10,
        unit='تن',
    )
    DisciplineSubReportConcrete.objects.create(
        sub_report=civil,
        concrete_description='بتن عیار400',
        volume_m3='12.5',
    )
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert report.material_entries.filter(is_deleted=False).count() == 1
    assert report.concrete_logs.filter(is_deleted=False).count() == 1
    assert float(report.concrete_logs.filter(is_deleted=False).first().volume_m3) == 12.5

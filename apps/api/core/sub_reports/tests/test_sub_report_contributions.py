import pytest

from field_reports.models import LaborCategory
from sub_reports.models import (
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
    SubReportNoteType,
)
from field_reports.tests.daily_report_summary_helpers import make_sub_report
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_contribution_models_persist(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.DRAFT)
    labor = DisciplineSubReportLabor.objects.create(
        sub_report=sr,
        labor_category=LaborCategory.INDIRECT,
        job_title='مدیر پروژه',
        present_count=1,
        leave_count=0,
    )
    mat = DisciplineSubReportMaterial.objects.create(
        sub_report=sr, material_description='ماسه', quantity=1, unit='m3',
    )
    conc = DisciplineSubReportConcrete.objects.create(
        sub_report=sr, concrete_description='C30', volume_m3='2',
    )
    gen = DisciplineSubReportGeneralActivity.objects.create(
        sub_report=sr, activity_description='تخلیه بار', location='قطعه 8',
    )
    note = DisciplineSubReportNote.objects.create(
        sub_report=sr, note_type=SubReportNoteType.ISSUE, text='کمبود مصالح', row_number=1,
    )
    assert labor.pk and mat.pk and conc.pk and gen.pk and note.pk
    assert sr.labor_entries.count() == 1

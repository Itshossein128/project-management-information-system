"""TDD: daily report activity contractor_ref (027 US3 / Phase 7)."""

import pytest
from django.utils import timezone

from field_reports.models import DailyReport, DailyReportActivity
from projects.tests.contractor_select_helpers import make_active_contractor


@pytest.mark.django_db
def test_activity_serializer_snapshots_contractor_name(project, user):
    from field_reports.serializers import DailyReportActivitySerializer

    contractor = make_active_contractor(project, user, 'DR Co')
    report = DailyReport.objects.create(
        project=project,
        report_date=timezone.localdate(),
        created_by=user,
        updated_by=user,
    )
    ser = DailyReportActivitySerializer(
        data={
            'activity_description': 'Work',
            'shift': 'shift_1',
            'contractor_ref': str(contractor.id),
            'quantity_measured': False,
        },
        context={'report': report, 'project_id': project.id},
    )
    assert ser.is_valid(), ser.errors
    row = ser.save(report=report)
    assert isinstance(row, DailyReportActivity)
    assert row.contractor_ref_id == contractor.id
    assert row.subcontractor_name == 'DR Co'


@pytest.mark.django_db
def test_activity_rejects_unbound_subcontractor_name(project, user):
    from field_reports.serializers import DailyReportActivitySerializer

    report = DailyReport.objects.create(
        project=project,
        report_date=timezone.localdate(),
        created_by=user,
        updated_by=user,
    )
    ser = DailyReportActivitySerializer(
        data={
            'activity_description': 'Work',
            'shift': 'shift_1',
            'subcontractor_name': 'Invented Co',
            'quantity_measured': False,
        },
        context={'report': report, 'project_id': project.id},
    )
    assert not ser.is_valid()
    assert 'contractor_ref' in ser.errors


@pytest.mark.django_db
def test_daily_report_labor_aggregation_contractor_buckets(project, user):
    from field_reports.models import DailyReportLabor
    from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
    from field_reports.tests.daily_report_summary_helpers import make_sub_report
    from sub_reports.models import DisciplineSubReportLabor, SubReportStatus
    from common.reporting_units import SpecialtyUnit

    contractor_a = make_active_contractor(project, user, 'Contractor Alpha')
    contractor_b = make_active_contractor(project, user, 'Contractor Beta')

    today = timezone.localdate()
    sr1 = make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
    )
    DisciplineSubReportLabor.objects.create(
        sub_report=sr1,
        labor_category='skilled',
        job_title='آرماتوربند',
        present_count=4,
        contractor_ref=contractor_a,
    )

    sr2 = make_sub_report(
        project,
        user,
        unit=SpecialtyUnit.ELECTRICAL,
        discipline='electrical',
        report_date=today,
        status=SubReportStatus.SUBMITTED,
    )
    DisciplineSubReportLabor.objects.create(
        sub_report=sr2,
        labor_category='skilled',
        job_title='آرماتوربند',
        present_count=2,
        contractor_ref=contractor_b,
    )
    # Direct company labor (no contractor_ref)
    DisciplineSubReportLabor.objects.create(
        sub_report=sr2,
        labor_category='skilled',
        job_title='آرماتوربند',
        present_count=3,
        contractor_ref=None,
    )

    summary = ensure_daily_report_summary(project.id, today, user=user)
    labor_rows = list(summary.labor_entries.filter(is_derived=True, job_title='آرماتوربند').order_by('total_count'))
    assert len(labor_rows) == 3

    # Row for contractor B (2 workers)
    row_b = next(r for r in labor_rows if r.contractor_ref_id == contractor_b.id)
    assert row_b.total_count == 2
    assert row_b.contractor_name == 'Contractor Beta'

    # Row for contractor A (4 workers)
    row_a = next(r for r in labor_rows if r.contractor_ref_id == contractor_a.id)
    assert row_a.total_count == 4
    assert row_a.contractor_name == 'Contractor Alpha'

    # Row for direct company labor (3 workers)
    row_direct = next(r for r in labor_rows if r.contractor_ref is None)
    assert row_direct.total_count == 3
    assert row_direct.contractor_name == 'نفر شرکت'

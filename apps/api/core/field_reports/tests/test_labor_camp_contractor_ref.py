"""TDD: labor camp contractor_ref snapshot (027 US3 / Phase 7)."""

import pytest
from django.utils import timezone

from field_reports.models import DailyReport, DailyReportLaborCamp
from field_reports.serializers import DailyReportLaborCampSerializer
from projects.tests.contractor_select_helpers import make_active_contractor


@pytest.mark.django_db
def test_labor_camp_serializer_snapshots_contractor_name(project, user):
    contractor = make_active_contractor(project, user, 'Camp Co')
    report = DailyReport.objects.create(
        project=project,
        report_date=timezone.localdate(),
        created_by=user,
        updated_by=user,
    )
    ser = DailyReportLaborCampSerializer(
        data={
            'connex_number': 'C-1',
            'subcontractor_name': '',
            'contractor_ref': str(contractor.id),
            'total_residents': 10,
            'present_count': 8,
            'on_leave_count': 2,
            'capacity': 12,
        },
        context={'report': report, 'project_id': project.id},
    )
    assert ser.is_valid(), ser.errors
    row = ser.save(report=report)
    assert isinstance(row, DailyReportLaborCamp)
    assert row.contractor_ref_id == contractor.id
    assert row.subcontractor_name == 'Camp Co'


@pytest.mark.django_db
def test_labor_camp_rejects_unbound_subcontractor_name(project, user):
    report = DailyReport.objects.create(
        project=project,
        report_date=timezone.localdate(),
        created_by=user,
        updated_by=user,
    )
    ser = DailyReportLaborCampSerializer(
        data={
            'connex_number': 'C-2',
            'subcontractor_name': 'Ghost Camp Co',
            'total_residents': 4,
            'present_count': 2,
            'on_leave_count': 2,
            'capacity': 6,
        },
        context={'report': report, 'project_id': project.id},
    )
    assert not ser.is_valid()
    assert 'contractor_ref' in ser.errors

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

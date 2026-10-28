"""Tests for Feature 038: Discipline Sub-Reports Lifecycle and Validation."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

from common.reporting_units import SpecialtyUnit
from projects.models import Activity, Stakeholder
from risk.models import Inspection
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMaterial,
    SubReportStatus,
    SubcontractorLaborLedgerEntry,
)

User = get_user_model()
REPORT_DATE = date(2026, 10, 28)


@pytest.fixture
def contractor(db, project, user):
    return Stakeholder.objects.create(
        project=project,
        name='Test Plumbing Subcontractor',
        role='contractor',
        created_by=user,
    )


@pytest.fixture
def project_activity(db, activity, project, approved_measurement):
    activity.status = 'in_progress'
    activity.is_deleted = False
    activity.save()
    return activity


@pytest.fixture
def buildings_sub_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        sub_discipline='CIVIL',
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


@pytest.fixture
def mechanical_sub_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.MECHANICAL,
        discipline='mechanical',
        sub_discipline='PLUMBING',
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


# ---------------------------------------------------------------------------
# US1: Execution Percentage Validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestExecutionPercentage:
    def test_valid_execution_percentages_saved(self, auth_client, project, buildings_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/activities/'
        payload = {
            'shift': 'shift_1',
            'crew_name': 'Civil Crew 1',
            'foreman_count': 1,
            'worker_count': 4,
            'activity_ref': str(project_activity.id),
            'activity_description': 'Concrete pouring slab 1',
            'contractor_ref': str(contractor.id),
            'quantity': '25.0000',
            'unit': 'متر مکعب',
            'execution_percentage': '15.50',
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        row = DisciplineSubReportActivity.objects.get(id=res.data[0]['id'])
        assert row.execution_percentage == Decimal('15.50')

    def test_null_execution_percentage_allowed(self, auth_client, project, buildings_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/activities/'
        payload = {
            'shift': 'shift_1',
            'crew_name': 'Civil Crew 1',
            'activity_ref': str(project_activity.id),
            'activity_description': 'Preparation work',
            'contractor_ref': str(contractor.id),
            'execution_percentage': None,
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        row = DisciplineSubReportActivity.objects.get(id=res.data[0]['id'])
        assert row.execution_percentage is None

    def test_boundary_percentages_accepted(self, auth_client, project, buildings_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/activities/'
        for val in ['0.00', '100.00']:
            payload = {
                'shift': 'shift_1',
                'crew_name': 'Crew',
                'activity_ref': str(project_activity.id),
                'activity_description': f'Test {val}',
                'contractor_ref': str(contractor.id),
                'execution_percentage': val,
            }
            res = auth_client.post(url, payload, format='json')
            assert res.status_code == status.HTTP_201_CREATED

    def test_out_of_range_percentage_rejected(self, auth_client, project, buildings_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/activities/'
        for bad_val in ['-5.00', '105.00', '100.01']:
            payload = {
                'shift': 'shift_1',
                'crew_name': 'Crew',
                'activity_ref': str(project_activity.id),
                'activity_description': f'Bad {bad_val}',
                'contractor_ref': str(contractor.id),
                'execution_percentage': bad_val,
            }
            res = auth_client.post(url, payload, format='json')
            assert res.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
            res_str = str(res.data)
            assert 'percent_must_be_between_0_and_100' in res_str


# ---------------------------------------------------------------------------
# US2: Empty Sub-Report Submission Guard
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestEmptySubReportSubmission:
    def test_cannot_submit_empty_sub_report(self, auth_client, project, buildings_sub_report):
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/submit/'
        res = auth_client.post(url, format='json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        code = res.data.get('code') or (res.data.get('error', {}).get('code') if isinstance(res.data.get('error'), dict) else None)
        assert code == 'cannot_submit_empty_sub_report'
        buildings_sub_report.refresh_from_db()
        assert buildings_sub_report.status == SubReportStatus.DRAFT

    def test_submit_succeeds_with_at_least_one_row(self, auth_client, project, buildings_sub_report, project_activity, contractor):
        # Add an activity row
        DisciplineSubReportActivity.objects.create(
            sub_report=buildings_sub_report,
            row_number=1,
            shift='shift_1',
            crew_name='Crew 1',
            activity_ref=project_activity,
            activity_description='Work done',
            contractor_ref=contractor,
            quantity=Decimal('10.0'),
            unit='m',
        )
        url = f'/api/v1/projects/{project.id}/units/buildings/daily-reports/{buildings_sub_report.id}/submit/'
        res = auth_client.post(url, format='json')
        assert res.status_code == status.HTTP_200_OK
        buildings_sub_report.refresh_from_db()
        assert buildings_sub_report.status == SubReportStatus.SUBMITTED


# ---------------------------------------------------------------------------
# US4: Mechanical Materials Access
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMechanicalMaterials:
    def test_materials_endpoint_available_for_mechanical(self, auth_client, project, mechanical_sub_report):
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/materials/'
        payload = {
            'transaction_type': 'consumption',
            'material_description': 'لوله ۵ لایه',
            'quantity': '20.0000',
            'unit': 'متر طول',
            'consumption_location': 'Block A Floor 2',
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert DisciplineSubReportMaterial.objects.filter(sub_report=mechanical_sub_report).count() == 1


# ---------------------------------------------------------------------------
# US5: Hydrostatic Testing & QC Linkage
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestHydrostaticTesting:
    def test_hydrostatic_outcome_uses_canonical_values(self, auth_client, project, mechanical_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/activities/'
        payload = {
            'shift': 'shift_1',
            'crew_name': 'Plumbing Crew',
            'activity_ref': str(project_activity.id),
            'activity_description': 'Piping installation test line',
            'contractor_ref': str(contractor.id),
            'is_hydrostatic_tested': True,
            'test_pressure_bar': '6.50',
            'test_duration_minutes': 120,
            'test_outcome': 'PASSED',
            'tested_segment': 'Riser R-1',
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data[0]['test_outcome'] == 'PASSED'

        payload['test_outcome'] = 'pass'
        res = auth_client.post(url, payload, format='json')
        assert res.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_invalid_pressure_rejected(self, auth_client, project, mechanical_sub_report, project_activity, contractor):
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/activities/'
        payload = {
            'shift': 'shift_1',
            'crew_name': 'Plumbing Crew',
            'activity_ref': str(project_activity.id),
            'activity_description': 'Piping with bad pressure',
            'contractor_ref': str(contractor.id),
            'is_hydrostatic_tested': True,
            'test_pressure_bar': '-2.00',
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
        assert 'invalid_test_pressure_value' in str(res.data)

    def test_hydrostatic_test_passed_creates_qc_inspection_on_submit(
        self, auth_client, project, mechanical_sub_report, project_activity, contractor, user
    ):
        act = DisciplineSubReportActivity.objects.create(
            sub_report=mechanical_sub_report,
            row_number=1,
            shift='shift_1',
            crew_name='Plumbing Crew',
            activity_ref=project_activity,
            activity_description='Plumbing installation test line',
            contractor_ref=contractor,
            quantity=Decimal('30.0'),
            unit='m',
            is_hydrostatic_tested=True,
            test_pressure_bar=Decimal('6.50'),
            test_duration_minutes=120,
            test_outcome='PASSED',
            tested_segment='Riser R-1',
        )
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/submit/'
        res = auth_client.post(url, format='json')
        assert res.status_code == status.HTTP_200_OK
        act.refresh_from_db()
        assert act.qc_inspection is not None
        assert act.qc_inspection.project_id == project.id
        assert '6.50' in act.qc_inspection.description or 'Riser R-1' in act.qc_inspection.description


# ---------------------------------------------------------------------------
# US6: Subcontractor Crew Labor Hours Rollup
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSubcontractorLaborRollup:
    def test_direct_company_labor_can_omit_contractor_and_is_not_credited(
        self, auth_client, project, mechanical_sub_report, project_activity
    ):
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/activities/'
        payload = {
            'shift': 'shift_1',
            'crew_name': 'نفر شرکت',
            'activity_ref': str(project_activity.id),
            'activity_description': 'Company maintenance work',
            'contractor_ref': None,
            'foreman_count': 1,
            'worker_count': 2,
            'quantity': '1.0',
            'unit': 'عدد',
        }
        res = auth_client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data[0]['contractor_ref'] is None

    def test_labor_ledger_entry_generated_on_approval(
        self, auth_client, other_user, project, mechanical_sub_report, project_activity, contractor, user
    ):
        # Preparer creates row with 2 foremen and 6 workers, shift 8h
        act = DisciplineSubReportActivity.objects.create(
            sub_report=mechanical_sub_report,
            row_number=1,
            shift='shift_1',
            crew_name='Plumbing Crew',
            activity_ref=project_activity,
            activity_description='Plumbing installation',
            contractor_ref=contractor,
            foreman_count=2,
            worker_count=6,
            shift_hours=Decimal('8.00'),
            quantity=Decimal('50.0'),
            unit='m',
        )
        # Submit report
        url_submit = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/submit/'
        res_sub = auth_client.post(url_submit, format='json')
        assert res_sub.status_code == status.HTTP_200_OK

        # Approver (superuser or different role user) approves
        user.is_superuser = True
        user.save()
        url_approve = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{mechanical_sub_report.id}/approve/'
        res_app = auth_client.post(url_approve, format='json')
        assert res_app.status_code == status.HTTP_200_OK

        ledger_entry = SubcontractorLaborLedgerEntry.objects.filter(
            project=project,
            contractor=contractor,
            activity_row=act,
        ).first()
        assert ledger_entry is not None
        # (2 + 6) * 8 = 64 person-hours
        assert ledger_entry.total_person_hours == Decimal('64.00')
        assert ledger_entry.status == 'APPROVED'

        # Query endpoint
        url_ledger = f'/api/v1/projects/{project.id}/contractors/{contractor.id}/labor-ledger/'
        res_ledger = auth_client.get(url_ledger)
        assert res_ledger.status_code == status.HTTP_200_OK
        assert res_ledger.data['total_person_hours'] == '64.00'
        assert len(res_ledger.data['entries']) == 1
        assert res_ledger.data['entries'][0]['total_person_hours'] == '64.00'


# ---------------------------------------------------------------------------
# US7: Sub-Discipline Taxonomy Bridge
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSubDisciplineTaxonomy:
    def test_open_and_patch_sub_discipline(self, auth_client, project):
        url_open = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/open/'
        res_open = auth_client.post(
            url_open,
            {'report_date': '2026-10-28', 'sub_discipline': 'PLUMBING'},
            format='json',
        )
        assert res_open.status_code == status.HTTP_201_CREATED
        assert res_open.data['sub_discipline'] == 'PLUMBING'
        report_id = res_open.data['id']

        url_detail = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/{report_id}/'
        res_patch = auth_client.patch(url_detail, {'sub_discipline': 'HVAC'}, format='json')
        assert res_patch.status_code == status.HTTP_200_OK
        assert res_patch.data['sub_discipline'] == 'HVAC'

    def test_sub_discipline_is_scoped_to_canonical_unit(self, auth_client, project):
        url = f'/api/v1/projects/{project.id}/units/mechanical/daily-reports/open/'
        res = auth_client.post(
            url,
            {'report_date': '2026-10-29', 'sub_discipline': 'CIVIL'},
            format='json',
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


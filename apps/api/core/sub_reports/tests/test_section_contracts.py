"""Section contracts on the canonical unit-report surface (feature 033).

US1 executed-activity contract (tasks T012), per
contracts/unit-report-sections-api.md §1. Sections for later stories
(US2–US7, tasks T019–T049) arrive with their phases.
"""
from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
import pytest

from projects.models import Activity, Project, Stakeholder, WBS
from sub_reports.models import DisciplineSubReport, SubReportStatus
from common.reporting_units import SpecialtyUnit
from sub_reports.serializers import (
    UnitReportActivitySectionSerializer,
)
from sub_reports.services.section_validation import (
    validate_activity_rows,
    SectionContractError,
)

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def unit_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        lineage_id=None,
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


@pytest.fixture
def contractor(db, project, user):
    stakeholder = Stakeholder.objects.create(
        project=project,
        name='Test Contractor Co',
        role='contractor',
        created_by=user,
    )
    stakeholder.refresh_from_db()
    return stakeholder


@pytest.fixture
def project_activity(db, activity, project):
    activity.status = 'in_progress'
    activity.is_deleted = False
    activity.save()
    return activity


@pytest.fixture
def foreign_project(db, user):
    other = Project.objects.create(
        project_code='PRJ-001-F',
        project_name='Other Project',
        employer='Employer Co',
    )
    node = WBS.add_root(project=other, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(
        project=other,
        wbs=node,
        activity_code='X1',
        activity_name='Foreign activity',
        status='in_progress',
        created_by=user,
    )
    stakeholder = Stakeholder.objects.create(
        project=other,
        name='Foreign Contractor Co',
        role='contractor',
        created_by=user,
    )
    return {'project': other, 'wbs': node, 'activity': activity, 'stakeholder': stakeholder}


@pytest.fixture
def section_activity_payload(project_activity, contractor):
    return {
        'row_number': 1,
        'shift': 'shift_1',
        'activity_ref': str(project_activity.id),
        'activity_description': 'Wall works',
        'contractor_ref': str(contractor.id),
        'crew_name': 'Crew A',
        'foreman_count': 2,
        'worker_count': 3,
        'parcel': 'P4',
        'zone': 'Z1',
        'block': 'B2',
        'floor': 'F3',
        'quantity': '12.5',
        'unit': 'm3',
    }


def _save_rows(report, rows):
    """Save section rows through the section-validation service + serializer path."""
    return validate_activity_rows(report, rows, context={})


# ---------------------------------------------------------------------------
# §1: executed activities (Buildings / Electrical / Mechanical)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestActivitySectionContract:
    def test_valid_complete_row_saves_and_maintains_headcount(
        self, db, unit_report, section_activity_payload,
    ):
        rows = _save_rows(unit_report, [section_activity_payload])
        assert len(rows) == 1
        row = rows[0]
        # headcount maintained as foreman_count + worker_count (T014)
        assert row.headcount == 5
        assert row.foreman_count == 2
        assert row.worker_count == 3
        assert row.contractor_ref_id
        assert row.activity_ref_id

    @pytest.mark.parametrize('quantity', ['0', '-12.5'])
    def test_quantity_must_be_positive(
        self, db, unit_report, section_activity_payload, quantity,
    ):
        section_activity_payload['quantity'] = quantity
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('quantity') == ['quantity_must_be_positive']

    def test_invalid_shift_not_silently_remapped(
        self, db, unit_report, section_activity_payload,
    ):
        section_activity_payload['shift'] = 'برانکارد'  # unrecognized free text
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('shift') == ['invalid_shift']

    def test_foreign_project_activity_refused(
        self, db, unit_report, section_activity_payload, foreign_project,
    ):
        section_activity_payload['activity_ref'] = str(foreign_project['activity'].id)
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('activity_ref') == ['activity_not_in_project_scope']

    def test_inactive_or_unapproved_activity_refused(
        self, db, unit_report, section_activity_payload, project_activity,
    ):
        project_activity.status = 'suspended'
        project_activity.save(update_fields=['status'])
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('activity_ref') == ['activity_not_in_project_scope']

    def test_foreign_project_contractor_refused(
        self, db, unit_report, section_activity_payload, foreign_project,
    ):
        section_activity_payload['contractor_ref'] = str(foreign_project['stakeholder'].id)
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('contractor_ref') == [
            'contractor_not_in_project_scope',
        ]

    def test_contractor_required(self, db, unit_report, section_activity_payload):
        section_activity_payload.pop('contractor_ref')
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('contractor_ref') == ['contractor_required']

    def test_crew_name_and_contractor_survive_as_separate_columns(
        self, db, unit_report, section_activity_payload, contractor,
    ):
        rows = _save_rows(unit_report, [section_activity_payload])
        data = UnitReportActivitySectionSerializer(rows[0]).data
        # No merged paint-by-name column: crew and contractor are distinct fields.
        assert 'crew_name' in data
        assert 'contractor_ref' in data
        assert data['crew_name'] == 'Crew A'
        assert data['contractor_ref'] == str(contractor.id)

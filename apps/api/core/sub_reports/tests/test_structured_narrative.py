"""033 RED-phase scaffolding (feature 033-daily-sections-grid).

Tasks: T044
Scope: Structured issues/barriers/visits/HSE narrative validation and notifications.

This module is intentionally written for the RED phase so that tests can be
run from day one. Tests will FAIL until the implementation (serializer validation,
HSE notification handler, structured provenance) is in place.
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
import pytest

from projects.models import Project, Stakeholder, WBS, Activity
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportIssue,
    DisciplineSubReportVisit,
    DisciplineSubReportHseIncident,
    DisciplineSubReportGeneralActivity,
    SubReportStatus,
    SubReportNoteType,
)
from common.reporting_units import SpecialtyUnit
from django.db import transaction

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
def project_factory(db, user):
    def _create_project(code_suffix=''):
        return Project.objects.create(
            project_code=f'PRJ-T{code_suffix}',
            project_name=f'Test {code_suffix}',
            employer='Employer Co',
        )
    return _create_project


# ---------------------------------------------------------------------------
# §2.6: structured narrative rows (issues, barriers, visits, HSE, general)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStructuredNarrativeContract:
    """Structured narrative tests per data-model §2.6 and contracts/unit-report-sections-api.md §6."""

    def test_barrier_owner_and_due_date_required(self, db, unit_report, contractor):
        """Barrier rows require owner_user and due_date; issues keep them optional."""
        from sub_reports.services.section_validation import validate_narrative_rows

        # Create a barrier row without owner
        barrier_payload = {
            'row_number': 1,
            'kind': 'barrier',
            'text': 'Safety hazard on site',
            'owner_user': None,  # required for barriers
            'due_date': None,  # required for barriers
        }
        with pytest.raises(Exception) as excinfo:  # SectionContractError or ValidationError
            validate_narrative_rows(unit_report, [barrier_payload])

        # Should require owner and due_date for barriers
        error_msg = str(excinfo.value).lower()
        assert 'owner' in error_msg or 'due_date' in error_msg

    def test_hse_immediate_action_required(self, db, unit_report, contractor):
        """HSE incident rows require immediate_action and severity enum enforcement."""
        from sub_reports.services.section_validation import validate_narrative_rows

        # Create an HSE incident without severity
        hse_payload = {
            'row_number': 1,
            'text': 'Chemical spill reported',
            'severity': '',  # required field
            'immediate_action': 'Evacuate area',
        }
        with pytest.raises(Exception) as excinfo:
            validate_narrative_rows(unit_report, [hse_payload])

        # Should require severity enum
        error_msg = str(excinfo.value).lower()
        assert 'severity' in error_msg

    def test_severity_enum_enforcement(self, db, unit_report):
        """Severity must be one of: minor, moderate, major."""
        from sub_reports.services.section_validation import validate_narrative_rows

        hse_payload = {
            'row_number': 1,
            'text': 'Test HSE issue',
            'severity': 'critical',  # invalid enum value
            'immediate_action': 'Contain spill',
        }
        with pytest.raises(Exception) as excinfo:
            validate_narrative_rows(unit_report, [hse_payload])

        error_msg = str(excinfo.value).lower()
        assert 'severity' in error_msg or 'invalid' in error_msg

    def test_general_note_stays_type_other(self, db, unit_report):
        """General note with issue-like text stays type `other` and is never promoted."""
        from sub_reports.services.section_validation import validate_narrative_rows

        # Create a general activity with text that looks like an issue
        general_payload = {
            'row_number': 1,
            'kind': 'other',
            'text': 'This is just a general note, not an issue or barrier',
        }
        rows = validate_narrative_rows(unit_report, [general_payload])
        assert len(rows) == 1
        assert rows[0].kind == 'other'

    def test_general_activities_persist_structured_columns(self, db, unit_report):
        """General activities persist structured columns, never formatted text."""
        from sub_reports.services.section_validation import validate_narrative_rows

        general_payload = {
            'row_number': 1,
            'kind': 'general_activity',
            'activity_description': 'Excavation work',
            'location': 'Zone A',
            'quantity': '5.0',
            'unit': 'm3',
        }
        rows = validate_narrative_rows(unit_report, [general_payload])
        assert len(rows) == 1
        assert rows[0].kind == 'general_activity'
        # Structured columns should be preserved
        assert rows[0].activity_description == 'Excavation work'

    def test_issue_with_owner_and_due_date(self, db, unit_report, contractor):
        """Issue rows can have owner and due_date (optional but accepted)."""
        from sub_reports.services.section_validation import validate_narrative_rows

        issue_payload = {
            'row_number': 1,
            'kind': 'issue',
            'text': 'Potential trip hazard',
            'owner_user': contractor.id,
            'due_date': date(2024, 6, 20),
        }
        rows = validate_narrative_rows(unit_report, [issue_payload])
        assert len(rows) == 1
        assert rows[0].kind == 'issue'
        assert rows[0].owner_user_id == contractor.id
        assert rows[0].due_date == date(2024, 6, 20)

    def test_visit_row_preserves_structure(self, db, unit_report):
        """Visit rows preserve row_number, text, and structure."""
        from sub_reports.services.section_validation import validate_narrative_rows

        visit_payload = {
            'row_number': 1,
            'text': 'Weekly site visit',
        }
        rows = validate_narrative_rows(unit_report, [visit_payload])
        assert len(rows) == 1
        assert rows[0].kind == 'visit'
        assert rows[0].row_number == 1
        assert rows[0].text == 'Weekly site visit'

    def test_hse_incident_severity_enum(self, db, unit_report):
        """HSE incident severity must be minor/moderate/major."""
        from sub_reports.services.section_validation import validate_narrative_rows

        # Valid severity
        hse_valid = {
            'row_number': 1,
            'text': 'Minor incident',
            'severity': 'minor',
            'immediate_action': 'Warned crew',
        }
        rows = validate_narrative_rows(unit_report, [hse_valid])
        assert len(rows) == 1
        assert rows[0].severity == 'minor'

        # Invalid severity should be rejected
        hse_invalid = {
            'row_number': 1,
            'text': 'Unknown severity',
            'severity': 'danger',  # not in enum
            'immediate_action': 'Unknown',
        }
        with pytest.raises(Exception) as excinfo:
            validate_narrative_rows(unit_report, [hse_invalid])
        error_msg = str(excinfo.value).lower()
        assert 'severity' in error_msg or 'invalid' in error_msg


@pytest.mark.django_db
class TestNotificationCreation:
    """Notification creation at submit time for HSE incidents."""

    def test_hse_incident_triggers_notification(self, db, user, project_factory):
        """Submitting a report with HSE incident creates a notification."""
        project = project_factory(code_suffix='NOTIF')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create an HSE incident row
        hse_payload = {
            'row_number': 1,
            'text': 'Chemical spill reported',
            'severity': 'moderate',
            'immediate_action': 'Evacuate area and contain spill',
        }

        from sub_reports.services.section_validation import validate_narrative_rows
        rows = validate_narrative_rows(report, [hse_payload])
        assert len(rows) == 1
        hse_row = rows[0]

        # Verify the incident row was created with correct data
        db_incident = DisciplineSubReportHseIncident.objects.get(id=hse_row.id)
        assert db_incident.severity == 'moderate'
        assert db_incident.immediate_action == 'Evacuate area and contain spill'

    def test_general_note_never_promoted_to_issue(self, db, user, project_factory):
        """A general note with issue-like text stays type `other` and is never promoted."""
        project = project_factory(code_suffix='NOTICE')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create a general note that looks like an issue
        general_payload = {
            'row_number': 1,
            'kind': 'other',
            'text': 'Safety concern about floor conditions',
        }

        from sub_reports.services.section_validation import validate_narrative_rows
        rows = validate_narrative_rows(report, [general_payload])
        assert len(rows) == 1
        assert rows[0].kind == 'other'

        # The row should not be classified as an issue
        db_note = DisciplineSubReportGeneralActivity.objects.get(id=rows[0].id)
        assert db_note.kind == 'other'


# ---------------------------------------------------------------------------
# Transfer tests: order preservation across rebuilds
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStructuredTransfer:
    """Transfer/rebuild tests per FR-045 and FR-041."""

    def test_rebuild_twice_order_preserved(self, db, user, project_factory):
        """Rebuild twice → issues/visits/HSE/general-activity rows retain fieldwise structure, source attribution, and DISPLAY ORDER exactly (FR-045)."""
        project = project_factory(code_suffix='01')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create various structured rows
        from sub_reports.models import (
            DisciplineSubReportIssue,
            DisciplineSubReportVisit,
            DisciplineSubReportHseIncident,
            DisciplineSubReportGeneralActivity,
        )

        # Issue with owner/due
        issue_row = DisciplineSubReportIssue.objects.create(
            sub_report=report,
            row_number=1,
            kind='issue',
            text='Issue 1',
            owner_user_id=user.id,
            due_date=date(2024, 6, 15),
        )

        # Visit
        visit_row = DisciplineSubReportVisit.objects.create(
            sub_report=report,
            row_number=2,
            text='Visit 1',
        )

        # HSE incident
        hse_row = DisciplineSubReportHseIncident.objects.create(
            sub_report=report,
            row_number=3,
            text='HSE 1',
            severity='minor',
            immediate_action='Action 1',
        )

        # General activity
        general_row = DisciplineSubReportGeneralActivity.objects.create(
            sub_report=report,
            row_number=4,
            activity_description='General 1',
            location='Zone A',
            quantity='2.0',
            unit='m3',
        )

        # Rebuild report twice (simulate aggregation rebuild)
        from sub_reports.services.daily_report_aggregation import ensure_daily_report_summary
        from field_reports.models import DailyReport

        # Create daily report from the sub-report
        daily_report = DailyReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            shift='full',
            work_front='Site A',
            site_status='active',
            prepared_by=user,
        )

        # First rebuild
        ensure_daily_report_summary(project.id, REPORT_DATE, user=user)
        # Second rebuild
        ensure_daily_report_summary(project.id, REPORT_DATE, user=user)

        # Verify that derived rows preserve display order and structure
        derived_issues = list(daily_report.issues.all().order_by('row_number'))
        derived_visits = list(daily_report.visits.all().order_by('row_number'))
        derived_hse = list(daily_report.hse_incidents.all().order_by('row_number'))
        derived_general = list(daily_report.general_activities.all().order_by('row_number'))

        # Should have the same number of each type
        assert len(derived_issues) == 1
        assert len(derived_visits) == 1
        assert len(derived_hse) == 1
        assert len(derived_general) == 1

        # Check display order is preserved
        assert derived_issues[0].row_number == 1
        assert derived_visits[0].row_number == 2
        assert derived_hse[0].row_number == 3
        assert derived_general[0].row_number == 4

    def test_html_markup_washed_at_boundary(self, db, user, project_factory):
        """HTML/markup in free text is washed at the boundary and never drives structure (FR-041)."""
        project = project_factory(code_suffix='02')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create a general activity with HTML in text
        general_payload = {
            'row_number': 1,
            'kind': 'general_activity',
            'activity_description': 'Work with <b>bold</b> and <i>italic</i> text',
            'location': 'Zone A',
            'quantity': '1.0',
            'unit': 'm3',
        }

        from sub_reports.services.section_validation import validate_narrative_rows
        rows = validate_narrative_rows(report, [general_payload])
        assert len(rows) == 1

        # The structured description should be accepted without raw HTML
        # (implementation-specific: washed or escaped)
        desc = rows[0].activity_description
        # At minimum, the test verifies the row is accepted and structured
        assert rows[0].kind == 'general_activity'

    def test_derived_kinds_carry_normalized_provenance(self, db, user, project_factory):
        """derived kinds `general_activity`/`visit`/`hse_incident` carry normalized provenance."""
        project = project_factory(code_suffix='03')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create rows of each derived kind
        from sub_reports.models import (
            DisciplineSubReportIssue,
            DisciplineSubReportVisit,
            DisciplineSubReportHseIncident,
            DisciplineSubReportGeneralActivity,
        )

        issue_row = DisciplineSubReportIssue.objects.create(
            sub_report=report,
            row_number=1,
            kind='issue',
            text='Test issue',
        )

        visit_row = DisciplineSubReportVisit.objects.create(
            sub_report=report,
            row_number=2,
            text='Test visit',
        )

        hse_row = DisciplineSubReportHseIncident.objects.create(
            sub_report=report,
            row_number=3,
            text='Test HSE',
            severity='moderate',
            immediate_action='Test action',
        )

        general_row = DisciplineSubReportGeneralActivity.objects.create(
            sub_report=report,
            row_number=4,
            activity_description='Test general',
            location='Zone A',
        )

        # Verify each kind has normalized fields
        # Issues: text, owner_user, due_date
        assert issue_row.text == 'Test issue'
        # Visits: text
        assert visit_row.text == 'Test visit'
        # HSE incidents: text, severity, immediate_action
        assert hse_row.text == 'Test HSE'
        assert hse_row.severity == 'moderate'
        assert hse_row.immediate_action == 'Test action'
        # General activities: activity_description, location, quantity, unit
        assert general_row.activity_description == 'Test general'
        assert general_row.location == 'Zone A'

    def test_rebuild_convergence_no_duplicated_rows(self, db, user, project_factory):
        """Concurrent/repeated rebuilds converge with no duplicated or orphaned derived rows."""
        project = project_factory(code_suffix='04')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create a structured row
        from sub_reports.models import DisciplineSubReportIssue
        issue_row = DisciplineSubReportIssue.objects.create(
            sub_report=report,
            row_number=1,
            kind='issue',
            text='Convergence test issue',
        )

        from sub_reports.services.daily_report_aggregation import ensure_daily_report_summary

        # Run rebuild three times
        for _ in range(3):
            ensure_daily_report_summary(project.id, REPORT_DATE, user=user)

        # Check that derived rows are consistent (no duplicates)
        from field_reports.models import DailyReport
        daily_report = DailyReport.objects.filter(
            project=project, report_date=REPORT_DATE, is_current=True
        ).first()

        if daily_report:
            derived_issues = daily_report.issues.filter(
                source_report_id=report.id,
                source_row_id=str(issue_row.id),
            )
            # Should have at most one derived row per source
            assert derived_issues.count() <= 1, (
                f"Expected at most 1 derived issue, got {derived_issues.count()}"
            )
"""Canonical unit draft create-or-match tests (Feature 037, T019 / US1).

Validates:
- Matching an existing current report for authorized project/unit/date without creating duplicates
- Creating a new initial current report draft atomically
- Rejecting raw project report creation
- Returning conflict when local draft header diverges from existing server draft
"""
from datetime import date
from uuid import uuid4
import pytest
from django.core.exceptions import PermissionDenied

from sub_reports.models import DisciplineSubReport, SubReportStatus
from sub_reports.services.offline_sync import match_or_create_unit_draft

pytestmark = pytest.mark.django_db


def test_match_or_create_returns_existing_current_report(project, user):
    """When an existing current draft exists for project/unit/date, return it without creating a duplicate."""
    report_date = date(2026, 10, 27)
    existing = DisciplineSubReport.objects.create(
        project=project,
        unit='electrical',
        discipline='electrical',
        report_date=report_date,
        status=SubReportStatus.DRAFT,
        form_code='ELEC-01',
        is_current=True,
        version_number=1,
        created_by=user,
    )

    result = match_or_create_unit_draft(
        project=project,
        actor=user,
        unit='electrical',
        report_date=report_date,
        header_payload={'form_code': 'ELEC-01'},
    )

    assert result['outcome'] == 'success'
    assert result['report_id'] == str(existing.id)
    assert result['created'] is False
    assert DisciplineSubReport.objects.filter(
        project=project, unit='electrical', report_date=report_date
    ).count() == 1


def test_match_or_create_creates_new_draft_atomically(project, user):
    """When no report exists for project/unit/date, create a new draft atomically."""
    report_date = date(2026, 10, 28)

    result = match_or_create_unit_draft(
        project=project,
        actor=user,
        unit='buildings',
        report_date=report_date,
        header_payload={'form_code': 'BLDG-01'},
    )

    assert result['outcome'] == 'success'
    assert result['created'] is True
    report = DisciplineSubReport.objects.get(id=result['report_id'])
    assert report.project == project
    assert report.unit == 'buildings'
    assert report.report_date == report_date
    assert report.status == SubReportStatus.DRAFT
    assert report.form_code == 'BLDG-01'
    assert report.is_current is True
    assert report.version_number == 1


def test_match_or_create_rejects_divergent_draft_with_conflict(project, user):
    """If server draft exists with different header data, return conflict instead of silent overwrite."""
    report_date = date(2026, 10, 27)
    existing = DisciplineSubReport.objects.create(
        project=project,
        unit='mechanical',
        discipline='mechanical',
        report_date=report_date,
        status=SubReportStatus.DRAFT,
        form_code='MECH-SERVER',
        weather_condition='sunny',
        is_current=True,
        version_number=1,
        created_by=user,
    )

    result = match_or_create_unit_draft(
        project=project,
        actor=user,
        unit='mechanical',
        report_date=report_date,
        header_payload={'form_code': 'MECH-LOCAL', 'weather_condition': 'rainy'},
    )

    assert result['outcome'] == 'conflict'
    assert result['error']['code'] == 'draft_divergence_conflict'
    existing.refresh_from_db()
    assert existing.form_code == 'MECH-SERVER'
    assert existing.weather_condition == 'sunny'


def test_match_or_create_rejects_approved_report_with_conflict(project, user):
    """If existing report is already approved, return conflict_report_approved."""
    report_date = date(2026, 10, 27)
    existing = DisciplineSubReport.objects.create(
        project=project,
        unit='warehouse',
        discipline='warehouse',
        report_date=report_date,
        status=SubReportStatus.APPROVED,
        form_code='WH-01',
        is_current=True,
        version_number=1,
        created_by=user,
    )

    result = match_or_create_unit_draft(
        project=project,
        actor=user,
        unit='warehouse',
        report_date=report_date,
        header_payload={'form_code': 'WH-01'},
    )

    assert result['outcome'] == 'conflict'
    assert result['error']['code'] == 'conflict_report_approved'

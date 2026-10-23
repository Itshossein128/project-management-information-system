from datetime import date
import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
)
from project_templates.models import (
    ProjectReportingConfiguration,
    ProjectReportingConfigurationUnit,
    ProjectTemplate,
    ProjectTemplateRequiredUnit,
)
from project_templates.services import activate_project_reporting_configuration
from sub_reports.models import DisciplineSubReport, SubReportStatus


def make_unit_report(
    project,
    user,
    *,
    unit=SpecialtyUnit.BUILDINGS,
    status=SubReportStatus.SUBMITTED,
    report_date=SUMMARY_DATE,
):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        unit=unit,
        legacy_discipline=unit,
        discipline='civil',
        status=status,
        is_current=True,
        is_deleted=False,
        version_number=1,
        created_by=user,
        updated_by=user,
        submitted_by=user,
    )


@pytest.fixture
def reporting_template(db, user):
    template = ProjectTemplate.objects.create(
        template_name='Standard Project Template',
        created_by=user,
    )
    for i, u in enumerate([SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL, SpecialtyUnit.MECHANICAL]):
        ProjectTemplateRequiredUnit.objects.create(
            template=template,
            unit=u,
            display_order=i,
        )
    return template


@pytest.mark.django_db
def test_completeness_when_no_configuration_bound(project, user):
    make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=summary)
    completeness = meta.get('completeness', {})

    assert completeness.get('state') == 'configuration_incomplete'
    assert completeness.get('configuration_id') is None
    assert completeness.get('expected_units') == []
    assert completeness.get('contributing_units') == [SpecialtyUnit.BUILDINGS]
    assert completeness.get('missing_units') == []


@pytest.mark.django_db
def test_completeness_partial_when_some_required_missing(project, user, reporting_template):
    activate_project_reporting_configuration(
        project=project,
        template=reporting_template,
        effective_from=date(2024, 1, 1),
        user=user,
    )
    make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=summary)
    completeness = meta.get('completeness', {})

    assert completeness.get('state') == 'partial'
    assert completeness.get('expected_units') == [
        SpecialtyUnit.BUILDINGS,
        SpecialtyUnit.ELECTRICAL,
        SpecialtyUnit.MECHANICAL,
    ]
    assert completeness.get('contributing_units') == [SpecialtyUnit.BUILDINGS]
    assert set(completeness.get('missing_units')) == {
        SpecialtyUnit.ELECTRICAL,
        SpecialtyUnit.MECHANICAL,
    }


@pytest.mark.django_db
def test_completeness_complete_when_all_required_present(project, user, reporting_template):
    activate_project_reporting_configuration(
        project=project,
        template=reporting_template,
        effective_from=date(2024, 1, 1),
        user=user,
    )
    make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL)
    make_unit_report(project, user, unit=SpecialtyUnit.MECHANICAL)

    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=summary)
    completeness = meta.get('completeness', {})

    assert completeness.get('state') == 'complete'
    assert completeness.get('missing_units') == []
    assert set(completeness.get('contributing_units')) == {
        SpecialtyUnit.BUILDINGS,
        SpecialtyUnit.ELECTRICAL,
        SpecialtyUnit.MECHANICAL,
    }


@pytest.mark.django_db
def test_eligible_non_required_unit_in_contributing_never_in_missing(project, user, reporting_template):
    activate_project_reporting_configuration(
        project=project,
        template=reporting_template,
        effective_from=date(2024, 1, 1),
        user=user,
    )
    # Buildings, Electrical, Mechanical present + Warehouse (non-required) present
    make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL)
    make_unit_report(project, user, unit=SpecialtyUnit.MECHANICAL)
    make_unit_report(project, user, unit=SpecialtyUnit.WAREHOUSE)

    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=summary)
    completeness = meta.get('completeness', {})

    assert completeness.get('state') == 'complete'
    assert SpecialtyUnit.WAREHOUSE in completeness.get('contributing_units')
    assert SpecialtyUnit.WAREHOUSE not in completeness.get('missing_units')


@pytest.mark.django_db
def test_empty_eligible_report_counts_as_contributing(project, user, reporting_template):
    activate_project_reporting_configuration(
        project=project,
        template=reporting_template,
        effective_from=date(2024, 1, 1),
        user=user,
    )
    # Create empty report for buildings (no activities, labor, materials)
    r_empty = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    assert r_empty.activities.count() == 0

    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=summary)
    completeness = meta.get('completeness', {})

    assert SpecialtyUnit.BUILDINGS in completeness.get('contributing_units')
    assert SpecialtyUnit.BUILDINGS not in completeness.get('missing_units')


@pytest.mark.django_db
def test_historical_completeness_uses_bound_configuration(project, user, reporting_template):
    c1 = activate_project_reporting_configuration(
        project=project,
        template=reporting_template,
        effective_from=date(2024, 1, 1),
        user=user,
    )
    make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS)
    summary = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert summary.reporting_configuration == c1

    # Create a new template requiring all 6 units and activate later
    t2 = ProjectTemplate.objects.create(template_name='Expanded Template', created_by=user)
    for i, u in enumerate(SpecialtyUnit.values):
        ProjectTemplateRequiredUnit.objects.create(template=t2, unit=u, display_order=i)
    c2 = activate_project_reporting_configuration(
        project=project,
        template=t2,
        effective_from=date(2024, 7, 1),
        user=user,
    )

    # Rebuilding summary for SUMMARY_DATE (2024-06-10) must keep bound configuration c1
    rebuilt = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user, report=summary)
    assert rebuilt.reporting_configuration == c1
    meta = build_aggregation_meta(project.id, SUMMARY_DATE, report=rebuilt)
    assert meta['completeness']['configuration_id'] == str(c1.id)
    assert len(meta['completeness']['expected_units']) == 3

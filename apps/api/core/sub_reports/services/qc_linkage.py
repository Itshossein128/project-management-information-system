"""Sampling declaration → existing ``risk.Inspection`` store (feature 033, T041).

Does not create a parallel QC table. Linkage is idempotent: a row that already
points at a same-project inspection is left untouched on resubmit.
"""
from __future__ import annotations

from django.utils import timezone

from risk.models import Inspection, InspectionStage
from sub_reports.models import SamplingState
from sub_reports.services.section_validation import (
    SAMPLING_REQUIRES_TEST_INFORMATION,
    SectionContractError,
)


def _project_wbs(project):
    from projects.models import WBS

    existing = WBS.objects.filter(project_id=project.id).order_by('id').first()
    if existing is not None:
        return existing
    return WBS.add_root(
        project=project,
        wbs_code='QC',
        wbs_name='Quality inspections',
    )


def assert_sampling_ready(report):
    """Block submit when a declared sample lacks test information."""
    incomplete = report.concrete_entries.filter(
        is_deleted=False,
        sampling_state=SamplingState.SAMPLING_DECLARED,
    )
    for row in incomplete:
        if not (row.lab_sample_code or '').strip() or row.test_sheet_count is None:
            raise SectionContractError(
                code=SAMPLING_REQUIRES_TEST_INFORMATION,
                message='Declared sampling requires a lab sample code and test sheet count',
            )


def link_declared_concrete_sampling(report, user):
    """Create or reuse a project Inspection for each declared pour."""
    assert_sampling_ready(report)
    if user is None:
        user = report.created_by
    if user is None:
        return []
    linked = []
    for row in report.concrete_entries.filter(
        is_deleted=False,
        sampling_state=SamplingState.SAMPLING_DECLARED,
    ).order_by('id'):
        if row.qc_inspection_id and str(row.qc_inspection.project_id) == str(report.project_id):
            linked.append(row)
            continue
        inspection = Inspection.objects.create(
            project_id=report.project_id,
            wbs=_project_wbs(report.project),
            responsible_user=user,
            inspection_date=report.report_date or timezone.now().date(),
            stage=InspectionStage.RESULT,
            description=(
                f'Concrete sample {row.lab_sample_code} '
                f'({row.concrete_description})'
            )[:1000],
            created_by=user,
            updated_by=user,
        )
        row.qc_inspection = inspection
        row.save(update_fields=['qc_inspection'])
        linked.append(row)
    return linked


def link_hydrostatic_tests(report, user):
    """Create or reuse a project Inspection for each passed hydrostatic test on activities (feature 038, US5)."""
    if user is None:
        user = report.created_by
    if user is None:
        return []
    linked = []
    for row in report.activities.filter(
        is_deleted=False,
        is_hydrostatic_tested=True,
        test_outcome='PASSED',
    ).order_by('id'):
        if row.qc_inspection_id and str(row.qc_inspection.project_id) == str(report.project_id):
            linked.append(row)
            continue
        segment_desc = f" ({row.tested_segment})" if row.tested_segment else ""
        pressure_desc = f"{row.test_pressure_bar} Bar" if row.test_pressure_bar else "N/A"
        duration_desc = f", duration: {row.test_duration_minutes} min" if row.test_duration_minutes else ""
        inspection = Inspection.objects.create(
            project_id=report.project_id,
            wbs=_project_wbs(report.project),
            responsible_user=user,
            inspection_date=report.report_date or timezone.now().date(),
            stage=InspectionStage.RESULT,
            description=(
                f'Hydrostatic test PASSED: {pressure_desc}{duration_desc}{segment_desc} '
                f'[{row.activity_description}]'
            )[:1000],
            created_by=user,
            updated_by=user,
        )
        row.qc_inspection = inspection
        row.save(update_fields=['qc_inspection'])
        linked.append(row)
    return linked


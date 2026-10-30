"""Snapshot comparison must not mutate the stored, possibly approved report."""
from datetime import date

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport, ReportStatus
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    rebuild_daily_report_summary,
)
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus


@pytest.mark.django_db
def test_snapshot_source_comparison_detects_edit_and_preserves_approved_snapshot(project, user):
    day = date(2024, 6, 10)
    source = DisciplineSubReport.objects.create(
        project=project, report_date=day, unit=SpecialtyUnit.BUILDINGS,
        discipline='civil', status=SubReportStatus.SUBMITTED, created_by=user, updated_by=user,
    )
    row = DisciplineSubReportActivity.objects.create(
        sub_report=source, row_number=1, shift='shift_1', crew_name='Crew',
        activity_description='Original', quantity=5, unit='m2',
    )
    snapshot = rebuild_daily_report_summary(project.id, day, user=user)
    assert build_aggregation_meta(project.id, day, snapshot)['snapshot_source_comparison'] == 'matching_fingerprint'
    snapshot.status = ReportStatus.APPROVED
    snapshot.save(update_fields=['status'])
    before = (snapshot.aggregation_fingerprint, snapshot.aggregated_at, list(snapshot.activities.values_list('activity_description', flat=True)))
    row.activity_description = 'Changed'
    row.save(update_fields=['activity_description'])
    meta = build_aggregation_meta(project.id, day, snapshot)
    assert meta['snapshot_source_comparison'] == 'changed'
    snapshot.refresh_from_db()
    assert snapshot.status == ReportStatus.APPROVED
    assert (snapshot.aggregation_fingerprint, snapshot.aggregated_at, list(snapshot.activities.values_list('activity_description', flat=True))) == before


@pytest.mark.django_db
def test_snapshot_source_comparison_unknown_without_stored_fingerprint(project, user):
    day = date(2024, 6, 10)
    report = DailyReport.objects.create(project=project, report_date=day, shift='full', is_auto_summary=True, created_by=user)
    assert build_aggregation_meta(project.id, day, report)['snapshot_source_comparison'] == 'unknown'
    assert build_aggregation_meta(project.id, day)['snapshot_source_comparison'] == 'unknown'
